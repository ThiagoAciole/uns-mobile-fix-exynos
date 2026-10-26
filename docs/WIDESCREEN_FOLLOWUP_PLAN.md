# Plano de ajustes visuais widescreen — sem regressão de margem

Revisado em 26/10/2026. Este plano cobre escurecimento/transições, a demonstração de controles e as emendas do título. Não altera o APK funcional até que um candidato independente passe pelas validações.

## Diagnóstico e bloqueios resolvidos no plano

- O APK atual em `build/Naruto Ultimate Ninja Storm.apk` tem SHA-256 `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`, versão 1.2.10 / código 38. Esse é o APK aceito no S24.
- O hash `717A2535...` é a entrada anterior usada para gerar o APK funcional. A correção de composição alterou 8 bytes nativos e removeu a origem X=210 em 2340×1080. Usar `717A...` como base descartaria essa correção e pode reintroduzir a margem.
- A pasta `audit/` foi restaurada e contém `frame_001.jpg` a `frame_029.jpg`. Inspeção visual: `frame_001` mostra a configuração de controles e uma cena concentrada no centro; `005–008` mostram opções/confirmação e mudança de escurecimento; `015–018` mostram a seleção de modo e seu diálogo; `022–025` registram uma transição clara; `026–029` mostram estados do título. Esses pixels são evidência do sintoma, não prova da rota nativa. Preservar a pasta e seus hashes durante a investigação.
- O usuário forneceu `background-joystick-widescreen.png` como arte expandida para a tela de controles. Ela mede **2342×1080**, dois pixels a mais que o canvas S24 de 2340×1080, e tem SHA-256 `AA01B4B6F1865E91A5C6D204A873DFF9331CBD5329C9BE3E27CAABBBB3E1F697`. Foi integrada ao candidato preservando os pixels e amostrando os 2340 pixels centrais.
- O APK atual é protegido: não sobrescrever, remover, desinstalar ou limpar os dados do jogo durante esta tarefa.

### Mapa das referências recuperadas

| Frames | O que se vê | Como usar na investigação |
|---|---|---|
| `001` | Configuração de controles sobre cenário; a cena aparece numa área central e há arte decorativa nas laterais. | Verificar se a câmera/cena pode revelar mais cenário sem escalar personagens nem remover elementos laterais intencionais. |
| `005–008` | Opções com diálogo e estados de escurecimento antes/depois da confirmação. | Comparar área, intensidade e instante do overlay; nuvens claras nas bordas não provam por si só uma falha de viewport. |
| `015–018` | Seleção de modo, diálogo e retorno à tela. | Seguir a transição completa, incluindo o estado com diálogo e a cena depois que ele some. |
| `019–025` | Quadros pretos, espiral, quadro claro e entrada do título. | Tratar preto/branco como possíveis quadros intencionais de transição; conferir sequência e duração antes de chamar de defeito. |
| `026–029` | Título parado e variações de opacidade do texto “Toque para iniciar”. | Procurar mudança de borda/recorte entre estados; não presumir que uma diferença de opacidade seja emenda de textura. |

As observações acima vêm apenas dos JPGs recuperados. A resolução, o estado do APK que os produziu e a relação temporal entre arquivos ainda devem ser registrados antes de usar diferenças de pixels como critério conclusivo.

## Invariante para impedir a margem de 210 px

O candidato parte do APK atual `5DAC...`; não parte de `717A...` nem diretamente de `origin/`. Antes e depois de cada patch, confirmar que a rota `nuccSys::ChangeRender` continua usando largura e altura reais do dispositivo (`w1=w20`, `w2=w4` nas instruções corrigidas em `0x1079910` e `0x1079914`). Não reaplicar nem substituir esse patch durante os ajustes de cenas.

Para as telas que devem ocupar toda a largura, a composição deve usar origem X=0, largura de destino igual à largura do display e altura igual à altura do display. No S24 2340×1080, não pode haver destino 1920×1080 centralizado, origem X=210, corte à direita ou faixa preta involuntária à esquerda. Validar também o mapeamento inverso dos toques com a mesma escala e origem da interface.

Na geometria que realmente use o espaço lógico 1280×720, calcular a largura lógica a partir da proporção, sem coordenada fixa por modelo:

```text
Hlogical = 720
Wlogical = Hlogical × displayWidth / displayHeight
Xleft = 640 − Wlogical / 2
Xright = 640 + Wlogical / 2
```

Isso resulta em `(0, 1280)` em 1920×1080, `(-140, 1420)` em 2340×1080 e aproximadamente `(-213.333, 1493.333)` em 2560×1080. Só usar essa fórmula depois de provar que a cena usa esse espaço lógico e esse centro. Se o engine exigir inteiros, definir arredondamento simétrico e testar as bordas para evitar uma coluna descoberta.

## 1. Fixar e registrar a base

1. Calcular SHA-256 do APK atual e confirmar exatamente `5DAC1302...D2147D86`; conferir pacote, versão, código, certificado e hash da biblioteca ARM64 `5E279728...F78071`.
2. Extrair somente para uma pasta nova de candidato. Registrar hashes da entrada, da biblioteca e dos assets CPK relevantes. Manter a entrada original e o APK atual intactos.
3. Se o hash não corresponder, interromper. Não usar `717A...`, a origem original ou outra cópia como fallback silencioso.
4. Inventariar SHA-256 e dimensões de todos os frames de referência. Criar também capturas-base atuais do APK aceito em 2340×1080, nas mesmas cenas/estados e após as animações estabilizarem. Guardar ambas as séries sem sobrescrever `audit/`.

## 2. Identificar cada rota antes de alterar

Tratar cada sintoma como uma investigação e patch separados. Não mudar coordenadas por semelhança visual.

1. **Escurecimento e transições:** usar a sequência `005–008` e `015–018`. Rastrear `ccDispFilter::Draw`, câmera/projeção, viewport, alpha, profundidade e tempo do fade. Distinguir o escurecimento previsto atrás do diálogo de áreas laterais que deveriam escurecer junto.
2. **Demonstração dos controles:** usar `frame_001` como referência e `background-joystick-widescreen.png` como candidato de arte para as laterais. Rastrear o sprite `0x1e7` e provar se a tela usa uma imagem estática ou uma cena 3D viva. Se for a imagem de fundo dessa tela, testar a substituição/integração dessa camada mantendo o menu e os controles como elementos independentes. A imagem tem 2 px a mais que o S24: não redimensionar; só considerar corte central de 1 px por lado após confirmar que as bordas não contêm conteúdo relevante. Se a cena for renderizada ao vivo, não congelar personagens usando uma captura achatada: manter a imagem apenas como referência/arte das laterais e ampliar o FOV horizontal da câmera, preservando FOV vertical, altura, HUD e proporções.
3. **Emendas e transições do título:** usar `022–025` para a transição clara/flash e `026–029` para o título e a animação de “Toque para iniciar”. Identificar modelo, material, chunk, limites de visibilidade e pass responsáveis. Não presumir que todas as diferenças visíveis sejam emendas da textura; separar borda de viewport, fade, culling e sobreposição antes de alterar.
4. Registrar para cada hipótese a função/callsite, VA/offset, asset e bytes de origem. Se a rota não for confirmada, continuar o rastreamento sem patch.

## 3. Aplicar patches isolados e verificáveis

- Trabalhar em `work/candidates/widescreen-followup/`, sem reutilizar uma pasta de saída existente.
- Criar um patch pequeno por sintoma, com SHA-256 de origem, bytes esperados, intervalos alterados e rejeição de reaplicação. Não tocar em `ChangeRender` nem nos stubs de UI/toque já aceitos, salvo se uma reprodução provar que são a causa do sintoma.
- Para cada cena, calcular limites usando a transformação comprovada. Não aplicar a geometria `(−140, 1420)` globalmente a diálogos, filtros, câmera 3D e título.
- Se um ajuste exigir código novo, comprovar espaço livre, referências e alinhamento; não sobrescrever funções, dados compartilhados ou código executável.
- Atualizar somente a biblioteca e os chunks de assets necessários. Preservar idioma, patch Exynos, controles, manifest, DEX, áudio, vídeos e demais payloads.

## 4. Portões de regressão antes de assinar

1. **Composição:** reproduzir as instruções finais da rota e testar 1920×1080, 2340×1080 e 2560×1080. Exigir origem X=0 e destino `[0,0,W,H]` para cenas full-screen, sem centro fixo 16:9. Testar ambos os extremos e pontos de toque; manter um caso de regressão que detecte os 210 px.
2. **Visual por cena:** comparar capturas-base e candidato na mesma resolução, cena, estado de fade e instante da animação. Medir as bordas e verificar separadamente distorção, corte, emenda e conteúdo que deve permanecer escuro.
3. **Diff binário:** comprovar que cada diff nativo e cada chunk alterado está declarado; confirmar que o patch Exynos e os 8 bytes da composição aceita permanecem intactos. Rejeitar alterações em manifest/DEX e diferenças não explicadas nos demais payloads.
4. **APK:** confirmar pacote, versão 1.2.10/código 38, mesmo certificado local, assinatura v3, alinhamento de 16 KiB e hashes após assinatura. Registrar SHA-256 final e manifesto de construção.

## 5. Aceitação e entrega

- Gerar o candidato como `build/Naruto Ultimate Ninja Storm - widescreen ajustado.apk`, sem substituir `build/Naruto Ultimate Ninja Storm.apk`.
- A montagem e as verificações estáticas não comprovam ausência visual da margem nem regressão zero em jogo. O aceite em aparelho exige abrir o candidato no S24 em paisagem 2340×1080 e repetir as cenas, toques, vila e batalha; até esse teste, rotular como **APK verificado, validação no aparelho pendente**.
- Não instalar sem solicitação explícita, desinstalar, limpar dados, publicar ou substituir o APK funcional. A pedido do usuário, o candidato foi instalado como atualização (`adb install -r`) sem limpar dados; a compatibilidade do save ainda não foi testada separadamente.
- Se qualquer gate falhar, descartar somente o candidato e manter o APK atual intacto. Corrigir a hipótese antes de tentar outro patch.

## Ação inicial do plano — concluída

O hash do APK funcional conferiu como `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`. Os 29 frames de `audit/`, a arte e uma captura somente leitura da tela de seleção de modo no APK atualmente instalado foram registrados em `work/candidates/widescreen-followup-20261026-01/reference-manifest.json`. A captura não substitui as capturas-base das demais cenas, que seguem pendentes para a aceitação visual.

## Execução — 26/10/2026

O candidato foi montado separadamente como `build/Naruto Ultimate Ninja Storm - widescreen ajustado.apk`. O relatório completo, hashes dos bancos, patches e validações está em `build/Naruto Ultimate Ninja Storm - widescreen ajustado.apk.build.json` e no documento `WIDESCREEN_FOLLOWUP_RESULT_20261026.md`.

Foram integrados: fundo expandido da tela de controles, quatro camadas de cobertura do título e patch nativo de filtro/fade com guarda específica para 2340×1080. O patch nativo partiu da biblioteca do APK funcional, preservou os bytes da correção de composição/toque e não altera o APK funcional. Os bancos CPK e os conteúdos substituídos foram relidos do APK assinado e tiveram seus hashes conferidos.

**Estado:** APK assinado e instalado no S24 por atualização; a abertura chegou à seleção de modo e à vila. Uma captura posterior ficou preta com `MainActivity` ainda em foco, sem fatal/ANR no trecho de logcat consultado; a causa não está confirmada. A validação visual dos diálogos, da tela de controles e do título segue pendente. Os frames de `audit/` continuam preservados. O APK funcional anterior e o original não foram substituídos no disco.

Uma captura-base somente leitura da seleção de modo, em 2340×1080, foi guardada junto ao candidato. Capturas após a instalação também foram registradas no manifesto, incluindo splash, seleção de modo e um quadro preto posterior; elas não cobrem os diálogos, os controles ou o título parado.
