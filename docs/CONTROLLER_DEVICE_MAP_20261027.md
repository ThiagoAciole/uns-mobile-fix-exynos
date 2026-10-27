# Mapeamento no S24 — GameSir (27/10/2026)

## Estado e limites

Mapeamento em andamento para HUD, prompts, navegação e configuração. S24 SM-S921B conectado por ADB; pacote `com.bandainamcoent.ultimateninjastorm`, versão 1.2.10, código 38. O aplicativo foi aberto a partir da instalação existente, sem instalar APK, desinstalar ou limpar dados. A presença de `GameSir-X5 Lite` como GAMEPAD/JOYSTICK foi observada posteriormente no Android; isso não comprova interação nesta rodada.

## Telas observadas

| Tela | Observação | Evidência |
|---|---|---|
| Título | Texto `TOQUE PARA INICIAR`, versão 1.2.10. | `work/device-map-20261027/launch.png` |
| Configurações de controle | Exibe controles gerais, sensibilidade de movimento, botões, rolagem e restauração. A captura apresenta `Desativado`; não se deve inferir a que dispositivos se aplica sem confirmação. O HUD de batalha aparece no fundo. | `work/device-map-20261027/options.png` |
| Seleção de modo | Modo Missão Suprema, setas e retorno visíveis. | `work/device-map-20261027/control-scroll.png` |

A sequência não estabelece o caminho exato entre telas: houve mudança de tela entre capturas, possivelmente por interação concorrente ou transição. Não atribuir a navegação a uma ação específica. O GameSir foi conectado após as primeiras capturas; faltam capturas e testes com ele ativo, seleção de personagens, batalha, pausa, reconexão e quaisquer prompts contextuais.

## Próximas observações

Capturar seleção de personagens com controle ativo; depois batalha, lista de itens e pausa; documentar foco, prompts e diferenças antes/depois de conectar. Identificar uma entrada de configuração física ou registrar sua ausência apenas nas telas efetivamente percorridas. Não alterar opções nem progresso para estabelecer o inventário inicial.

## Seleção de personagens com GameSir conectado

Captura `work/device-map-20261027/character-gamesir.png`: Naruto aparece destacado na lista, com setas laterais e botões visíveis `Aleatório`, `Configurações de batalha` e `Selecionar`. Não há glyphs ABXY visíveis nesta captura. A imagem demonstra o estado visual, não comprova isoladamente quais botões físicos ativam cada ação ou se o destaque acompanha todas as entradas.

## Batalha com GameSir conectado

Captura `work/device-map-20261027/battle-gamesir.png`: HUD de batalha apresenta botões táteis à direita, botão de pausa, barras, personagens de suporte e lista de itens na parte inferior. O controle estava conectado conforme inventário Android anterior. A captura é da versão instalada existente, não do candidato de ocultação; confirma a presença visual do HUD, sem avaliar a resposta dos botões ou a desconexão nesta rodada.

## Pausa e listas de comandos

- `pause-gamesir.png`: menu apresenta lista de comandos do personagem, comandos básicos, tutorial, configurações de controle, retorno à seleção de personagem ou modo e fechar. Os controles táteis permanecem visíveis ao fundo.
- `basic-commands.png` e `basic-attacks.png`: a lista básica apresenta texto em inglês e orientações de toque com ícones táteis mesmo com o GameSir conectado; foram observadas as seções de movimento, levantar, defesa, ataque e combo. Não foi inspecionada a lista inteira.
- `character-commands.png`: a lista do Naruto apresenta sequências usando ícones táteis de ataque e movimento, sem ABXY visíveis no trecho capturado.

Essas telas são pontos adicionais para investigar texto e glyphs contextuais; substituir apenas a arte dos dois prompts de seleção não cobre essas listas. Arquivos de evidência em `work/device-map-20261027/`.
