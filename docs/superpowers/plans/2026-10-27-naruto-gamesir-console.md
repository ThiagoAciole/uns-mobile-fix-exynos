# Plano de implementação — Naruto Storm e GameSir

**Objetivo:** entregar um APK assinado para Galaxy S24 com Exynos, widescreen, pt-BR, GameSir, HUD adaptativo, prompts ABXY corretos e configuração de controle persistente.

**Arquitetura:** preservar a base S24 já aceita, o caminho de controles táteis e o mapeamento Paddleboat funcional. Investigar os pontos nativos antes de definir hooks; reutilizar recursos e editor existentes somente quando seus contratos forem demonstrados. Validar cada componente isoladamente antes de compor o APK final.

**Tecnologia:** Python, patches AArch64, Ghidra headless 12.2, ferramentas Android de assinatura e ADB. **Referências:** `docs/PRD.md`, `docs/ARCHITECTURE.md`, `docs/CONTROLLER_S24_VALIDATION_20261027.md` e `docs/CONTROLLER_CONSOLE_UI_INVESTIGATION_20261027.md`.

## Limites e evidências

- Alvo de aceite: SM-S921B, 2340×1080, GameSir-X5 Lite; não extrapolar para outros aparelhos.
- Preserve APKs, progresso, chave de assinatura, capturas e arquivos em `work/`. Não desinstalar nem limpar dados. Instalar apenas com `adb install --no-incremental -r --user 0`.
- O arquivo final padrão em `build/` só pode ser substituído após confirmação explícita. Candidatos temporários seguem as regras de `AGENTS.md` e não substituem o APK aceito.
- Estado documentado: Exynos, widescreen e controle têm evidência anterior no S24; HUD candidato e prompts Y/B foram verificados estaticamente/host, não no aparelho. O editor e prompts dinâmicos não estão implementados.
- Presença do atlas ABXY, vtable e textos não comprova roteamento, UV, leitura real dos bindings ou execução. Não confundir evidência estática com aceite visual.
- Há registro de uma falha inicial de superfície Vulkan; observar recorrência e preservar logs, sem atribuir causa sem evidência.

## 1. Preparação e referência

**Arquivos:** `docs/CONTROLLER_S24_VALIDATION_20261027.md`, `scripts/build-selective.py`, `docs/CONTROLLER_CONSOLE_UI_INVESTIGATION_20261027.md`.

- [ ] Conferir hash do APK base S24, biblioteca exigida pelo orquestrador, identidade do pacote, versão e certificado, sem expor credenciais; verificar compatibilidade de assinatura antes de qualquer instalação.
- [ ] Verificar disponibilidade do S24 e ADB; registrar estado de conexão e preservar a versão instalada. Não supor que a conexão esteja ativa.
- [ ] Registrar cenas de referência e estado de controles, idioma e progresso; identificar o caminho de retorno ao APK aceito sem apagar dados.
- [ ] Confirmar como produzir candidatos isolados: `--controller-base-apk` exige a base de biblioteca `8797e444…`, `--controls` e não aceita `--ptbr`/`--widescreen` simultaneamente; esses ajustes devem estar presentes na base. A opção atual `--console-ui` também aplica Y/B estático, logo não serve como teste isolado de HUD sem adaptação.

**Aceite:** identidade, assinatura e caminho de retorno comprovados; se o aparelho estiver indisponível, avançar nos passos de análise e testes host, mantendo aceite de aparelho pendente.

## 2. HUD adaptativo e foco

**Arquivos:** `scripts/patch-controls-console-ui.py`, `patches/controls-diag/console-ui.S`, `scripts/build-selective.py`; testes específicos existentes ou novos apenas para os contratos alterados.

- [ ] Rever o stub v2, guardas de hash/Build ID/bytes e preservação da lista de itens; identificar também se entrada tátil continua ativa apesar de oculta e definir comportamento observável seguro.
- [ ] Preparar um candidato de teste que isole o HUD da skin Y/B; manter o build padrão e as demais opções funcionais. Validar bytes, fluxo ativo/inativo, releitura e guardas no host.
- [ ] No S24, verificar batalha com controle conectado: HUD tátil oculto, lista de itens visível e ações funcionando. Desconectar e reconectar durante a batalha; verificar retorno do HUD e funcionamento do toque.
- [ ] Verificar foco, seleção e navegação em menus e seleção de personagem, incluindo mudança de conexão; registrar capturas e resultado por cenário.

**Aceite:** HUD muda com o estado do controle, toque continua utilizável sem controle e os elementos de seleção e itens permanecem visíveis. Um build assinado ou hash correto não substitui esses testes.

## 3. Prompts ABXY contextuais

**Arquivos:** `scripts/patch-controls-prompts.py`, `scripts/build-selective.py`, recursos identificados em `docs/CONTROLLER_CONSOLE_UI_INVESTIGATION_20261027.md`; novos arquivos somente após identificar os pontos de integração.

- [ ] Inventariar as telas de menus, seleção, batalha, tutoriais e configuração e associar cada prompt visível à ação que representa; registrar atlas e pontos de desenho, incluindo casos ainda não identificados.
- [ ] Decodificar ou comprovar os UVs dos sprites `xcmn_*` e sua correspondência A/B/X/Y. Conferir o mapeamento físico GameSir e os bindings efetivos, não apenas a posição do glyph.
- [ ] Identificar como consultar conexão e binding atual na geração/desenho dos prompts; implementar a menor alteração que os atualize após conexão, desconexão e mudança de configuração, preservando a apresentação tátil.
- [ ] Substituir ou restringir a skin Y/B estática atual quando a rota dinâmica estiver comprovada; verificar que não restam prompts enganosos sem controle.
- [ ] Validar guardas e saídas no host e capturar no S24 todas as telas inventariadas, incluindo bindings alterados e reconexão.

**Aceite:** cada prompt coberto corresponde à ação e ao binding efetivo, usa ABXY GameSir quando apropriado e volta à apresentação adequada sem gamepad. Uma tela não inspecionada permanece explicitamente pendente.

## 4. Configuração do controle

**Arquivos:** relatório de investigação, projeto Ghidra `work/controls-console-ui-20261027/sprite-xrefs-static-20261027`; scripts de patch/build a definir conforme descoberta.

- [ ] Rastrear criação, inicialização, controle, desenho, encerramento e propriedade de `ccKeyConfigDuel`; determinar se seus métodos e persistência são compatíveis com Android e Paddleboat. Reutilizar Ghidra com `-noanalysis`; registrar limites dos xrefs e testes realizados.
- [ ] Identificar a seleção que leva ao passo 4 da pausa e um ponto para acrescentar acesso à configuração física sem substituir a página tátil `Entry(0xaa)`; comprovar retorno e ciclo de vida.
- [ ] Comprovar caminho binding → entrada real → armazenamento → recarga. Se o editor nativo não atender, documentar a evidência e projetar a menor alternativa integrada antes de implementá-la.
- [ ] Implementar acesso, navegação, confirmação, cancelamento, prevenção ou tratamento claro de conflitos e restauração dos padrões; manter a configuração tátil acessível.
- [ ] Testar no S24: alterar pelo menos dois botões, confirmar efeitos em jogo e prompts, cancelar alteração, restaurar padrão, reiniciar o jogo e verificar persistência, além de desconectar e reconectar.

**Aceite:** configurações alteradas funcionam e persistem, prompts acompanham os bindings e usuário pode retornar ou restaurar padrões; a tela tátil permanece funcional.

## 5. Composição, regressão e entrega

**Arquivos:** `scripts/build-selective.py`, scripts de teste pertinentes, README/PRD e relatório de validação do S24.

- [ ] Integrar os patches comprovados com base S24, controles, HUD e prompts; manter as guardas de hash, Build ID, bytes e releitura, sem permitir combinação incorreta de bibliotecas. Não tratar opção experimental como aceita antes dos testes.
- [ ] Executar testes específicos das guardas, bindings e recursos, `py_compile` dos scripts alterados e `git diff --check`; conferir assinatura, alinhamento, integridade, manifesto e identidade da composição gerada.
- [ ] Instalar candidato assinado preservando dados e executar matriz no S24: abertura repetida; menus e seleção; batalha e itens; toque sem controle; conexão/reconexão; configuração e persistência; pt-BR; widescreen e alinhamento de toque. Registrar cada cenário, hash e capturas, bem como falhas Vulkan se ocorrerem.
- [ ] Corrigir regressões e repetir os cenários afetados. Atualizar documentação com evidências e limites reais; não declarar concluído se algum critério estiver sem teste.
- [ ] Preparar APK final assinado e manifesto; obter confirmação específica antes de substituir `build/Naruto Ultimate Ninja Storm.apk`, e depois verificar o arquivo entregue por hash e assinatura.

**Aceite final:** todos os critérios acima passam na mesma composição identificada por hash no S24, com progresso preservado e retorno disponível. Sem dispositivo, assinatura compatível ou evidência de uma cena, a entrega permanece pendente.

## Dependências e estimativa

1. Preparação antecede qualquer instalação. O HUD pode ser validado separadamente da investigação do editor.
2. Prompts que refletem bindings dependem da descoberta do mapa efetivo; a validação completa depende da configuração persistente.
3. A integração final depende do aceite dos componentes e da composição em um único APK.
4. Ainda não há estimativa total confiável: a rota e a compatibilidade do editor são desconhecidas. Reestimar depois da etapa 4 de investigação, com base no contrato identificado e nos primeiros testes no S24.
