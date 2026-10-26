# Composição widescreen: rota que reintroduz 210 px

Análise de 26/10/2026. Foram examinadas as instruções da biblioteca instalada do build de 24/10 (`04b046b7…`) e do candidato UI/toque (`1e72dbed…`). Nenhum APK, fonte funcional ou dado no aparelho foi alterado por esta análise.

## Resultado

Há duas rotas que configuram a composição final. O patch widescreen modifica `nuccSys::SetResolution`, mas deixa `nuccSys::ChangeRender` com proporção fixa **16:9**. Quando a textura interna já tem 2340×1080, essa segunda rota produz destino de 1920×1080 iniciado em X=210; o compositor depois envia uma imagem de largura 2340 a partir desse X.

Essa sequência reproduz a faixa preta esquerda e o corte direito observados, sem precisar supor erro na textura ou na escala dos botões. É um mecanismo comprovado em emulação; ainda falta capturar sua execução no fluxo afetado do aparelho.

## Montagem da tela

O patch faz `AdjustScreenSize` retornar sem reduzir o S24 para 1920×1080. A textura de render pode, portanto, permanecer 2340×1080. Em `SetResolution`, os parâmetros 16/9 já foram substituídos pelas dimensões reais.

`ChangeRender` recria texturas e reconstrói a composição por outra chamada a `SetRenderMode`, sem passar por esse trecho corrigido de `SetResolution`:

```text
ChangeRender:
  SetRenderTexture(largura, altura, ...)
  ...
  SetRenderMode(16, 9, largura_dispositivo, altura_dispositivo, contain, 0, 0)
```

No S24, a chamada mantém uma área central 16:9:

```text
largura central = 1080 × 16/9 = 1920
margem esquerda = (2340 - 1920) / 2 = 210
```

A função `Render` usa os campos do retângulo calculado e o tamanho da textura para montar o descriptor passado a `nummSpriteDraw2D`. Para X:

```text
X_sprite = sys.adjustX + resolution.destX
           + max((resolution.destWidth - resolution.sourceWidth)/2, 0)
```

Os campos relevantes são `nuccSys+0x5f0`, `resolution+0x08`, `resolution+0x10` e `resolution+0x24`. Para destino de largura 1920 e textura de largura 2340, o termo max é zero. Com ajuste manual zero, o sprite começa em **210** e continua com **2340** de largura: sua extensão chega a 2550, ultrapassando em 210 a tela de 2340.

| Etapa emulada | Proporção coerente | Rota 16:9 residual |
|---|---:|---:|
| Textura interna | 2340×1080 | 2340×1080 |
| Área de destino | 2340×1080 | 1920×1080 |
| Origem X de destino | 0 | 210 |
| Largura do sprite final | 2340 | 2340 |
| Origem X do sprite final | 0 | 210 |

## Instruções que faltam no patch

Endereços abaixo são ELF VA; offsets de arquivo são VA menos `0x4000`. Não usar os endereços Ghidra, que têm base adicional de `0x100000`, como offsets de patch.

| ELF VA | Offset de arquivo | Instalado e candidato atual | Substituição proposta |
|---|---|---|---|
| `0x1079910` | `0x1075910` | `01028052`: `mov w1,#16` | `e103142a`: `mov w1,w20` |
| `0x1079914` | `0x1075914` | `22018052`: `mov w2,#9` | `e203042a`: `mov w2,w4` |

Nesse ponto, W20 contém a largura consultada do dispositivo e W4 a altura. A chamada ocorre em `0x1079928`. É o mesmo princípio já aplicado às duas instruções de `SetResolution` em `scripts/patch-widescreen.py`, mas falta esta segunda rota.

O caminho estático confirmado é `nuccSys::MainEnd → ChangeRender → SetRenderMode → Render` na troca de configuração de render. O banco Ghidra mostra a chamada a `ChangeRender` no trecho de `MainEnd` que trata alteração de renderização. Isso não comprova quando a rotina foi executada na captura específica de título/termos.

## Prova emulada das duas instruções

Executamos o tail real de `ChangeRender`, incluindo a preparação de parâmetros e seu branch de chamada; o stub PLT foi redirecionado à função real `SetRenderMode`, seguida de `Render`. A captura observa o descriptor enviado à API de sprites, não um desenho real na GPU.

| Captura de W1..W7 no call | Resultado |
|---|---|
| Antes: `[16,9,2340,1080,1,0,0]` | Destino `[210,0,1920,1080]`; sprite X=210, largura=2340 |
| Depois: `[2340,1080,2340,1080,1,0,0]` | Destino `[0,0,2340,1080]`; sprite X=0, largura=2340 |

As duas instruções propostas foram alteradas **somente na memória do emulador**. Os demais bytes do tail foram conferidos intactos. Foram executados seis cenários de `SetRenderMode` e seis de `Render`, incluindo as duas variantes do tail. Outros cenários distinguem textura estreita de margem manual.

```powershell
python work/widescreen-composition-analysis/emulate_composition.py
```

## Hipótese alternativa verificada

`SetAdjustScreenPos` também soma uma translação na composição. Seus callers examinados inicializam X/Y em zero; a rotina de ajuste manual do menu limita os valores a ±16. Isso não oferece, nesses callers, uma origem normal para +210. Não foram auditadas todas as possíveis escritas diretas nesses campos nem lida sua memória no aparelho.

## Consequência para o próximo ajuste

O APK `Naruto Ultimate Ninja Storm - UI e toque ajustados.apk` **ainda contém a rota 16:9 residual**: `ChangeRender`, `SetRenderMode`, `Render` e o setter de ajuste de posição são idênticos nele e na biblioteca instalada.

A abordagem principal é corrigir a proporção em `ChangeRender`, com guardas de hash/bytes, e validar a composição completa. O primeiro teste deveria usar o build de 24/10 e alterar apenas essa segunda rota, mantendo UI e toque antigos, para separar a falha de composição das experiências posteriores de matriz/toque. Não recomendar nova compensação global de -210 no input antes desse teste.

O relatório de assets anterior e a medição do botão Entrar (+210,33 px com escala preservada) são compatíveis com esse mecanismo. A confirmação final ainda exige observar o fluxo real no S24 e conferir título, termos, Opções e toque após a correção.

## Evidência e limites

Em `work/widescreen-composition-analysis/`: `emulate_composition.py`, `emulation.json`, `changerender.txt`, `setresolution.txt`, `setrendermode.txt`, `render.txt`, `change-render.c.txt`, logs Ghidra e `verified-function-ranges.json`.

As faixas nativas de `ChangeRender`, `SetRenderMode`, `Render` e `SetAdjustScreenPos` foram comparadas byte a byte entre a biblioteca instalada, a fonte do banco Ghidra e o candidato UI/toque. As quatro conferem. O ambiente emulado usa dimensões e memória sintéticas e simula chamadas externas de renderização; não captura estado do processo Android nem comprova aceitação visual.
