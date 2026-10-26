# Análise do APK disponível

Data da inspeção: 2026-10-24.

## Artefato

- Arquivo: `naruto-ultimate-ninja-storm-mod_129_working_1791703630.apk`
- SHA-256: `9E020B5ACA39D786E4EBFD9A9485DD4A33FE7C6A41CA66C9AEF75E425C11473D`
- Package: `com.bandainamcoent.ultimateninjastorm`
- Versão: `1.2.9` (`versionCode 37`)
- `minSdkVersion`: 28; `targetSdkVersion`: 35; compilado com SDK 35
- ABI: `arm64-v8a`; contém `libc++_shared.so` e `libultimateninjastorm.so`
- O APK inclui os dados do jogo em `assets/data`; não há arquivo OBB nem outro APK/split no workspace.
- Assinatura APK v3 válida, feita com certificado `CN=Debug` (SHA-256 `a052076edcc6adc9368b9428afaeaf630fd670fb15fdc7ca62c338d7afa7d8bd`). Isso identifica o arquivo disponível como artefato assinado com chave de desenvolvimento; não comprova procedência oficial.

## Diagnóstico

Não foi possível atribuir a este APK o crash Vulkan descrito numa investigação anterior: o SHA-256 do `libultimateninjastorm.so` atual é `ADC77A5A80CEF5AE694CEE9898488DF19FCB835AC4E847FBED9258069A905DEC`, diferente do binário daquela análise. Os logs e arquivos da análise anterior também não estão presentes no workspace atual.

O ADB iniciou, mas `adb devices -l` não listou aparelho conectado. Assim, não há logcat atual, propriedades do dispositivo nesta sessão, nem captura da primeira operação Vulkan que falha para este binário. Não há causa comprovada para justificar patch de manifesto, Smali ou código nativo.
