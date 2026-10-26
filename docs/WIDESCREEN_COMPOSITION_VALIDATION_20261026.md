# Validação da correção widescreen — 26/10/2026

## Resultado

O APK corrigido foi instalado no Galaxy S24 (SM-S921B). Após abrir o jogo, o usuário confirmou que a margem lateral de 210 px e o desalinhamento dos toques foram corrigidos.

## Artefato

- APK: `build/Naruto Ultimate Ninja Storm.apk`
- Pacote: `com.bandainamcoent.ultimateninjastorm`
- Versão: `1.2.10`, `versionCode 38`
- Tamanho: `3.647.964.116` bytes
- SHA-256 do APK: `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`
- SHA-256 da biblioteca ARM64: `5E2797280A0D9EAE2CF2D14F0089D6A9585699673A7C872E0D21D61BE6F78071`

A instalação foi feita com `adb install --no-incremental -r --user 0`. A versão e o hash do APK instalado foram consultados no aparelho e correspondem ao artefato acima. Não houve desinstalação nem limpeza de dados.

## Correção

Na rota `nuccSys::ChangeRender`, o APK anterior mantinha a proporção fixa 16:9 mesmo quando o S24 renderizava em 2340×1080. Isso gerava um destino de 1920×1080, com origem X=210; a imagem de 2340 px era desenhada a partir dessa origem e ultrapassava a borda oposta.

A build corrigida substitui duas instruções ARM64 para passar a largura e a altura reais do dispositivo ao `SetRenderMode`:

| ELF VA | Antes | Depois |
|---|---|---|
| `0x1079910` | `mov w1,#16` | `mov w1,w20` |
| `0x1079914` | `mov w2,#9` | `mov w2,w4` |

A emulação do trecho de composição passa o início do sprite de X=210 para X=0. A mudança do retângulo de composição também deixa o toque alinhado com a área visível; os stubs de UI/toque foram preservados nesta build. O patch modificou 8 bytes da biblioteca nativa; os demais payloads do APK foram verificados como preservados no relatório de build.

## Evidências e limites

- Assinatura APK v3, alinhamento de 16 KiB, pacote/versão e integridade dos payloads constam em `work/s24-composition/build-report.json` e `work/s24-composition/payload-validation.json`.
- O hash do APK instalado no S24 foi `5dac1302663cbec6abc678b7f9c84976c2a2a1fea487f183febd2d42d2147d86`; o hash da biblioteca instalada foi `5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071`.
- A correção e o toque foram aceitos pelo usuário no S24, em 2340×1080. Não foi criada captura nova nesta etapa; o aceite visual é o relato do usuário.
- A validação não cobre outras proporções, orientação retrato, todos os diálogos ou batalhas.
