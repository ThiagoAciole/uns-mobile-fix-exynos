# Patch Exynos — versões 1.2.9 e 1.2.10

> Estado em 26/10/2026: o APK original único 1.2.10 e o APK final combinado são os artefatos ativos. Os binários antigos da 1.2.9 e das análises anteriores foram removidos; esta documentação preserva o registro técnico histórico. As seções abaixo preservam o registro técnico histórico.

Registro consolidado em **24/10/2026**. Os comandos desta página usam PowerShell na raiz:

O APK único 1.2.10 recebido posteriormente tem um [relatório próprio](APK_UNICO_1_2_10.md). Os resultados de dispositivo da 1.2.10 descritos aqui são do conjunto de cinco splits.

O **APK único 1.2.10 é a base principal**, por decisão do usuário em 24/10/2026. Os comandos e evidências de 1.2.9 e dos splits abaixo permanecem como histórico e reprodução dos respectivos artefatos.

```powershell
Set-Location 'C:\Users\Thiago Aciole\Projetos\Jogos\naruto-storm-1'
```

## 1. Resultado e nível de evidência

| Item | 1.2.9 | 1.2.10 |
|---|---|---|
| Identificação | `versionCode=37`, `minSdk=28`, `targetSdk=35` | `versionCode=38`, `minSdk=28`, `targetSdk=36` |
| Pacote | `com.bandainamcoent.ultimateninjastorm` | Mesmo pacote |
| Entrada | APK único de 3.471.342.213 bytes, com certificado Debug | Base e quatro splits extraídos do aparelho |
| Patch nativo | Aplicado em cópia; reversão conferida por SHA-256 | Aplicado em cópia; reversão conferida por SHA-256 |
| Empacotamento | APK único, assinatura v3 e alinhamento de 16 KiB verificados | Cinco APKs assinados com o mesmo certificado, alinhamento e manifests verificados |
| Instalação no S24 | ADB retornou `Success`; versão 1.2.9 e `installed=true` confirmados no perfil pessoal | Conjunto instalado com sucesso durante a investigação |
| Abertura | Usuário informou **“Deu Certo!”** após a instalação; o alcance desse relato não foi detalhado | Abertura, vídeo e título observados em duas execuções, sem novo crash nativo naquela sessão |
| Menu / batalha | Não confirmados especificamente | Não validados; fluxo bloqueado pelo Play Games |
| Autenticação | Integração preservada; resultado da 1.2.9 não foi confirmado | OAuth recusou o certificado local com `DEVELOPER_ERROR` |

O relato do usuário sobre a 1.2.9 não foi convertido em comprovação de batalha, câmera, HUD ou estabilidade prolongada. A evidência detalhada de abertura capturada pelo agente pertence à **1.2.10**.

## 2. Ambiente e ferramentas utilizados

| Área | Ferramentas / ambiente |
|---|---|
| Host | Windows, PowerShell, Python 3.13 e JDK 25 |
| Dispositivo | Galaxy S24 SM-S921B, Exynos 2400, Xclipse 940, tela 2340 × 1080; Android 17 / SDK 37 observado na sessão |
| Android | ADB, build-tools 36.0.0 (`aapt`, `zipalign`, `apksigner`), SDK e NDK 27.2.12479018 |
| Java / recursos | Apktool 3.0.3 e JADX 1.5.6 |
| Código nativo | LLVM do NDK, Ghidra 12.2 local, REA para operações suportadas e capturas ADB |

O provider Ghidra integrado ao REA não aceitou ELF ARM64 neste Windows. A investigação nativa continuou com Ghidra headless local e LLVM. A autoanálise Ghidra ficou parcial; os pontos críticos foram conferidos com assembly dirigido. Não há requisito de repetir uma autoanálise completa para aplicar os perfis já verificados.

## 3. Diagnóstico compartilhado

### 3.1 Crash final observado na 1.2.10

O abort registrado terminava em:

```text
InitializeRenderSystem
  → Finalize do dispositivo / render manager
  → mmThread_Impl::WaitForEnd
  → pthread_join
  → SIGABRT: invalid pthread_t 0x2e79616c702e6469
```

O assembly confirmou que o campo `pthread_t` não é inicializado pelo construtor de `mmThread_Impl`, que `Start()` ignora o retorno de `pthread_create` e que `WaitForEnd()` chama `pthread_join` sem validar o handle. O render manager aguarda as duas threads no cleanup mesmo quando a inicialização falha antes de iniciá-las.

Isso identifica um defeito de cleanup. O patch entregue **não altera esse código**: a investigação procurou a operação gráfica anterior ao abort.

### 3.2 Reprodução da chamada gráfica problemática

O engine solicita o formato interno `mmDataFormat=15`, mapeado originalmente para Vulkan 129 (`D24_UNORM_S8_UINT`). Na Xclipse 940, a consulta desse formato reportou `optimalTilingFeatures=0`.

O engine calcula o tiling a partir do bit `SAMPLED_IMAGE` dos features:

```text
tiling = 1 & ~optimalTilingFeatures
```

Para o formato 129, isso escolhe `VK_IMAGE_TILING_LINEAR`. O tipo de uso 2 fornece `0x3`; o caminho acrescenta `0x20` de depth/stencil e `0x4` de sampled, resultando em `usage=0x27`.

| Teste no probe independente do S24 | Resultado |
|---|---|
| Instância, superfície, dispositivo e swapchain com os parâmetros conhecidos do jogo | `VK_SUCCESS` |
| Formato 129, tiling optimal e `usage=0x20` — controle inicial | Criação, memória e bind passaram; não reproduzia os parâmetros do engine |
| Formato 129, tiling linear, `usage=0x27`, 2340 × 1080 | `vkCreateImage = -3`, `VK_ERROR_INITIALIZATION_FAILED` |
| Formato 130, tiling escolhido pelo mesmo critério, `usage=0x27` | Imagem, memória, bind, image view, render pass e framebuffer depth-only passaram |
| Formato 126 (`D32_SFLOAT`) | Também passou no probe, mas não preserva stencil |

O formato 130 foi escolhido por manter **depth e stencil**. A reprodução é de uma chamada equivalente deduzida do ELF; o primeiro `VkResult` não foi interceptado dentro do processo original. A abertura da 1.2.10 após o patch acrescentou evidência de que a alteração supera o crash inicial.

Os avisos `GPU do not support native format(3)` e `PAL: Invalid format 0` também apareceram em testes de swapchain que retornaram sucesso. Eles não foram usados isoladamente como prova da falha.

## 4. Alteração binária por versão

Biblioteca: `lib/arm64-v8a/libultimateninjastorm.so`, ELF64 AArch64 little-endian.

| Campo | 1.2.9 | 1.2.10 |
|---|---|---|
| Build ID | `d6c3c1ca40aa936ceb5b585da96f4a4a` | `c3e506f9be350dfb4a00c79228754028` |
| Base da tabela de formatos no ELF | `0x6c6128` | `0x6bf928` |
| Offset de arquivo alterado, entrada 15 | **`0x6c6164`** | **`0x6bf964`** |
| `GetImageDataFormat(mmDataFormat)` | `0x917090` | `0x910890` |
| Instrução que fornece formato 15 ao depth buffer | `0xd18a3c` | `0xd1223c` |
| Instrução `bic` que calcula o tiling | `0x11c8258` | `0x11c1a58` |

Os endereços de código da tabela são VMA do ELF. O primeiro `PT_LOAD` dos dois arquivos tem VMA igual ao offset de arquivo. No projeto Ghidra da 1.2.10, carregado com base `0x100000`, o campo do patch aparece em `0x7bf964`.

Alteração em ambas as versões:

```text
Entrada uint32 little-endian: 129 → 130
Antes: 81 00 00 00
Depois: 82 00 00 00
```

É um campo de quatro bytes; apenas o primeiro byte muda. A tabela é usada também pelo render pass, mantendo o formato selecionado consistente entre esses caminhos.

[patch-exynos-depth.ps1](../scripts/patch-exynos-depth.ps1) verifica o cabeçalho ELF, o Build ID conhecido, os limites e o valor anterior. Recusa alteração na origem, saída em `original/`, saída existente e reaplicação do mesmo patch. Produz um manifesto com SHA-256 e suporta `-Reverse` para uma nova saída.

### Identidade das bibliotecas

| Versão | Estado | SHA-256 |
|---|---|---|
| 1.2.9 | Recebida | `ADC77A5A80CEF5AE694CEE9898488DF19FCB835AC4E847FBED9258069A905DEC` |
| 1.2.9 | Patchada | `6989DB81BADDBD8B140E0B79CFA8A1C5926EA309D549E16DB28A03764E553507` |
| 1.2.10 | Extraída do original | `AD9B07806ED2C0A9BA4FBB2DA9D0B680BD5998880A8A166F862D6CB9E38475D2` |
| 1.2.10 | Patchada | `C43293F4E3BD6061B096FE857E2C5C3998DABBD84385F870CE8EA1F0A4210EDF` |

Aplicar e reverter o patch foi executado nas duas bibliotecas. Os resultados revertidos ficaram idênticos às respectivas entradas por SHA-256. O Build ID permanece igual após a alteração; o hash e o manifesto distinguem o arquivo patchado.

## 5. Versão 1.2.10 — conjunto de splits

### Entrada e trabalho realizado

Os cinco APKs em `original/` foram preservados:

```text
base.apk
split_config.arm64_v8a.apk
split_config.pt.apk
split_config.xxhdpi.apk
split_InstallPack.apk
```

O base foi decodificado com Apktool e decompilado com JADX. A biblioteca ARM64 foi extraída seletivamente para `work/native/`; os assets grandes foram inicialmente inventariados. O patch de formato foi aplicado em cópia da biblioteca.

[build-exynos-diagnostic.ps1](../scripts/build-exynos-diagnostic.ps1) substitui a biblioteca no split ARM64, alinha a cópia, assina todos os APKs com a mesma chave local e verifica certificado comum, assinatura, alinhamento, manifests binários e hash da biblioteca empacotada.

### Saída e evidências

Saída: `output/exynos-depth-candidate/`.

- [Manifesto dos APKs e hashes](../output/exynos-depth-candidate/manifest.json).
- [Registro de validação no dispositivo](../output/exynos-depth-candidate/device-validation.json).
- [Log do probe com os parâmetros do engine](../work/native/s24-engine-depth-20261024.log).
- [Captura da tela de título e mensagem de erro](../work/captures/depth-candidate-wait/screen.png).
- [Log do bloqueio de autenticação](../work/native/s24-auth-diagnostic.log).

A instalação original no telefone foi removida com autorização explícita do usuário, que informou não haver dados a preservar. O candidato 1.2.10 abriu a apresentação e a tela de título em duas execuções. Posteriormente, ele foi removido para instalar a 1.2.9.

### Bloqueio do Play Games

O log da 1.2.10 mostrou `DEVELOPER_ERROR`, resposta OAuth informando que o par pacote/certificado SHA-1 não era registrado e mensagens do Play Store de `certificate mismatch`.

Assinar localmente permite instalar o APK, mas não registra esse certificado no cliente OAuth do editor. Reinstalar o mesmo APK ou conceder permissões não resolve esse vínculo. O funcionamento do Play Games depende do certificado associado ao cliente publicado; ver [documentação oficial](https://developer.android.com/games/pgs/android/troubleshooting#check_the_certificate_fingerprint).

Não foram alteradas licença, compras, integridade ou autenticação. A validação de batalha da 1.2.10 ficou pendente.

### Reprodução neste workspace

A biblioteca já patchada está em `work/native/exynos-depth-d32s8/libultimateninjastorm.so`. Para gerar outro conjunto, escolha uma saída que ainda não exista:

```powershell
.\scripts\build-exynos-diagnostic.ps1 -OutputDirectory 'output\exynos-depth-rebuild'
```

Em uma preparação sem o arquivo patchado padrão, gere-o antes:

```powershell
.\scripts\patch-exynos-depth.ps1
```

O builder 1.2.10 usa o caminho padrão da biblioteca; ele não recebe um parâmetro para escolher outra `.so`. Não execute novamente o patch sobre saídas existentes: o script recusa sobrescrevê-las.

## 6. Versão 1.2.9 — APK único fornecido pelo usuário

### Entrada e adaptação

Entrada preservada:

```text
C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\naruto-ultimate-ninja-storm.apk
```

Esse APK tem todos os dados reunidos em um arquivo e foi recebido com um certificado Debug. Sua origem não foi autenticada como uma publicação oficial. Apenas a biblioteca e os DEX necessários à análise foram extraídos; o APK inteiro não foi descompactado para estudar o patch.

O Build ID e os endereços diferem da 1.2.10. LLVM confirmou a tabela e as instruções equivalentes antes de adicionar o perfil 1.2.9 ao script de patch.

### Repack, assinatura e verificações

[repack-native-apk.py](../scripts/repack-native-apk.py) reconstruiu o APK substituindo a biblioteca verificada. Os outros **570 payloads** preservaram CRC32 e tamanho descomprimido; manifest e os dois DEX também foram comparados por SHA-256 e permaneceram idênticos à entrada.

As assinaturas antigas foram substituídas pela chave local. O repacker usa ZIP clássico abaixo de 4 GiB. Para que o assinador preserve o alinhamento, o campo ZIP Android `0xd935` inclui o múltiplo de alinhamento como uint16, seguido de padding. Um teste pequeno confirmou repack → assinatura → verificação de alinhamento; depois o APK completo passou pelo mesmo fluxo.

Foi necessário corrigir o padding ZIP e o limiar conservador de ZIP64 do Python durante o desenvolvimento do repacker. A primeira saída assinada que falhou no alinhamento não foi entregue como válida; o arquivo final foi reconstruído e verificado após a assinatura. APKs intermediários gerados foram removidos ao fim da validação.

| Artefato | Local |
|---|---|
| APK final, 3.484.961.255 bytes | [naruto-ultimate-ninja-storm-exynos.apk](../../../UltimateNinjaStorm/output/naruto-ultimate-ninja-storm-exynos.apk) |
| Relatório associado | [validation.json](../../../UltimateNinjaStorm/output/validation.json) |
| Verificação de assinatura | [signature-verification.txt](../work/external-1.2.9/signature-verification.txt) |
| Instalação via ADB | [install-result.txt](../work/external-1.2.9/install-result.txt) |

### Código adicional existente na entrada

O segundo DEX recebido contém `com.adshim.AdShimProvider` e `AdTimerCallback`. O provider registra callbacks de Activity; enquanto há Activity ativa, o callback abre um endereço externo no navegador a cada 180 segundos. Esse código não foi criado nem removido pelo patch gráfico.

O cliente Java do Play Games também permaneceu na entrada e na saída. Não foi demonstrado que a 1.2.9 dispense sua autenticação ou resolva o bloqueio OAuth observado na 1.2.10.

### Reprodução com novas saídas

No workspace atual, a biblioteca extraída e sua cópia patchada já existem. Para gerar outro APK usando a biblioteca patchada verificada:

```powershell
$inputApk = 'C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\naruto-ultimate-ninja-storm.apk'
$library = 'work\external-1.2.9\patched\libultimateninjastorm.so'
$unsigned = 'work\external-1.2.9\rebuild\exynos-unsigned.apk'
$outputApk = 'C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\output\naruto-storm-exynos-rebuild.apk'

if (Test-Path -LiteralPath $outputApk) { throw 'Escolha uma saída nova.' }
python .\scripts\repack-native-apk.py $inputApk $library $unsigned
if ($LASTEXITCODE -ne 0) { throw 'Repack falhou.' }
zipalign -c -P 16 4 $unsigned
if ($LASTEXITCODE -ne 0) { throw 'Alinhamento pré-assinatura falhou.' }

apksigner sign --ks 'work\signing\naruto-local.p12' --ks-key-alias naruto-local --ks-pass 'file:work/signing/naruto-local.password' --v4-signing-enabled false --out $outputApk $unsigned
if ($LASTEXITCODE -ne 0) { throw 'Assinatura falhou.' }
apksigner verify --verbose --print-certs $outputApk
if ($LASTEXITCODE -ne 0) { throw 'Verificação de assinatura falhou.' }
zipalign -c -P 16 4 $outputApk
if ($LASTEXITCODE -ne 0) { throw 'Alinhamento pós-assinatura falhou.' }
```

Para gerar outra cópia da biblioteca patchada, sem sobrescrever a atual:

```powershell
.\scripts\patch-exynos-depth.ps1 -InputLibrary 'work\external-1.2.9\libultimateninjastorm.so' -OutputLibrary 'work\external-1.2.9\patch-rebuild\libultimateninjastorm.so'
```

Se usar essa nova biblioteca no repack, ajuste `$library` para o novo caminho. O arquivo `.patch.json` adjacente é necessário ao repacker para conferir a origem e o resultado.

## 7. Instalação e erro de downgrade no S24

Antes da instalação, o dispositivo deve aparecer como `device`:

```powershell
adb devices -l
```

### APK único 1.2.9

Com o pacote anterior já removido, a instalação executada foi:

```powershell
adb install --no-incremental --user 0 'C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\output\naruto-ultimate-ninja-storm-exynos.apk'
```

O ADB retornou `Success`. As consultas seguintes confirmaram `versionCode=37`, `versionName=1.2.9`, um `base.apk` e `installed=true` no perfil pessoal. Depois disso, o usuário informou “Deu Certo!”. Não há confirmação específica de batalha.

### Conjunto 1.2.10

O conjunto exige os cinco arquivos da mesma saída e assinatura:

```powershell
$names = @('base.apk', 'split_config.arm64_v8a.apk', 'split_config.pt.apk', 'split_config.xxhdpi.apk', 'split_InstallPack.apk')
$apks = $names | ForEach-Object { Join-Path 'output\exynos-depth-candidate' $_ }
adb install-multiple $apks
```

Não tente atualizar uma instalação assinada pelo editor com a chave local. Uma troca de certificado exige remover o pacote anterior; isso apaga seus dados.

### `INSTALL_FAILED_VERSION_DOWNGRADE`

No aparelho desta sessão, a remoção apenas no perfil pessoal deixou a 1.2.10 registrada no perfil de trabalho (`user 11`). O instalador recusou a 1.2.9 porque o código 37 é inferior ao 38.

O log registrou a remoção posterior no perfil de trabalho, e então o pacote deixou de aparecer nas consultas. A instalação por ADB passou sem alterar artificialmente o versionCode.

Diagnóstico:

```powershell
adb shell pm list users
adb shell pm list packages --user 0 com.bandainamcoent.ultimateninjastorm
adb shell pm list packages --user 11 com.bandainamcoent.ultimateninjastorm
adb shell dumpsys package com.bandainamcoent.ultimateninjastorm | Select-String 'versionCode=|versionName=|User '
```

O ID 11 é específico do perfil de trabalho observado; confira `pm list users` em outro aparelho. Somente depois de autorizar a perda dos dados de todas as instalações desse pacote, uma remoção global pode ser feita com:

```powershell
adb uninstall com.bandainamcoent.ultimateninjastorm
```

## 8. Assinatura e reversão

Os dois candidatos usam a mesma chave local, alias `naruto-local`, em `work/signing/naruto-local.p12`. A senha fica em `work/signing/naruto-local.password`. Esses arquivos privados não devem acompanhar documentação pública ou APKs distribuídos.

Certificado local SHA-256:

```text
17d4f698488d0eca80bcff7c4440426e8bc7e145abf0ec05d9692a815693f074
```

Para reverter apenas a biblioteca 1.2.9 para uma nova saída:

```powershell
.\scripts\patch-exynos-depth.ps1 -Reverse -InputLibrary 'work\external-1.2.9\patched\libultimateninjastorm.so' -OutputLibrary 'work\external-1.2.9\rollback-novo\libultimateninjastorm.so'
```

Para a 1.2.10:

```powershell
.\scripts\patch-exynos-depth.ps1 -Reverse -InputLibrary 'work\native\exynos-depth-d32s8\libultimateninjastorm.so' -OutputLibrary 'work\native\rollback-novo\libultimateninjastorm.so'
```

Reverter a `.so` não altera o aplicativo já instalado. Restaurar a instalação original exige remover o candidato com autorização para apagar seus dados e reinstalar os cinco APKs de `original/` com `adb install-multiple`. Isso restaura a assinatura e o comportamento originais, incluindo a falha gráfica que motivou a investigação.

## 9. Experimentos que não entraram nos candidatos

Um tombstone anterior da 1.2.10 registrou `window == nullptr` em `vkCreateAndroidSurfaceKHR`. O Java pede permissões depois de inicializar a NativeActivity; isso motivou um experimento de lifecycle.

[patch-exynos-diagnostic.ps1](../scripts/patch-exynos-diagnostic.ps1) removeu somente esse pedido em uma cópia decodificada e gerou um **base sem assinatura**. Apktool construiu e JADX confirmou a alteração. Esse base não foi instalado e não compõe os candidatos finais, que preservam o Java recebido.

`READ_EXTERNAL_STORAGE` e `WRITE_EXTERNAL_STORAGE` não estavam declaradas no manifesto analisado, portanto `pm grant` não pôde concedê-las; `INTERNET` já estava concedida. Conceder permissões não foi a correção Exynos encontrada.

O probe independente usa `org.aciolabs.narutovulkanprobe`, uma Activity/SurfaceView e uma biblioteca NDK. Foi instalado e removido durante os testes. O aparelho bloqueado impediu os primeiros testes de superfície; eles foram repetidos após desbloqueio físico.

Para construir outra cópia do probe, escolha um diretório novo:

```powershell
.\scripts\build-vulkan-probe.ps1 -OutputDirectory 'work\probe-rebuild'
```

## 10. Assets, tradução e widescreen

Os arquivos `.awb` do InstallPack foram inicialmente classificados como áudio pela extensão. A leitura dos cabeçalhos corrigiu essa hipótese: são contêineres **CPK/@UTF**, com conteúdos variados.

[inventory-cpk.py](../scripts/inventory-cpk.py) inventariou os três contêineres da 1.2.10 sem extrair todos os payloads: 406 entradas em `installTimeDisc.awb`, 34 em `installTime.awb` e 252 em `sound.awb`, totalizando 692. Os dados estão em [cpk-inventory.json](../work/assets/cpk-inventory.json).

[extract-cpk-files.py](../scripts/extract-cpk-files.py) extraiu e descomprimiu seletivamente:

| Arquivo inglês | Tamanho extraído |
|---|---:|
| `data/event/eng/message.bin.xfbin` | 847.428 bytes |
| `data/event/eng/message_btl.bin.xfbin` | 50.038 bytes |
| `data/event/eng/itemtext.bin.xfbin` | 51.433 bytes |

Os arquivos têm prefixo NUCC e contêm textos reais, como `Free Battle`, tutoriais e IDs `NS1_Mobile_*`. O inventário também encontrou versões fre/ger/ita/jpn/spa. O [manifesto da extração](../work/assets/localization-eng/manifest.json) registra hashes e origem.

O split `pt` analisado contém textos de AndroidX/Google Play Services, não uma tradução completa do jogo. Ainda faltam interpretar os registros e offsets NUCC, criar o catálogo por ID, traduzir, reempacotar e validar fontes/placeholders.

Nenhum patch de câmera, FOV, HUD ou controles para 19,5:9 foi aplicado. O probe operar em 2340 × 1080 não comprova widescreen do jogo; a tela de título capturada ainda usa uma área central com arte lateral.

## 11. Limitações e próximos critérios de aceitação

- A troca da tabela é global para `mmDataFormat=15`, e não condicionada ao modelo da GPU. Outros dispositivos não foram validados.
- A metadata lógica de bits por pixel continua 32, enquanto D32S8 requer mais memória. A alocação Vulkan usa os requirements reais, mas readback/cópias de depth precisam de avaliação.
- O cleanup de threads e a hipótese de superfície nula continuam sem correção no candidato; uma outra falha de inicialização pode voltar a expor esses defeitos.
- Faltam evidências de entrada em batalha, renderização 3D/depth/stencil, controles, fechamento e reabertura durante gameplay e estabilidade prolongada.
- Widescreen e pt-BR são trabalhos pendentes; os APKs documentados contêm somente o patch gráfico descrito e o conteúdo existente nas respectivas entradas.

## 12. Referências e histórico

- [Histórico local completo](PROGRESS.md) e [notas dos experimentos](../patches/exynos/DIAGNOSTIC.md).
- [Investigação pública usada como referência inicial](https://github.com/apostolicfidei21/naruto-storm-android-reverse-engineering).
- [Google: certificado associado ao cliente Play Games](https://developer.android.com/games/pgs/android/troubleshooting#check_the_certificate_fingerprint).
- [AOSP: alinhamento no ApkSigner](https://android.googlesource.com/platform/tools/apksig/+/master/src/main/java/com/android/apksig/ApkSigner.java).
- Formatos de assets: [CPK/@UTF](https://github.com/kamikat/cpktools/blob/master/cpkunpack.py) e [CRILAYLA](https://github.com/esperknight/CriPakTools/blob/master/CriPakTools/CPK.cs).
