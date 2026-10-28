# Controles: estado atual

O suporte Paddleboat/GameSir foi validado no S24 segundo a documentação do projeto. O usuário confirmou no S24 que o HUD condicional fica oculto com controle e aparece sem controle. A skin Y/B tem evidência estática e de host; não foi aceita no aparelho. A skin é fixa e não acompanha conexão ou bindings.

## F1.1 — HUD condicional

- O APK com gamepad aceito foi recuperado do S24 para `build/UNSM-S24-GAMEPAD-INSTALADO.apk`; seu SHA-256 `a9288675a6d66b235349f1b20b81e9adf95cd9fa6aeb69b2811138d14bfd32fd` coincide com o registro de aceite. A biblioteca e seu manifesto conferem com SHA-256 `2923db436931bb2f3a0b7178a7b1c007434e28d269e5ec5a81c5be4a73e96db7`.
- O patch v2 passou em `--check-only`: Build ID, entrada, manifesto, prólogo e verificações da cave; produziu em memória o SHA-256 `557b842e7f3372b1498843fce78df8b32bab43e26030d4092ef6c66ce290cb9e`. Os cinco testes existentes de fluxo passaram.
- Disassembly confirmou o desvio para o status Paddleboat, o retorno ao desenho original quando inativo e o salto para a lista de itens quando ativo. A comparação reversível confirmou que apenas os dois intervalos registrados mudaram e que a cave do gamepad foi preservada. Isso não prova foco, seleção ou transições no aparelho; a verificação de branches da cave examina branches imediatos B/BL, não todos os possíveis acessos indiretos.
- O candidato `build/UNSM-S24-GAMEPAD-HUD-F1.1.apk` foi produzido substituindo somente a biblioteca no APK recuperado. A assinatura foi verificada com certificado igual ao da fonte; alinhamento 16 KiB e CRC/tamanho dos 571 demais membros passaram. Foi instalado por atualização via USB e o SHA-256 instalado conferiu com o candidato.
- O usuário confirmou no S24: com controle o HUD fica oculto, sem controle o HUD aparece, a lista de itens permanece visível e foco e seleção funcionam com o controle. Também confirmou que, sem fechar o jogo, o HUD reaparece ao desconectar e desaparece ao reconectar.

## Decisões confirmadas

- Preservar controle funcional, lista de itens e navegação; usar o estado ativo do Paddleboat e restaurar o HUD tátil na desconexão.
- Reutilizar os sprites de `cmn_button00` e manter `xbattle_pad.xfbin` para o HUD tátil.
- `ccOptionControl` e `Entry(0xaa)` pertencem aos controles táteis; não substituir essa tela pelo editor Duel sem conhecer seu ciclo de vida.

## F1.2 — prompts ABXY

O `--check-only` da skin Y/B passou na base anterior. Ela altera dois glyphs por posição e permanece ativa sem controle; não comprova ações nem cobre A/X. Seu script exige a biblioteca anterior e rejeita diretamente a base F1.1 aceita. Não aplicar essa skin como solução dinâmica.

O inventário inicial está no catálogo. A análise existente associa `CtrlCaptionControls` aos textos Awakening e Costume e a elementos de `msel1.xfbin`; isso não identifica os glyphs nem os bindings correspondentes. Antes de modificar o jogo, é necessário comprovar os pontos de desenho e o mapa efetivo de cada prompt, além da troca ao conectar e desconectar.

Os quatro sprites `xcmn_batsu`, `xcmn_circle`, `xcmn_triangle` e `xcmn_square` têm regiões de 68×68 no atlas `cmn_button00`, conferidas visualmente como A, B, Y e X, respectivamente. As coordenadas e os hashes estão no catálogo. Isso confirma os recursos, mas não prova que as telas Android usem esses sprites ou reflitam os bindings ativos.

No ELF, `ccHelpIconSet` e `ccHelpTextSet` possuem funções que selecionam IDs de confirmação e cancelamento `0x10`/`0x12` a partir dos campos `+0x1e0`/`+0x1e4` da instância de `nuccSys`; a relocação identifica o ponteiro global. Uma busca por chamadas ARM64 diretas encontrou usos, entre outros, na inicialização e controle dos ícones da seleção de personagem e na preparação do tutorial. A execução dessas rotas no Android e a atualização visual após conexão ou alteração de bindings ainda não foram demonstradas.

`nuccSys::UpdateKeyAssign` grava esses dois campos quando encontra entradas válidas e converte máscaras `0x10/0x20/0x40/0x80` em máscaras internas. Os helpers de ícones, porém, escolhem somente os IDs de A/B; não cobrem X/Y mesmo quando os campos recebem outras máscaras. A busca por chamadas `BL` diretas para `UpdateKeyAssign` não encontrou callers; chamadas indiretas não foram excluídas. A origem das entradas, o ciclo de atualização e a apresentação na desconexão continuam pendentes.

Na seleção de personagem, `InitHelpIcon` cria os ícones com os IDs obtidos naquele momento. `CtrlHelpIcon` cria o conjunto se estiver ausente e habilita o ícone de cancelamento encontrado pelo ID atual; nesse caminho, não chama `ChangeButton` nem recria o ícone de confirmação. `ChangeButton` existe e substitui um sprite preservando posição e alpha, mas não foi demonstrado que essa tela o chame na conexão ou mudança de binding. A decompilação foi feita em projeto Ghidra somente leitura; os bytes das funções conferem com a biblioteca F1.1. Não há prova de atualização visual dinâmica no S24.

`GetHelpIconId` procura tanto o ID do texto quanto o ID do botão e retorna o índice da peça ou `-1`. Na inicialização da seleção de personagem, os textos de confirmação e cancelamento usam os IDs `0x3e` e `0x3f`; esses IDs permitem localizar as peças independentemente do glyph atual. `UpdateKeyAssign` consulta dados através do singleton `mmInputManager`, identificado pela relocação. A verificação em memória confirmou que o `xmode.xfbin` da F1.1 tem o mesmo hash da base anterior, sem aplicar a skin estática.

Análise estática adicional encontrou `mmControllerManager_Android::ControllerStatusCallback` chamando `mmController_Android::SetLayout` no ramo de conexão (`param_2 == 2`). `SetLayout` monta a tabela de 16 entradas, guarda em `+0x154`/`+0x156` os índices cujas máscaras são `0x10`/`0x20` e ativa a flag `+0x158`. `nuccSys::MainStart`, chamado por `nuccSys::Update`, contém uma cópia da lógica de `UpdateKeyAssign` que consome essa flag e atualiza as máscaras. O valor do callback não deve ser confundido com o valor retornado pela consulta de status usada pelo HUD. A frequência em execução e a atualização dos sprites continuam sem prova no aparelho.

Na captura da seleção de personagem do S24 com controle conectado, a F1.1 exibe botões Android, sem glyphs ABXY visíveis. A decompilação mostra que `ccHelpIconSet::Ctrl` e `Draw` são retornos imediatos e que `ccSelectCharacter::Ctrl` e `Draw` não chamam `CtrlHelpIcon` e `DrawHelpIcon`. Uma busca por branches B/BL no ELF encontrou somente a chamada de `CtrlHelpIcon` para `InitHelpIcon`; não encontrou chamadas diretas às outras duas rotinas, sem excluir referências indiretas. Assim, alterar apenas os helpers de IDs não exibiria os prompts nessa tela; é preciso implementar e comprovar desenho, posição e ciclo de vida. Captura: `work/controls-console-ui-20261027/f12-character-connected.png`, SHA-256 `8ff8e27489613fd339d4bc091d699afe02d3f85c9dce295722aa766cea4f7e73`.

O usuário confirmou os controles da seleção de personagem no GameSir: **A** seleciona, **Y** escolhe Aleatório e **Start** abre Configurações de batalha. Essas associações não comprovam o comportamento de outros botões ou telas.

`ccCharacterSelectPad::Setup` cria os quatro botões de texto Android com `InitializeTextButton`: Aleatório, Configurações e duas instâncias de Selecionar. `ccCommonTouchTextButton::SetText` atualiza o texto e sua escala; o código de desenho do pad chama os quatro objetos. Esse é um ponto de integração concreto para a interface exibida, mas ainda não estabelece como desenhar os sprites ABXY sem interromper o toque ou manter a apresentação ao trocar o controle.

Na seleção de cenário, `ccStageSelectPad::Setup` cria botões Selecionar e Aleatório em `+0xb0` e `+0x410`; `ccStageSelectPad::Draw` desenha ambos. O usuário confirmou A para Selecionar e Y para Aleatório. O candidato atualizado em memória adiciona os glyphs nessa tela, com hooks no desenho e destrutor; não foi empacotado nem validado no S24.

Como a cave existente da F1.1 tem menos espaço que o necessário para o ciclo completo, `scripts/extend-controls-elf.py` reserva espaço em memória para a implementação na biblioteca identificada por hash; os testes verificam segmentos, alinhamento, seções e branches diretos para a nova região, sem cobrir referências indiretas. `llvm-readelf` aceitou a estrutura resultante, mas isso não comprova carregamento no Android. `patches/controls-diag/abxy-mapping.c` mapeia as quatro máscaras em IDs de sprites, com teste de host para todas as máscaras de 16 bits. Esses componentes foram incorporados ao candidato instalado; o comportamento no S24 ainda requer confirmação.

`scripts/patch-controls-select-prompts.py` monta um candidato experimental com hooks de desenho e destruição do pad de seleção. O payload prevê Y em Aleatório, o sprite correspondente à máscara de confirmação em Selecionar e o texto START em Configurações, somente com controle ativo. O APK separado `build/UNSM-S24-GAMEPAD-ABXY-F1.2-SELECAO.apk` foi assinado e conferido no host e instalado por atualização no S24; o SHA-256 do APK instalado confere. O vídeo mostra o jogo carregado e A/Y/START desenhados na seleção e nos suportes; ações, posição adequada em todas as situações e reconexão ainda precisam de confirmação. O host verificou o ciclo dos objetos, os hooks e a reversão byte a byte. **Outras telas e bindings personalizados permanecem pendentes; não é aceite da F1.2.**

Um projeto Ghidra separado localizou as referências dos três textos aos métodos de setup dos pads de seleção; a análise completa atingiu o limite de 240 segundos e teve erros do analisador. As referências reportadas coincidem com uma busca independente por instruções ARM64; o restante da análise não deve ser tratado como completo.

Os fluxos e cenários estão em [flows.json](flows.json) e [cases.json](../../tests/controls/cases.json). Quadros do vídeo fornecido mostram prompts na seleção e nos suportes, ausência de glyphs na arena e instruções e imagens táteis nos tutoriais. O usuário confirmou A para Selecionar e Y para Aleatório na arena; relata que B leva à tela inicial do celular em todas as telas. A causa ainda está em investigação. O vídeo não comprova perda de foco ou transições de conexão. Os textos PT-BR de `Mobile_Tutorial` incluem instruções táteis e marcadores de ícones; sua troca global prejudicaria o fallback. A página específica e os bindings ativos ainda precisam ser identificados.

## Pendências

- Confirmar consumidores de prompts e correspondência ABXY com bindings efetivos nas telas Android.
- Localizar criação, navegação, retorno e persistência de `ccKeyConfigDuel` no Android; validar a configuração completa.

Fontes e confiança: [catálogo](catalog.json). Cenários: [casos](../../tests/controls/cases.json).

O teste de B no S24 registrou `BTN_EAST` no GameSir e, em seguida, `onBackInvoked` e `moveTaskToBack` no Android; o PID do jogo permaneceu ativo. A saída para a tela inicial é navegação de sistema, não queda comprovada. Na biblioteca F1.1, `mmInput_Android::UpdatePlatform` encaminha o evento ao Paddleboat e pode substituir o resultado pelo retorno de `mmKeyboardManager_Android::NotifyKeyEvent` antes de `AInputQueue_finishEvent`; o GameSir é classificado também como teclado. Esse caminho é uma hipótese concreta, mas os retornos efetivos e o evento de fallback ainda precisam ser medidos antes do patch.

O usuário observou o mesmo comportamento de B em outros aplicativos. No S24, o arquivo de sistema `Generic.kl` associa o código físico 305 a `BUTTON_B`, e `Generic.kcm` define `BUTTON_B` com `fallback BACK`. Isso explica o caminho de retorno do Android quando o evento não é tratado, mas não confirma qual consumidor do jogo devolveu evento não tratado. Não alterar o mapeamento global do aparelho.

A correção experimental `scripts/patch-controls-gamepad-b.py` compõe em memória os prompts existentes e intercepta as duas chamadas de finalização de eventos em `0x9e7c30` e `0x9e7cbc` (VA ELF). Após a entrega original ao motor, marca tratado apenas evento de tecla `BUTTON_B` com fonte gamepad; os demais preservam o resultado anterior. O `--check-only` e testes de host passaram. Não comprova que B execute cancelar, ataque, ou que o Android deixe de voltar no aparelho; a implementação ainda não foi empacotada ou instalada.

A composição em memória dos prompts de personagem e arena com a proteção de B passou em `--check-only`: biblioteca resultante SHA-256 `dac92156cad6ced9c68f92e4ede76736b44747cedc7e68e9be179fc127cd91e7`. Os testes de host verificam a lógica de apresentação e os branches, sem comprovar posição, retorno, foco ou estabilidade no S24.

O caminho estático dos tutoriais consulta ID, texto e imagem por página em `ccTutorialManager`, e `ccDispTutorial::Draw` reimprime o texto; o catálogo registra esses pontos em VA ELF. O conteúdo exibido no vídeo corresponde textualmente a `Mobile_Tutorial/tutori_203_01`, mas a página ativa e sua imagem não foram instrumentadas. Trocar a saída por modo de entrada requer validar ABI, bindings e seleção dinâmica de imagens; a versão tátil deve permanecer intacta.

O usuário relatou comandos de combate: L2 defesa, R2 substituição, L1/R1 suportes, direcional itens, Y chakra, X ataque e A pulo. X para ataque diverge do mapa estático anterior que associa `KeyAttack` a B; o binding efetivo e o motivo da diferença precisam de confirmação antes de adaptar as instruções. O usuário informou Y + A para Investida Ninja e que B leva o jogo à tela inicial; a ação interna de B permanece sem confirmação.

Foi preparado candidato separado de HUD, prompts de personagem/arena e tratamento de B, assinado com certificado igual ao da F1.1 e verificado por hash, alinhamento e CRC/tamanho dos demais membros. Ele não foi instalado; tutorial contextual não está implementado. Manifesto e SHA constam no catálogo.
