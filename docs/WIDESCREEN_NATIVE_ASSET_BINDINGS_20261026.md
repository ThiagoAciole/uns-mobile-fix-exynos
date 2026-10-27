# Ligações estáticas de sprites e assets — 26/10/2026

Este relatório registra novos vínculos obtidos da biblioteca ARM64 e dos XFBINs extraídos do APK canônico. Ele não representa aceitação visual/toque no S24.

## Base reproduzível

- APK: `build/Naruto Ultimate Ninja Storm.apk`, SHA-256 `5dac1302663cbec6abc678b7f9c84976c2a2a1fea487f183febd2d42d2147d86`.
- Biblioteca: SHA-256 `5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071`, Build ID `c3e506f9be350dfb4a00c79228754028`.
- Inventário CPK atualizado diretamente dessa base: `work/candidates/widescreen-app-completion/canonical-base-cpk-inventory.json`, SHA-256 `faed547c903ad4bc88878023babf0960da9df6fb233fadf5e8ba2978ea1ab313`. Os 12 bancos CPK foram validados.
- `work/inventory/cpk-inventory.json` é um inventário histórico: nele `installTimeDisc.awb` tem 435.684.928 bytes; na base canônica, o membro tem 584.534.016 bytes. Uma extração com o inventário antigo foi corretamente recusada pelo verificador. Seus offsets não servem para o APK canônico.
- Os sete XFBINs de mapa/menu foram extraídos da base com `scripts/extract-cpk-files.py` para `work/candidates/widescreen-app-completion/sprite-binding-assets/`; hashes estão no `manifest.json` ao lado. Tutorial e imagens de tutorial foram extraídos separadamente em `tutorial-canonical-source/`; o hash da textura `xcmn_tutorial_win00` é `3e9db920fa2c6a4ba71e66965eab82ac6fdba9a79d9ae0f0ddf5ec9b7ba1bac2` e coincide com a exportação anterior. PNGs canônicos estão em `tutorial-textures-canonical/`.

## Menu inicial da aventura

`ccDispStartMenuRpg::Init` (ELF VMA `0xb056fc`) cria os IDs `0x51`, `0xdf`, `0xe0`, além dos sprites de moeda. `Draw` (`0xa7d2a0`) desenha `0x51` e `0xdf`, processa animações/texto e desenha os dados de moeda. As entradas da tabela `CCD_DISP_ELEMENT_DATA_INFO_TBL` foram ligadas pelas relocações da biblioteca exata e conferidas com os chunks nos XFBINs extraídos:

| ID | XFBIN e chunk | Uso provado no código |
|---|---|---|
| `0x51` | `data/interface/index/ANDROID/xcmn_index.xfbin#xcmn_index04` | Sprite criado em `Init`, armazenado em `this+0xd8`, desenhado em `Draw`. |
| `0xdf` | `data/interface/adv/eng/ANDROID/xadv_mission_menu.xfbin#xadv_mission_menu10` | Sprite criado em `Init`, armazenado em `this+0xe0`, desenhado em `Draw`. |
| `0xe0` | `data/interface/index/eng/ANDROID/xadv_indexname.xfbin#xadv_indexname_fd01` | Sprite aplicado à animação de índice `0x292` em `Init`. |
| `0x180`, `0x181`, `0x182`, `0x185` | `data/interface/adv/eng/ANDROID/xadv_money.xfbin#xadv_moneyicon`, `#xadv_money`, `#xadv_scroll`, `#xadv_ryo_fd` | IDs passados ao construtor `ccDispCurrency` em `Init`; `Draw` chama duas camadas de moeda. |

O menu também consulta as mensagens `startmenu/rpg_info00`, `rpg_info01` e `rpg_info02`. A camada de cobertura S24 adicionada ao `PushLayer` não move estes sprites ou as coordenadas da animação. Ainda faltam decodificar bounds/UVs, ligar animações `0x292–0x295` aos layouts XFBIN e medir as hitboxes de cada opção.

## Mapa da vila

`ccDispStageMap::Init` usa os IDs `0xd4–0xd7` e `0xda`; `Draw` (`0x96a214`) cria camadas separadas para o mapa e controles. A tabela nativa aponta para os seguintes pares:

| ID | XFBIN e chunk na tabela nativa | Confirmação na base extraída |
|---|---|---|
| `0xd4` | `data/interface/adv/ANDROID/xadv.xfbin#xadv_mapmat00` | **Divergência:** o arquivo existe, mas não contém chunk com esse nome. Não assumir que é o fundo nem alterar até localizar a rota correta. |
| `0xd5` | `data/interface/adv/eng/ANDROID/xadv_map.xfbin#xadv_map00frm` | Chunk presente. |
| `0xd6` | `data/interface/adv/eng/ANDROID/xadv_map.xfbin#xadv_map00a` | Chunk presente. |
| `0xd7` | `data/interface/adv/eng/ANDROID/xadv_map.xfbin#xadv_map00a01` | Chunk presente. |
| `0xda` | `data/interface/adv/ANDROID/xadv_map00.xfbin#xadv_mapicon00` | Chunk presente; textura tem duas entradas homônimas, então falta resolver a variante/material em uso. |

As texturas canônicas ajudam a decidir a camada sem inferir que ela deve ser esticada: `xadv_map00a` é um atlas 384×384 do aro do minimapa e outros elementos; `xadv_map00` é o mapa da vila em 1280×972; `xadv_mapicon00` tem variantes 192×192 para ícones. O mapa e os ícones devem manter proporção. O defeito de alinhamento citado pelo usuário precisa ser resolvido por âncora/posição na rota nativa.

Os binds que coincidem ainda não informam UV, bounds finais, centro de escala animado ou região de toque. `DrawIcon`, `GetPosByParam` e `ClacOffsetCtrl` confirmam transformação de ícones separada do container; não se deve reposicionar marcadores pela aparência do screenshot.

Na rota de desenho, o ramo `state 1 / param 3` usa um layer `0x11` com limites calculados como `left = x0 + width*(1-scale)/2 + offsetX`, `top = y0 + height*(1-scale)/2 + offsetY`, `width = mapWidth*scale`, `height = mapHeight*scale`. Isso mantém o layer centrado durante a animação de escala; `ClacOffsetCtrl` anima `offsetX/offsetY`. Em seguida, o overlay usa um layer `0x16` de `GetUIScreenWidth() × GetUIScreenHeight()`. As coordenadas dão uma rota para comparar com a captura, mas ainda não identificam qual estado corresponde ao minimapa visível no gameplay.

`ccDispStageMap::Ctrl` controla estado de pausa/mapa e navegação por `ccMenuPad`, além de consultar o botão Android Back. Não foi localizado ali um hitbox de toque por marcador; outra camada/input route pode receber toque. Portanto, não aplicar a escala do mapa aos controles de toque sem traçar `ConvertScreenPosToRenderPos` e o consumidor do evento.

## Tutorial e localização

- `ccDispTutorial::Setup` (`0xaf1cac`) chama `ccDispSprite::Create(0x25e)` e `Create(0x25b)`. A tabela nativa e as relocações ligam estes IDs a `data/interface/cmn/PLAT/cmn_tutorial.xfbin`: `0x25e → xcmn_tutorial_dmy` e `0x25b → xcmn_tutorial_win00`. O último é o painel visível; o primeiro é auxiliar. A classe aplica ao painel escala X derivada da largura lógica e calcula escala Y a partir da altura dos botões e do próprio sprite.
- O cabeçalho comum usado pelo diálogo não é o mesmo sprite do painel: `ccWindowHeader` cria o clump ID `0x36e`, ligado pela tabela a `data/interface/cmn/PLAT/xcmn_mobile.xfbin#xcmn_hbase01_a01`. A altura vem do AABB do model. O código define posição, largura lógica e layer do cabeçalho separadamente.
- `ccDispTutorial::Draw` (`0xa7a308`) lê `xcmn_tutorial_tag01_a/b` do clump de tutorial; os chunks existem em `data/interface/cmn/ANDROID/cmn_tutorial.xfbin`. Essa é uma rota de coordenadas/conteúdo diferente dos sprites do painel e do cabeçalho identificados acima.
- O aviso da captura foi identificado no catálogo pelo texto: `dialog_014_01`, registro 11565 de `patches/ptbr/catalogs/message.bin.json`, origem “Go ahead and check the Mission List.” e tradução “Agora confira a Lista de Missões.”. O texto da captura coincide. Isso identifica a mensagem efetivamente desenhada; não confundir com a entrada de conteúdo `tutori_014_01` (registro seguinte), que descreve o tutorial do menu Itens.
- `ccTutorialManager::GetTutorialMsgId` escolhe o ID pelo índice de página no registro ativo; `GetTutorialMsg` consulta o catálogo “Mobile” com esse ID. `GetTutorialPicture` usa lista de nomes de chunk por página e procura no XFBIN de tutorial, com caminho de fallback localizado. Os dois caminhos lógicos no binário ainda precisam ser reconciliados com os caminhos físicos presentes no CPK antes de atribuir uma picture ao aviso; não foi encontrada confirmação de `texture_014_01` no XFBIN extraído.
- A entrada de controle percorre `ccDispTutorial::Ctrl → ccWindowHeader::Ctrl → ccCommonTouchButton::Ctrl → ccDispTouchButton::Ctrl`, que atualiza a colisão ligada ao `ccTouchButton`; o `ccButtonSet` também recebe seu próprio `Ctrl`. O código de tutorial navega páginas via estado/controlador e Android Back. Isso prova o caminho, mas não fornece por si só os retângulos touch em coordenadas do S24.
- Próximo vínculo: correlacionar o registro ativo do tutorial com `dialog_014_01` e confirmar se há imagem associada; depois medir bounds finais e hitbox de confirmar/fechar. Não expandir novamente a arte do painel antes de conferir a saída no S24: o código já escala X para largura lógica; a divergência restante pode estar no compositor, nas coordenadas, na variante do painel ou na conversão de toque.

Evidência de decompilação exata: `ghidra-tutorial-setup2-output.txt`, `ghidra-window-ctor-output.txt`, `ghidra-clump-create2-output.txt`, `ghidra-tutorial-input-output.txt`, `ghidra-common-touch-input2-output.txt` e `ghidra-tutorial-manager-output.txt`. As entradas da tabela são `0x1321800/08` (sprite `0x25b`), `0x1321830/38` (sprite `0x25e`), `0x1322930/38` (clump `0x36e`) e `0x1325790`/`0x13257a0` (paths lógicos da lista de pictures); os addends de relocação foram lidos como strings terminadas em NUL no ELF canônico.

## Limite e decisão

As correspondências de ID → caminho → nome de chunk deste relatório são estáticas e reproduzidas da base canônica. Não há patch de mapa/tutorial/menu baseado nestes dados nesta etapa. Até resolver `0xd4`, todas as variantes homônimas e os bounds/hitboxes, os únicos alvos autorizados continuam sendo os patches de cobertura já declarados no manifesto do candidato. O aceite no dispositivo permanece pendente.

Fontes técnicas: `work/candidates/widescreen-app-completion/ghidra-exact-base.log`, `ghidra-map-functions-exact.log`, `native-function-map.json`, `render-route-ledger.json`, `sprite-binding-assets/manifest.json`, `work/candidates/widescreen-app-completion/canonical-base-cpk-inventory.json` e `work/s24-controls/findings.md`.
