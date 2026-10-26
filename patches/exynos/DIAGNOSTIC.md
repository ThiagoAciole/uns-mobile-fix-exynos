# Candidato diagnóstico: pedido de permissões no início

Este arquivo reúne experimentos em ordem de execução, incluindo hipóteses superadas. Para o resultado consolidado, os offsets das duas versões e os comandos atuais, consulte [EXYNOS_FIX.md](../../docs/EXYNOS_FIX.md). O candidato Java descrito primeiro não compõe os APKs finais.

`scripts/patch-exynos-diagnostic.ps1` copia a decodificação original para `work/decoded/exynos-diagnostic`, remove de `MainActivity.onCreate()` o bloco sem efeito de checagem e chamada `ActivityCompat.requestPermissions`, e reconstrói somente o base sem assinatura em `work/native/exynos-diagnostic-base-unsigned.apk`.

O Manifest declara `INTERNET`, mas não declara `READ_EXTERNAL_STORAGE` nem `WRITE_EXTERNAL_STORAGE`. A chamada ocorre depois de `mmEngineCoreActivity.onCreate()`, que chama `NativeActivity.onCreate()`. O tombstone do primeiro launch mostra `VkAndroidSurfaceCreateInfoKHR.window == nullptr` no caminho para `vkCreateAndroidSurfaceKHR`; isso torna a pausa/lifecycle uma hipótese testável. A relação causal ainda não foi provada, e os aborts posteriores em `pthread_join` continuam sem o primeiro `VkResult` capturado.

## Validação e limites

- Apktool 3.0.3 reconstruiu o base; JADX 1.5.6 reabriu o APK e confirmou `MainActivity.onCreate()` sem o pedido de permissões.
- Os inicializadores de `ccFrameworkUtility` e `ccSystemDialog` e a chamada a `super.onCreate()` foram preservados.
- O artefato é apenas o APK base sem assinatura. Não foi instalado: não é o conjunto completo de splits e não tem a assinatura original. O S24 permanece intacto.
- Este patch é um experimento de diagnóstico, não uma correção Exynos validada.

Para desfazer o experimento, descarte `work/decoded/exynos-diagnostic/` e `work/native/exynos-diagnostic-base-unsigned.apk`; os cinco APKs em `original/` e a decodificação base permanecem sem alteração.

## Probe de capabilities da superfície

`scripts/build-vulkan-probe.ps1` constrói `patches/exynos/ProbeActivity.java` e `vulkan_probe.c` em um pacote temporário separado. A `SurfaceView` fornece um `ANativeWindow`; o probe registra capabilities, formatos, suporte de imagem e filas present da GPU por Logcat. O APK foi instalado e removido do S24, mas o dispositivo estava bloqueado e sob `NotificationShade`, então a Activity não recebeu uma superfície. Repita o probe depois de desbloquear o telefone; a chave do probe fica apenas em `work/probe/probe.p12`.

## Confirmação estática adicional: cleanup de threads

Assembly AArch64 confirma que `mmThread_Impl` não inicializa o campo `pthread_t` em `+0x10`; `Start()` passa esse endereço a `pthread_create` e ignora seu retorno; `WaitForEnd()` passa o campo diretamente a `pthread_join`. O `Finalize()` do render manager aguarda as duas threads incondicionalmente, inclusive após falha de inicialização antes de `Start()`. Isso prova uma falha no cleanup parcial, mas a falha Vulkan que a antecede ainda não foi identificada. Nenhuma alteração foi feita na biblioteca nativa.

## Probe no S24 desbloqueado: superfície, swapchain e depth formats

O probe isolado confirmou sucesso em `vkCreateInstance`, `vkCreateAndroidSurfaceKHR`, `vkCreateDevice` e `vkCreateSwapchainKHR` com os parâmetros observados no jogo (formato 37, 2340×1080, 5 imagens, `usage=0x13`, identity, inherit e FIFO). Os warnings do driver `GPU do not support native format(3)` e `PAL: Invalid format 0` também apareceram nesse probe sem impedir a criação da swapchain.

A tabela do ELF mapeia `mmDataFormat=15` para Vulkan 129 (`D24_UNORM_S8_UINT`), cujo suporte de formato/uso depth é reportado como ausente pela Xclipse (`optimalTilingFeatures=0`, consulta de propriedades retorna -11). As alternativas 130 (`D32_SFLOAT_S8_UINT`) e 126 (`D32_SFLOAT`) são reportadas como suportadas. Porém o probe também conseguiu criar, alocar e vincular uma imagem 129, então isso ainda não prova que seja a primeira falha do jogo. A abertura original continua abortando no cleanup por pthread inválido; primeiro `VkResult` falho segue sem captura. Nenhum patch nativo foi feito.

Logs da execução: `work/native/s24-game-launch-20261024.log`, `work/native/s24-vulkan-probe-depth-20261024.log`, `work/native/s24-vulkan-imagecheck-20261024.log`, `work/native/s24-vulkan-memorycheck-20261024.log`. O pacote temporário foi removido após cada teste.

## Resultado mais recente: candidato nativo instalado

O probe anterior usava tiling optimal e usage=0x20, enquanto o engine solicita tiling linear para o formato 129 e usage=0x27. O probe com os parâmetros do engine reproduziu vkCreateImage=-3; com formato 130, passou por imagem, alocação, bind, image view, render pass e framebuffer. Detalhes de assembly e limites estão em docs/PROGRESS.md.

O script `scripts/patch-exynos-depth.ps1` altera o campo uint32 em offset ELF 0x6bf964 de 129 para 130, em cópia identificada pelo Build ID. Aplicação, reversão byte a byte por hash e guardas de entrada/saída foram validadas. A alteração é global e mantém metadata lógica de 32 bits por pixel: gameplay/readback e outros dispositivos ainda exigem teste.

Os cinco APKs em `output/exynos-depth-candidate/` foram assinados com a mesma chave local, verificados e instalados após autorização do usuário para remover o original. O jogo abriu vídeo e tela de título em duas aberturas, superando o abort de inicialização. A batalha não foi validada porque o Google Play Games recusou a assinatura local: o Logcat traz DEVELOPER_ERROR e informa que o par pacote/certificado SHA-1 não é registrado no OAuth do editor. Nenhuma verificação foi removida.

Comandos reproduzíveis, usando diretórios novos:

```powershell
.\scripts\build-vulkan-probe.ps1 -OutputDirectory work\probe-novo
.\scripts\patch-exynos-depth.ps1 -OutputLibrary work\native\depth-novo\libultimateninjastorm.so
.\scripts\patch-exynos-depth.ps1 -Reverse -InputLibrary work\native\depth-novo\libultimateninjastorm.so -OutputLibrary work\native\restaurado-novo\libultimateninjastorm.so
.\scripts\build-exynos-diagnostic.ps1 -OutputDirectory output\exynos-depth-novo
```

O build diagnóstico usa a biblioteca do caminho padrão gerado pelo patch e preserva os manifests originais. A chave e sua senha ficam em work/signing/; não devem ser publicadas. O script não instala nem desinstala aplicativos.

Referência do vínculo OAuth/certificado: https://developer.android.com/games/pgs/android/troubleshooting#check_the_certificate_fingerprint
