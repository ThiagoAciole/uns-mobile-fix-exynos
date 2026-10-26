# Português e widescreen — APK único 1.2.10

> **Build atual:** `build/Naruto Ultimate Ninja Storm.apk` (SHA-256 `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`). A instalação e o aceite do S24 estão em [WIDESCREEN_COMPOSITION_VALIDATION_20261026.md](WIDESCREEN_COMPOSITION_VALIDATION_20261026.md). Os caminhos e resultados de APKs anteriores abaixo são registros históricos.

Base: `origin/Ultimate-Ninja-Storm-1.2.10.apk`, versionCode 38. A entrada original é preservada. A correção de composição instalada e aceita em 26/10 está registrada em [WIDESCREEN_COMPOSITION_VALIDATION_20261026.md](WIDESCREEN_COMPOSITION_VALIDATION_20261026.md).

## Tradução

Os catálogos em `patches/ptbr/catalogs/` cobrem os 7.104 textos únicos não vazios encontrados em três arquivos ingleses: mensagens/interface/diálogos, mensagens de batalha e itens. São 13.209 campos catalogados, incluindo repetições, nomes próprios e campos vazios. A tradução modifica 7.843 campos em `message.bin`, 442 em `message_btl.bin` e 679 em `itemtext.bin`.

O português ocupa o idioma **English** do jogo. Nesse idioma, seu nome passa a **Português (Brasil)**. Em outro idioma, selecione English/英語, saia das Opções e confirme o retorno à tela de título para aplicar a mudança. Apenas passar as setas não recarrega os textos.

IDs, campos de voz, cabeçalhos e chunks não textuais são preservados. O editor valida a origem por SHA-256, variáveis printf, ícones e controles de cor; remonta offsets/tamanhos e relê o resultado. Cinco títulos de tutorial entre sinais `<...>` são texto visível e recebem equivalentes em português. A fonte nativa tem fallback para os acentos portugueses; não houve remoção de acentos nem substituição da fonte.

**Limite:** a dublagem, logotipos e artes fora dos elementos listados nesta documentação permanecem no idioma original. A tradução cobre os catálogos e os letreiros gráficos identificados para esta atualização.

## Letreiros gráficos

Foram traduzidos os letreiros em `xmode_fd_*`, o início do jogo (`xtitle_fd01`), o cabeçalho `Mode Select` e os atlas Android e padrão da tela de opções. O atlas Android foi aplicado também à cópia usada pelo menu ativo (`data/interface/option/eng/ANDROID/moption.xfbin`), além dos arquivos em `data/interface/index/eng/`. As imagens mantêm as dimensões dos canvases; os XFBINs preservam modelos, materiais, UVs e demais chunks. A amostra pequena de cor usada pelos modelos de modo foi mantida pixel a pixel. As áreas de toque não foram alteradas.

| Inglês | Português (Brasil) |
|---|---|
| Ultimate Mission Mode | Modo Missão Suprema |
| Free Battle Mode | Modo Batalha Livre |
| Options Mode | Modo de Opções |
| Tap to Start | Toque para iniciar |
| Mode Select | Seleção de Modo |
| Options | Opções |
| Control Settings | Configurações de Controle |
| Sound Settings | Configurações de Som |
| Camera Settings | Configurações de Câmera |
| Language Settings | Configurações de Idioma |
| Graphics Settings | Configurações Gráficas |

Os atlas de texturas comprimidos foram reimportados no formato ARGB8, preservando canvas, mip count, chunks adjacentes e UVs. Os três grandes letreiros de modo já eram ARGB8 e mantiveram o formato.

O cabeçalho “Options” também foi traduzido na cópia ativa do atlas Android, `data/interface/option/eng/ANDROID/moption.xfbin`, dentro de `assets/data/sim/installTime.awb`. A atualização desta cópia e do atlas padrão está incluída no APK final abaixo. A instalação atualizou a versão existente sem desinstalar nem limpar dados.

## Widescreen

`scripts/patch-widescreen.py` atua somente sobre a biblioteca principal 1.2.10 já corrigida para Exynos, com guardas de hash/Build ID/bytes e saída separada. Preserva o patch de depth/stencil.

- Mantém as dimensões reais de renderização em vez de limitar o S24 a 1920×1080.
- Compõe a imagem usando o tamanho real da tela e remove o desenho decorativo das faixas.
- Ajusta a perspectiva para ampliar o campo horizontal preservando o vertical.
- Mantém escala uniforme na matriz de interface e faz a conversão inversa do toque correspondente.
- Usa 140 bytes de código no corpo desativado de `DrawLetterBox`; análise de referências não encontrou entradas externas nesse intervalo.

O título tem um ajuste adicional em `scripts/patch-title-bg-s24.py`: amplia somente os quatro vértices X do plano dourado de ±640 para ±780 e seus limites de visibilidade. Logo, textura, UVs, animações e demais chunks permanecem idênticos. O modelo é identificado por nome, hash, layout e ligação de material; uma segunda aplicação é recusada. A largura é fixa para 19,5:9, sem ampliar o logo ou a interface.

O candidato é destinado ao S24 em paisagem, 2340×1080 (19,5:9). Outras proporções e orientação retrato não são homologadas.

## Construção

Com Python e as ferramentas Android já usadas neste projeto:

```powershell
python scripts/patch-widescreen.py
python scripts/build-ptbr-assets.py "CAMINHO/Ultimate-Ninja-Storm-1.2.10.apk" work/ptbr-build
python scripts/repack-native-apk.py "CAMINHO/Ultimate-Ninja-Storm-1.2.10.apk" work/widescreen/patched/libultimateninjastorm.so work/ptbr-build/unsigned.apk --replacements work/ptbr-build/apk-plan.json
```

As saídas precisam ser novas. O patch widescreen espera a cópia Exynos em `work/external-single-1.2.10/patched/`, produzida pelo procedimento da base principal. A assinatura usa o mesmo certificado local, com senha por arquivo; não publique a chave ou a senha. Após assinar, confira `apksigner verify` e `zipalign -c -P 16 4`. Instale por `adb install --no-incremental -r --user 0`, sem desinstalar ou limpar dados.

O construtor de assets também aplica o ajuste dourado do título. O repacker CPK acrescenta os quatro arquivos descompactados, atualiza somente TOC e tamanho de conteúdo e compara todos os bytes originais fora dos dois pacotes de metadados. O repacker APK verifica os hashes dos arquivos substituídos e CRC/tamanho de todos os demais membros. Manifest e DEX não são alterados.

## Evidência atual

A prévia parcial foi assinada com v3, alinhada em 16 KiB e instalada no S24 por atualização com resultado `Success`. A vila 3D e menus renderizaram em 2340×1080 sem as faixas decorativas; botões circulares permaneceram redondos. A alteração de idioma foi confirmada: apareceram Entrar, Criar backup, Carregar backup e Fechar.

Capturas em `work/captures/`: `wide-preview-title` contém gameplay na vila, `wide-preview-menu` contém configurações, `wide-preview-language-apply` documenta a confirmação necessária e `wide-preview-ptbr-loaded` mostra português carregado. O nome do diretório não muda o conteúdo observado.

A captura da tela de título revelou que o fundo dourado ainda ocupava apenas a área central, com preto além dele. O ajuste separado da geometria foi aplicado ao novo candidato e validado por reparse/readback, com somente 12 bytes efetivamente diferentes no asset. A versão completa dos catálogos e esse ajuste não são automaticamente validados pelo teste da prévia. Batalha, todos os diálogos, quebra de linhas e proporção dos vídeos ainda precisam de teste específico.

## APK completo instalado

APK final com os catálogos e letreiros gráficos:

`C:\Users\Thiago Aciole\Projetos\Jogos\Naruto Ultimate Ninja Storm\build\Naruto Ultimate Ninja Storm.apk` — 3.647.964.116 bytes, SHA-256 `717A253525F03E3F5D7FE308F7C3BDDDC1927B9A97B01BF5C0FBABB4375A2B3D`. Assinatura v3 verificada e alinhamento de 16 KiB conferido. O repacker validou 572 membros, SHA-256 da biblioteca nativa e CRCs dos demais payloads.

Instalação por atualização no S24 concluída com `Success`; o package manager confirmou versão 1.2.10 / código 38, atualizada em 24/10/2026 às 23:19:25. Nenhuma desinstalação ou limpeza de dados foi executada. A tela de opções foi aberta após a atualização: o cabeçalho “OPÇÕES” e as cinco categorias aparecem em português. A captura confirma proporção 2340×1080, sem faixas laterais. Evidência: `work/captures/ptbr-graphics-20261024-device-ready.png`.

Esse candidato foi substituído pela composição widescreen corrigida registrada no topo desta página.

Instalação por atualização concluída com `Success`; package manager confirmou 1.2.10 / código 38, atualização em 24/10/2026 às 20:54:04. Nenhuma desinstalação ou limpeza de dados foi executada. O português persistiu após reabrir o app. A tela final mostrou “Ajuste as configurações do jogo.” e “Voltar à tela de título?”, com acentos corretos, e os toques em Voltar/Sim acionaram as ações desenhadas. Capturas: `wide-final-boot`, `wide-final-title` e `wide-final-title-sequence`.

A sequência de retorno ao título mostrou o fundo preenchendo as laterais após a correção. O jogo avançou à escolha de modo durante a captura, portanto não há aceitação visual prolongada do logo parado. O APK atualizado inclui a tradução dos letreiros artísticos listados nesta documentação.
