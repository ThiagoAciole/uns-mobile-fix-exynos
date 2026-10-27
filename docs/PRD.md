# PRD — Naruto: Ultimate Ninja Storm no Android

Versão: 1.0 · Data: 27/10/2026 · Status: em execução

Escrito para: mantenedores e colaboradores do projeto, e usuários técnicos que querem instalar a versão corrigida.

## 1. Problema

O APK 1.2.10 original do jogo tem três problemas em dispositivos Android atuais:

1. **Falha de renderização em GPUs Exynos.** O engine pede o formato de depth `VkFormat 129`, que a GPU Xclipse não suporta. A tela não sai como deveria.
2. **Tela não ocupa a largura de celulares widescreen.** O jogo é projetado para 16:9 e deixa margens laterais, e os toques ficam deslocados.
3. **Textos e letreiros só em inglês.** O jogo não tem português.

Além disso, o controle externo (gamepad) não responde no jogo. Esse problema ainda não está resolvido.

## 2. Usuários

- **Principal:** o autor, que testa no Galaxy S24 (SM-S921B).
- **Secundário:** jogadores técnicos com o mesmo problema, que têm o próprio APK 1.2.10 e sabem usar terminal, ADB e Python.

Não é público geral. Não há instalador nem loja.

## 3. Objetivos e recursos

| Recurso | Objetivo | Estado |
|---|---|---|
| **Correção Exynos** | Jogo renderiza em GPUs Exynos sem o formato de depth não suportado. | Patch de 1 byte aplicado e verificado por hash. Parte da build final aceita. |
| **Widescreen** | Preencher telas 2340×1080 sem esticar personagens e com toques alinhados. | Validado no S24 em 2340×1080. Outras proporções **não** foram testadas. |
| **Português (Brasil)** | Textos de menus, mensagens, batalha e itens traduzidos; letreiros gráficos traduzidos. | Catálogos cobrem 7.104 textos únicos. Dublagem e algumas artes continuam em inglês. |
| **Controle externo** | Navegar nos menus e jogar com gamepad. | **Não funciona.** Causa ainda não identificada. |

## 4. Escopo

Dentro:
- Scripts que geram APKs a partir do 1.2.10 original, de forma seletiva.
- Documentação de instalação, evidências e limites.
- Diagnóstico do controle externo no aparelho.

Fora:
- Distribuir o jogo ou o APK original.
- Suporte a outros dispositivos sem teste próprio.
- Dublagem em português.
- Outras versões do jogo além da 1.2.10.

## 5. Requisitos funcionais

- **RF1.** O usuário escolhe quais ajustes incluir (Exynos é sempre incluído; widescreen e pt-BR são opcionais).
- **RF2.** Cada build vai para uma pasta nova e gera um manifesto com os hashes de entrada e saída.
- **RF3.** A opção de controle externo recusa a execução enquanto não houver patch validado.
- **RF4.** A assinatura é opcional e usa o keystore do próprio usuário.

## 6. Requisitos não funcionais

- **Segurança:** chave, senha, APKs do jogo e `work/` nunca entram no Git nem em publicações.
- **Verificabilidade:** toda alteração nativa é guardada por hash da entrada, Build ID e bytes esperados.
- **Preservação:** a instalação atualiza o pacote existente, sem desinstalar nem limpar dados.
- **Reversibilidade:** cada patch gera saída separada; a entrada original não é alterada.

## 7. Critérios de aceite

| Ajuste | Critério | Evidência atual |
|---|---|---|
| Exynos | Biblioteca final com SHA-256 `CCEA158F…` a partir da entrada `C631E7…`. | Verificado por hash e pelo repacker. |
| Widescreen | Tela 2340×1080 sem margem lateral e toques alinhados no S24. | Aceito pelo usuário no S24. |
| pt-BR | Contadores de campos alterados batem com a documentação (7843 / 442 / 679). | Verificado no build. |
| Controle | Navegação nos menus e gameplay com gamepad no S24. | **Não atendido.** |

## 8. Pendências

1. **Controle externo.** Descobrir por que o jogo não reage ao GameSir-X5 Lite, que envia eventos corretos ao Linux e às teclas do Android. Ver [ARCHITECTURE.md §6](ARCHITECTURE.md#6-caminho-da-entrada-do-controle).
2. **Widescreen em outras proporções** e outros aparelhos.
3. **Assinatura** do build seletivo com keystore real (ainda não testada).
4. **Commit** dos arquivos que ainda estão fora do Git.

## 9. Riscos

- O patch nativo depende do Build ID exato. Outro build do jogo exige novo mapeamento.
- Os offsets nativos podem mudar em outra versão do engine, e nesse caso os scripts abortam em vez de corromper o APK.
- O widescreen pode quebrar telas não testadas: só o S24 foi verificado.
- Os catálogos de tradução cobrem as strings identificadas; textos novos ficam em inglês.
