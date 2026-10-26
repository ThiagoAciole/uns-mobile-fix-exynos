# Validação

## Concluída nesta sessão

- Hash SHA-256 do APK de entrada calculado.
- Cópia em `original/` criada e verificada com o mesmo SHA-256: `9E020B5ACA39D786E4EBFD9A9485DD4A33FE7C6A41CA66C9AEF75E425C11473D`.
- `aapt dump badging` identificou package, versão, SDKs e ABI.
- `apksigner verify --verbose --print-certs` validou a assinatura v3 e identificou certificado de desenvolvimento.
- Inventário ZIP confirmou dados embutidos, duas bibliotecas nativas e ausência de OBB/split separado no workspace.

## Pendente

- Capturar logcat do APK atual no Galaxy S24 e identificar a primeira falha gráfica.
- Aplicar uma correção baseada nessa evidência, reconstruir, alinhar e assinar o APK de teste.
- Instalar e validar menus, carregamento de fase e gameplay no aparelho.

`adb devices -l` não encontrou dispositivo nesta sessão. Nenhum APK corrigido foi produzido e não há validação de runtime.
