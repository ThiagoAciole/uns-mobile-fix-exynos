# APK com ajuste de composição — 26/10/2026

Saída: `build/Naruto Ultimate Ninja Storm - composicao widescreen ajustada.apk`.

## O que está incluído

O APK usa a base exata do último build de 24/10, SHA-256 `717a253525f03e3f5d7fe308f7c3bdddc1927b9a97b01bf5c0fbabb4375a2b3d`. A biblioteca nativa recebe somente estas duas substituições em `nuccSys::ChangeRender`:

| ELF VA | Antes | Depois |
|---|---|---|
| `0x1079910` | `mov w1,#16` | `mov w1,w20` — largura real |
| `0x1079914` | `mov w2,#9` | `mov w2,w4` — altura real |

Isso impede que a troca de configuração recrie um destino 16:9 enquanto a textura do jogo já ocupa 2340×1080. Na emulação do código ARM64, a origem do sprite final muda de X=210 para X=0, mantendo largura 2340 e altura 1080.

A biblioteca resultante tem SHA-256 `5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071`. Todos os bytes fora dessas duas instruções são idênticos aos da biblioteca de 24/10. Os stubs de UI/toque antigos foram preservados; este APK não incorpora as alterações de `ui_uniform`/`input_inverse` do candidato anterior, nem seus experimentos de título/controle/filtro.

Os dois bancos de UI, Manifest e DEX permanecem idênticos aos da base. Áudio/vídeo têm os mesmos payloads preservados; o repack recalcula seus CRCs ZIP antigos inconsistentes. A base original e sua cópia restaurada continuam preservadas.

## Construção e validação

O patch incremental está em `scripts/patch-widescreen-composition.py`, com guarda do SHA-256 completo da biblioteca e dos bytes anteriores, recusa de reaplicação e saídas novas. O construtor completo `scripts/patch-widescreen.py` também recebeu essas duas substituições para não voltar a omitir essa rota em gerações futuras; o APK desta entrega usa o patch incremental sobre a base de 24/10.

```powershell
python scripts/test-widescreen-composition.py
python scripts/patch-widescreen-composition.py work/restore-20261024/transform-audit/installed.so work/s24-composition/patched/libultimateninjastorm.so
```

Os três testes verificam preservação dos bytes fora do intervalo, recusa de fonte errada/reaplicação e execução do tail efetivamente modificado, seguido do cálculo do destino e da composição final. O construtor completo também passou em `--check-only`.

O hash final do APK e o resultado das verificações de assinatura V3, certificado, alinhamento de 16 KiB, metadados, ZIP e payloads estão em `work/s24-composition/build-report.json` e no sidecar `.sha256` do APK. A exclusão do candidato anterior de UI/toque, autorizada pelo usuário, deve ser conferida em `retired-previous-apk.json` na mesma pasta; seus relatórios são preservados.

## Instalação e aceite posterior — 26/10/2026

O candidato foi instalado no Galaxy S24 (SM-S921B) por atualização ADB, sem desinstalar o app nem limpar dados. O pacote instalado foi confirmado como `com.bandainamcoent.ultimateninjastorm`, versão 1.2.10 / código 38. O SHA-256 do `base.apk` no aparelho corresponde ao candidato: `5dac1302663cbec6abc678b7f9c84976c2a2a1fea487f183febd2d42d2147d86`; o SHA-256 da biblioteca ARM64 instalada é `5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071`.

Depois de abrir o jogo, o usuário confirmou que a margem de 210 px e o desalinhamento dos toques foram corrigidos. A alteração funcional desta build limita-se às duas instruções de `ChangeRender` da tabela acima; a instalação alinha a composição com as dimensões reais e mantém os stubs de UI/toque anteriores. Nenhuma captura nova foi coletada pelo agente.

O aceite corresponde ao S24 em paisagem, 2340×1080. Não estende a validação a outras proporções, a todos os diálogos ou a batalhas.