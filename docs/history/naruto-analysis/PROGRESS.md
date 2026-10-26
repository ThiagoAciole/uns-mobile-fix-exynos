# Progresso — Naruto Storm Mobile

## Estado atual

- Preservado: `naruto-ultimate-ninja-storm.apk` na raiz.
- Desmontado com Apktool 3.0.3 em `work/decoded`.
- Extraídos diretamente do ZIP os `classes.dex` e `classes2.dex` para `work/native`.
- JADX 1.5.6 decompilou `MainActivity`; a classe carrega `ultimateninjastorm` via JNI.
- Biblioteca localizada: `lib/arm64-v8a/libultimateninjastorm.so`, ELF64 AArch64, Build ID `d6c3c1ca40aa936ceb5b585da96f4a4a`.
- Ghidra 12.1.4 foi iniciado com a biblioteca desta cópia, mas a autoanálise produziu erros repetidos em `GccExceptionAnalyzer`/`LSDACallSiteTable`, e a tentativa de exportar listagens com `-noanalysis` não terminou. Não há pseudocódigo confiável. `llvm-objdump` confirmou o código de `mmThread_Impl::WaitForEnd()` e o caminho de `InitializeRenderSystem()`.
- Scripts criados: `scripts/extract.ps1`, `scripts/build.ps1`, `scripts/sign.ps1`. A assinatura cria uma chave local na primeira execução e solicita a senha em cada execução.

## Identidade do pacote

- Package: `com.bandainamcoent.ultimateninjastorm`
- Versão: `1.2.9` (versionCode 37), minSdk 28, targetSdk 35.
- Activity inicial: `com.bandainamcoent.ultimateninjastorm.MainActivity`, landscape.
- O APK contém uma única ABI (`arm64-v8a`) e os dados do jogo dentro de `assets/data`; os 12 arquivos `.awb` somam aproximadamente 3,22 GiB descompactados. Não foi encontrado um segundo APK junto ao original. O Manifest contém metadado Play Core de asset packs; a dependência em runtime ainda não foi confirmada.
- Existem resources Android de suporte, mas a interface do jogo usa arquivos proprietários `.awb`/`.xfbin`; nenhum catálogo de strings de gameplay foi extraído ainda. O ELF expõe símbolos de idioma e `cmnMessageManager::Load`, o que aponta para tabelas internas carregadas por idioma, mas não revela as mensagens.

## Exynos e gráficos

- Log de inicialização fornecido em `2026-10-24 17:03`: o XGL/SUMD 25.3.3 completa `Create`/`Init` e `nativeloader` carrega `libultimateninjastorm.so` com sucesso a partir de `split_config.arm64_v8a.apk`. Às 17:03:30.667 o jogo registra duas vezes `GPU do not support native format(3)`; às 17:03:30.679 o PAL registra quatro `Invalid format 0` e `CreateInternalImage failed -1`; às 17:03:30.686 ocorre `invalid pthread_t` seguido de `SIGABRT`.
- O log informa `target_sdk_version=36` e instalação com `base.apk`, `split_InstallPack.apk`, `split_config.arm64_v8a.apk`, `split_config.pt.apk` e `split_config.xxhdpi.apk`. Isso não corresponde ao APK local desmontado (1.2.9, targetSdk 35, biblioteca dentro do APK principal). É uma compilação dividida diferente; o log não fornece versionName nem Build ID do ELF carregado.
- As mensagens `Failed to find entry 'classes.dex'` aparecem durante a busca nos APKs e não impedem a Activity de iniciar nem a biblioteca nativa de carregar; não são a falha fatal observada neste trecho. `render engine as VK` refere-se ao caminho gráfico Android/HWUI e não confirma que o jogo criou seu dispositivo lógico Vulkan. A janela Android recebe frame 2340×1080 mais tarde no log, mas isso não comprova o extent do swapchain nem o viewport interno do jogo.
- Evidência atual prioriza uma falha na seleção/validação de formato de imagem como evento imediatamente anterior ao cleanup. O log não contém o primeiro `VkResult`, a chamada Vulkan que o produziu, nem o tombstone/backtrace completo; não prova ainda a causa raiz.
- Evidência estática nesta cópia: `WaitForEnd()` chama `pthread_join()` diretamente com o campo em `this + 0x10`, sem checar inicialização. Isso sustenta a falha final de cleanup, não identifica a operação Vulkan anterior.
- O Build ID difere da referência anterior. Endereços dessa referência não foram aplicados.
- O ELF desta cópia confirma o construtor de `mmThread_Impl` zerando os campos em `+0x00` e `+0x18`, enquanto `WaitForEnd()` usa o campo `+0x10` como `pthread_t`. Isso torna plausível a hipótese de espera em objeto ainda não iniciado, mas o campo não tem sentinel confiável demonstrado e o resultado de `pthread_create` ainda precisa ser rastreado; por isso não foi gerado um patch binário.
- Nenhum patch ARM64 foi aplicado: ainda falta identificar um estado de thread confiável e o primeiro erro Vulkan nesta versão. Não foi fabricado sucesso de `VkResult` nem removida a espera de thread.

## Widescreen e tradução

- Sem alterações aplicadas. A projeção, viewport, HUD e controles estão no engine nativo/dados do jogo; alterar apenas o Manifest não comprova widescreen nativo.
- Sem catálogo pt-BR. Os arquivos principais de dados são AWB, e o formato/índice de strings ainda precisa ser identificado antes de qualquer edição.

## Pipeline

- Para extrair/reextrair: `powershell -ExecutionPolicy Bypass -File scripts\extract.ps1`
- Para reconstruir a árvore decodificada e assinar: `powershell -ExecutionPolicy Bypass -File scripts\build.ps1`
- Para assinar outro APK unsigned: `powershell -ExecutionPolicy Bypass -File scripts\sign.ps1 -ApkPath caminho\arquivo-unsigned.apk`
- O build completo e a assinatura ainda não foram executados. O APK reconstruído usará certificado local; não substitui uma instalação oficial assinada por outro certificado.
- Os três scripts passaram pela validação sintática do parser do PowerShell 5.1; a execução do empacotamento ainda não foi validada ponta a ponta.
- REA não está conectado nesta sessão. JADX e Ghidra locais foram usados; o decompilador JADX de todo o APK foi interrompido após progresso lento, após a classe principal ter sido decompilada individualmente.
- Nenhuma versão modificada foi preparada; portanto, não houve instalação nem teste no Galaxy S24. Compatibilidade Vulkan, proporção 19,5:9, localização e reinicialização permanecem sem validação em dispositivo.
