# Especificação de layout widescreen — Naruto Storm 1.2.10

Status: **plano de implementação**, baseado no APK principal `5DAC1302…D2147D86`, na referência visual enviada e no inventário/rotas disponíveis em 26/10/2026. Não significa que todas as telas já foram corrigidas ou aceitas no aparelho.

## Modelo de coordenadas para o Galaxy S24

Resolução de referência: `2340×1080`; área lógica original: `1280×720`.

```text
escala uniforme = 1080 / 720 = 1,5
largura lógica efetiva = 2340 / 1,5 = 1560
extensão horizontal = (1560 - 1280) / 2 = 140 por lado
canvas widescreen = X [-140, 1420], Y [0, 720]
tela = (1170 + 1,5 × (X - 640), 1,5 × Y)
```

O retângulo lógico original `[0,1280]` permanece central e ocupa `[210,2130]` pixels. A cena 3D usa toda a viewport com expansão horizontal de câmera. Camadas de cobertura usam o canvas `[−140,1420]`. A interface não deve ser esticada para preencher a tela.

### Âncoras a aplicar por elemento

| Âncora | Regra no espaço lógico | Uso esperado |
|---|---|---|
| Esquerda | Fixar distância até `X=-140`; acrescentar `−140` às posições desenhadas originalmente em `X=0`. | HUD, instruções, menus laterais e painel de tutorial quando a referência os encosta à esquerda. |
| Centro | Preservar centro em `X=640`; diálogo central mantém escala e proporção. | Personagem/crosshair, avisos, modais, botões de confirmação e conteúdo principal. |
| Direita | Fixar distância até `X=1420`; acrescentar `+140` às posições originalmente ancoradas em `X=1280`. | Minimap, contadores, HUD e ações do lado direito. |
| Inferior/superior | Preservar distância em relação a `Y=0` ou `Y=720`; verificar recortes e insets reais do Android. | Barras, legenda, navegação e textos persistentes. |
| Cobertura total | Expandir somente bounds de quad/camada para `[-140,1420]×[0,720]`; manter UV, proporção, alpha e timing quando aplicável. | Fundo, escurecimento, fade e panorama comprovadamente próprios da tela. |

O inverse touch deve converter display → logical pelo mesmo viewport/escala e atingir o hitbox lógico do controle já reposicionado. Não se desloca um controle visual sem medir e deslocar/verificar seu hitbox. UI original no centro continua no mesmo lugar; somente elementos com âncora lateral mudam.

## Mapa de tratamento por fluxo

| Fluxo (IDs do ledger) | Cena/fundo | UI e layout | Entrada e aceite que falta |
|---|---|---|---|
| `boot-logo`, `title` | Vídeo conforme aspecto original; fundo animado pode usar cover só com UV/rota confirmados. Logo mantém proporção. Quatro geometrias de cobertura do título são candidatas. | Logo central; comandos e opções ancorados após ligar sprite/material. | Capturar abertura, título parado/animação e transições; confirmar fade, skip e toque. |
| `mode-select` | Fundo cobre o canvas sem deformar cards. | Cards/textos centralizados; decisões laterais dependem do XFBIN e foco. | Mapear cada modo/diálogo, hitboxes e texto pt-BR. |
| `login` | Sem modificação visual presumida. | Tela possivelmente dependente de serviço externo; manter segura e sem credenciais. | Identificar se alcançável/offline e mapear somente após abrir em estado legítimo. |
| `options-menu` | Fundo específico por tela; atlas compartilhado não é redimensionado. | Cabeçalho e lista centralizados; navegação e scroll devem coincidir com bounds. | Percorrer controle, som, câmera, idioma e gráficos; validar estados/scroll/toque. |
| `controls-demo` | Único panorama de expansão confirmado: `moption.xfbin#xoption_battlebg01`, sprite `0x1e7`. Fundo expandido por canvas/UV, sem esticar personagens. | Painel de configuração mantém proporção e fica sobre o cenário. | Abrir tela no build atual; comparar cenário, controles desenhados e hitboxes. |
| `village-gameplay` | Hor+ em viewport `[0,2340]`; preservar escala vertical, centro/personagem e profundidade. | HUD esquerdo, objetivo/tutorial à esquerda; minimapa no canto superior direito; botões no lado inferior direito. | Validar caminhada/câmera, margens, minimapa e cada botão físico/touch. |
| `village-map` | Mapa mantém proporção e escala própria. | Mini/full map e marcadores em âncoras próprias; não usar a geometria do HUD genérico. | Ligar chunks, bounds, marcadores e hitboxes ao `ccDispStageMap::Draw`. |
| `tutorial-dialogs` | Painel só vira 9-slice/expansível quando UV e usuários compartilhados forem confirmados. | Janela/conteúdo central; prompt de gameplay mantém a posição da referência e não invade HUD. | Resolver tutorial ID → imagem/mensagem/sprite; confirmar confirmar/fechar/toque. |
| `mission-menu` | Fundo e faixa podem cobrir tela; lista e conteúdo não são esticados. | Lista/menu permanece na área principal; estatísticas e salvar ancorados à direita; título/faixa ao topo. | Resolver bounds em `xadv_startmain`/`xadv_mission_menu`; testar todos os itens e retorno. |
| `items-shop` | Janelas e listas preservam proporção; painel só expande via 9-slice comprovado. | Lista/seleção central, detalhes/preço à direita e navegação em posições reproduzíveis. | Mapear subfluxos, paginação/scroll, compra/confirmar/cancelar e hitboxes. |
| `minigames` | Cada atividade mantém sua própria cena e aspecto; nada de cover global presumido. | Instruções, timer e alvos mapeados por minigame. | Identificar formatos ainda não decodificados e testar input temporal/gestos. |
| `free-battle-select` | Preview 3D Hor+ se confirmado; cards e artes ficam proporcionais. | Seleção/filtros/paginação mantêm centro; confirmação e retorno com bounds próprios. | Traçar estados de personagem/suporte e testar todas as hitboxes. |
| `combat-hud` | Arena e câmera 3D usam viewport total; sem escala não uniforme nos lutadores. | Barras/ícones nos cantos; prompt/subtítulos centralizados sem colisão. | Batalha em movimento, HUD dinâmico, especiais, subtítulos e fim de round. |
| `battle-menu-result` | Fundo/filtro fullscreen; painel de resultado/menu não ganha UVs de forma especulativa. | Menu e resultado centrados; HUD/botões de borda respeitam suas âncoras. | Abrir pausa, retomar, sair, navegar resultado e testar toque. |
| `fade-modal` | Expandir o quad de filtro até as duas bordas somente nos estados em que ele cobre a tela; alpha/timing/depth inalterados. | Modal mantém tamanho e centro; toque atrás do modal bloqueado como no original. | Comparar sequências antes/durante/depois para separar fade intencional de resíduo. |
| `movies` | Cada stream usa contain/crop proporcional conforme a fonte; barras podem ser intencionais. | Legenda e skip em safe area, com idioma e toque conferidos. | Capturar dimensões/UV/shader e validar fonte 16:9 no S24. |
| `credits` | Rolagem/arte preserva proporção; decisão de recorte é por stream. | Texto central e largura de leitura segura; skip corretamente posicionado. | Traçar evento ativo, idioma, velocidade e caminho de saída. |
| `touch-cross-screen` | Transformação comum do render só é válida para camadas que compartilham a mesma câmera. | Bounds e hitboxes são inventariados por controle e tela; gamepad mapeado em separado. | Centro/cantos, bordas dos botões, arrasto, duplo toque, multitouch/cancel e gamepad. |
| `ptbr-layout` | Letreiros existentes não mudam de canvas sem necessidade comprovada. | Conferir textos longos, acentos, quebra, nomes dinâmicos e estados desabilitados em cada fluxo. | Varredura visual completa, priorizando batalha, tutorial, loja e vídeo. |

## Ordem de execução e bloqueios

1. **Base e inventário:** APK `5DAC…` fixado localmente; verificar estado instalado quando ADB voltar. Completar rotas de entrada/saída e segurança de save sem alterar dados.
2. **Núcleo de render/UI/toque:** preservar o `ChangeRender` aceito; provar a câmera de cada modo 3D; comparar a transformação global com a fórmula acima. Tratar discrepância no stub de UI antes de reutilizá-lo: `patches/widescreen/stubs.S` hoje define `ui_uniform` com `fneg s6,s0`, enquanto o APK-base em `0x9b12dc` usa `−640×escala`; a diferença muda a origem global. Não trocar esse comportamento sem comprovar a composição e o inverse touch completos.
3. **Rotas por grupos:** (a) gameplay/mapa/tutorial/aventura; (b) opções e seleção; (c) batalha; (d) título/fades/vídeos/créditos. Para cada grupo, completar state → draw route → asset/chunk/UV/bounds → anchor → hitbox → captura.
4. **Arte:** manter `xoption_battlebg01` como única expansão raster confirmada. Título, filtros e faixas podem receber ajustes geométricos se o estado e a superfície forem comprovados. Mapas, ícones, logo e atlas compartilhados não são alvos de esticar.
5. **Montagem/aceite:** montar candidato assinado novo a partir do APK canônico; verificar hashes, lista allowlist, tradução, Exynos, assinatura/alinhamento; atualizar por cima no S24 sem apagar dados; executar a caminhada dos 20 fluxos e registrar cada bloqueio.

## Evidência atual e limite

- Base estática: pacote 1.2.10/code 38, certificado local e SHA da biblioteca registrados em `work/candidates/widescreen-app-completion/base-manifest.json`.
- 20 fluxos cadastrados; 11 rotas compartilhadas identificadas. A maioria das associações exatas de sprites, limites e hitboxes ainda não está resolvida.
- O APK principal tem aceite do usuário para a margem de composição e toque observados no S24; capturas não comprovam a tela atual nem todos os fluxos.
- Sem dispositivo ADB conectado no levantamento. O aceite de candidate-02 é histórico e parcial.
- Este plano define decisão visual e sequência técnica; “app completo” permanece pendente até cobertura do ledger e aceite visual/toque, sem inferir aprovação por build estático.

Referências: [`WIDESCREEN_ASSET_MAP.md`](WIDESCREEN_ASSET_MAP.md), [`superpowers/plans/2026-10-26-naruto-storm-widescreen-app-completion.md`](superpowers/plans/2026-10-26-naruto-storm-widescreen-app-completion.md), e os ledgers em `work/candidates/widescreen-app-completion/`.
