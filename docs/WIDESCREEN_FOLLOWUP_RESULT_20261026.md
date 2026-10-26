# Resultado — correção widescreen S24 (26/10/2026)

## Entrega

APK candidato: `build/Naruto Ultimate Ninja Storm - widescreen ajustado.apk`  
SHA-256: `F94B7280D981DE56C2D03979791A31D0EE5DE765C1B5FB3B0EA3F08A311F159E`  
Pacote `com.bandainamcoent.ultimateninjastorm`, versão `1.2.10` / código `38`; assinatura v3 verificada, certificado local igual ao APK funcional e alinhamento de 16 KiB aprovado.

## Ajustes incluídos

1. **Tela de controles:** integrado `background-joystick-widescreen.png` (2342×1080). A textura conserva o arquivo e amostra 2340×1080 pixels centrais, sem redimensionar; quad estendido de `(-140, 0)` a `(1420, 720)`.
2. **Título:** ampliadas quatro malhas de cobertura/transição que atingiam 1280×720. Logo, textos, UVs, materiais e animações não foram alterados.
3. **Filtros e fades:** patch nativo restrito a 2340×1080, cobrindo filtros, fade de tela e centralização. A alteração parte da biblioteca do APK funcional e preserva os bytes da correção de composição/toque já aceita.

## Validação

- Hash da entrada: `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`; hash da biblioteca de entrada: `5E2797280A0D9EAE2CF2D14F0089D6A9585699673A7C872E0D21D61BE6F78071`.
- Assinatura v3 e certificado conferidos contra o APK funcional; alinhamento de 16 KiB conferido após assinatura.
- Os bancos CPK foram inventariados; os dois assets substituídos foram extraídos do APK assinado e seus hashes conferem com os candidatos. Os outros payloads mantiveram CRC e tamanho na reconstrução.
- Autoteste do importador de controles aprovado; testes das camadas do título: 4 aprovados; testes do patch de cobertura: 3 aprovados.
- `audit/frame_001.jpg` a `frame_029.jpg` permanecem presentes. O APK funcional e o original não foram sobrescritos.

## Estado de aceitação

O usuário pediu a instalação depois da montagem. O APK foi aplicado ao Galaxy S24 (SM-S921B) com `adb install --no-incremental -r --user 0`; o ADB retornou `Success`, sem desinstalar nem limpar dados. O sistema confirmou 1.2.10/código 38 e `lastUpdateTime=2026-10-26 10:13:57`.

O jogo abriu e chegou à seleção de modo e à vila. Uma captura de gameplay mostrou HUD e cenário em 2340×1080, sem as faixas de 210 px. Uma captura posterior ficou preta, embora `MainActivity` continuasse em foco; não apareceu fatal ou ANR no trecho de logcat consultado. A causa desse quadro preto não está confirmada.

**Aceitação visual incompleta:** ainda não foram percorridos os diálogos, a tela de controles com o novo fundo e o título parado. Portanto, montagem, assinatura e instalação estão verificadas; ausência de regressões visuais não está homologada. As capturas e seu manifesto estão em `work/candidates/widescreen-followup-20261026-01/`.
