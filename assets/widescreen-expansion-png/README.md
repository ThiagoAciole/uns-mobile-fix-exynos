# Imagem confirmada para expansão widescreen

Esta pasta contém somente `opcoes/moption/xoption_battlebg01.png`, fundo da demonstração dos controles associado ao sprite `0x1e7` em `moption.xfbin`. A imagem foi extraída do APK 1.2.10 e mantida nas dimensões originais (1920×1080).

A versão panorâmica pronta está em `opcoes/moption/xoption_battlebg01-widescreen.png` (2342×1080); é uma cópia da arte `background-joystick-widescreen.png` já fornecida na raiz. O importador usa 2340×1080 pixels centrais, sem esticar o conteúdo. Para outras telas, o diagnóstico atual indica correção de geometria/layout e âncoras; não expansão de atlas, HUD, mapa, logo ou painéis sem vínculo confirmado. Os XFBINs-fonte permanecem em `work/widescreen-expansion-source-20261026`.
