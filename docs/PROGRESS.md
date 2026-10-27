# Naruto Storm Android — progresso

Atualizado em 2026-10-26.

## Mapeamento integral widescreen — 26/10/2026

- Matriz por fluxo, assets, componente responsável, estado de evidência e lacunas: [WIDESCREEN_ASSET_MAP.md](WIDESCREEN_ASSET_MAP.md).
- Decisões de canvas 1560×720 lógico, âncoras e tratamento por tela: [WIDESCREEN_LAYOUT_SPEC.md](WIDESCREEN_LAYOUT_SPEC.md).
- Plano de conclusão em tarefas e gates independentes: [plano de widescreen integral](superpowers/plans/2026-10-26-naruto-storm-widescreen-app-completion.md).
- Escopo registrado: boot/logos/vídeo, título, modo, login, opções, gameplay/mapa, tutorial/diálogos, missões/itens/loja/minigames, seleção/batalha/pausa/resultados, transições, créditos e toque.
- Estado: base local `5DAC…` fixada; 20 fluxos cadastrados. Reanálise Ghidra foi feita na biblioteca exata e as VAs ELF foram corrigidas para remover a diferença de `0x100000` da imagem Ghidra. Mapa completo das funções identificadas em `work/candidates/widescreen-app-completion/native-function-map.json`.
- Revisão de evidências: as entradas do tutorial/menu de missões agora apontam para a análise da biblioteca exata; as VAs ELF antigas que ainda apareciam na matriz foram corrigidas. Rotas de mapa, tutorial e menu no ledger também apontam para os logs Ghidra exatos. Arquivos JSON dos ledgers e manifests foram reabertos e validados.
- Novos vínculos estáticos: sprites do menu de missões e quatro chunks do mapa foram ligados pelas relocações da tabela nativa e confirmados em assets extraídos do APK canônico; o ID `0xd4` não bate com o chunk extraído e permanece em investigação. Também foi encontrada uma inconsistência importante: o inventário CPK histórico não corresponde ao tamanho do banco no APK canônico. O inventário novo está em `canonical-base-cpk-inventory.json`; a extração canônica agora usa esse arquivo.
- O mapa foi classificado por camada: aro/minimapa em atlas 384×384, mapa da vila 1280×972 e ícones em textura separada. A rota de desenho usa um layer centrado que anima escala/offsets, depois um overlay fullscreen; isso não prova ainda qual ramo gera o minimapa do gameplay nem os limites de toque.
- Relatório detalhado: [ligações nativas de sprites e assets](WIDESCREEN_NATIVE_ASSET_BINDINGS_20261026.md). O S24 segue desconectado nesta sessão; não houve instalação nem teste visual novo.
- Candidato assinado separado: `D:\NarutoStorm_appcompletion_candidate_20261026\NarutoStorm-appcompletion-s24-candidate-verified.apk`, SHA-256 `6921DA65C70465840FD79EEFC5F9529E673241CAA48FF88A402F13A185A9F958`. Pacote 1.2.10/code 38, assinatura v3/certificado esperado, alinhamento 16 KiB e comparação dos 572 membros aprovados; relatório `work/candidates/widescreen-app-completion/candidate-integrity-report.json`.
- **Ainda não é o APK definitivo:** ADB está sem aparelho; associação visual de sprites/UV/bounds/hitboxes e aceite dos 20 fluxos continuam pendentes. Uma saída anterior em `D:` teve CRC inválido em `stage1.awb`, foi marcada como inválida e não foi instalada.

Guia consolidado: [Patch Exynos — versões 1.2.9 e 1.2.10](EXYNOS_FIX.md).

## Estado atual

**Correção aceita em 26/10/2026:** o APK `build/Naruto Ultimate Ninja Storm - composicao widescreen ajustada.apk` foi instalado por atualização no S24. O usuário confirmou que a margem de 210 px e o desalinhamento dos toques desapareceram.

- Pacote `com.bandainamcoent.ultimateninjastorm`, versão 1.2.10 / código 38.
- SHA-256 do APK instalado, conferido por ADB: `5dac1302663cbec6abc678b7f9c84976c2a2a1fea487f183febd2d42d2147d86`.
- SHA-256 da biblioteca ARM64 instalada: `5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071`.
- A atualização foi feita com `adb install --no-incremental -r --user 0`; não houve desinstalação nem limpeza de dados.
- O patch troca somente duas instruções de `ChangeRender` para usar largura e altura reais da tela; os demais bytes da biblioteca e os demais payloads foram preservados.
- Aceite visual e dos toques: relato do usuário após abrir o app; não foi produzida nova captura nesta etapa.
- Escopo validado: Galaxy S24, paisagem, 2340×1080. Outras telas, proporções e gameplay não foram revalidados.

Os registros abaixo descrevem análises e builds anteriores à correção aceita.

## Artefatos confirmados

- Os cinco APKs esperados existem em `original/`; os originais foram mantidos intactos.
- `base.apk`: pacote `com.bandainamcoent.ultimateninjastorm`, versão `1.2.10`, `versionCode=38`, `minSdk=28`, `targetSdk=36`.
- Manifesto: `MainActivity`, landscape, mudanças de orientação/tela tratadas pela Activity e carregamento nativo `ultimateninjastorm`.
- `split_config.arm64_v8a.apk`: contém `libultimateninjastorm.so` e `libc++_shared.so`. A primeira foi extraída para `work/native/`.
- A `.so` é ELF64 AArch64 little-endian, importa Vulkan/Android/JNI base e tem Build ID `c3e506f9be350dfb4a00c79228754028`. Corresponde exatamente à compilação citada na investigação anterior.
- `split_config.pt.apk` é split de recursos pt; foi decodificado em `work/decoded/split-pt/`.
- `split_InstallPack.apk` contém três contêineres CPK com extensão `.awb`, totalizando ~722 MB sem compressão no ZIP externo. Não foram extraídos nem expandidos.
- `base.apk` foi decodificado com Apktool 3.0.3 para `work/decoded/base/`.
- JADX 1.5.6 foi baixado da release oficial para `work/tools/` e executado em `base.apk`; a decompilação Java ocorreu, com 8 erros parciais. `MainActivity` está em `work/jadx/base/sources/.../MainActivity.java`.

## Estado da investigação Exynos

### Evidência existente e aplicável ao Build ID atual

- A investigação anterior para este mesmo Build ID confirmou `SIGABRT` em `pthread_join` com `pthread_t` inválido durante cleanup do renderizador Vulkan.
- Logs anteriores registraram `GPU do not support native format(3)`, `PAL: Invalid format 0` e `CreateInternalImage failed -1` imediatamente antes do abort. Isso aponta a investigação para criação/formato de imagem, mas ainda não identifica o primeiro `VkResult` falho.
- A análise estática anterior delimitou o fluxo Vulkan, swapchain e as duas threads do renderizador. Não há patch comprovado.
- A instalação original e os dados do jogo não foram alterados nesta execução.

### Ferramentas

- Apktool e JADX executaram localmente.
- REA `open_binary` identificou o ELF, mas as consultas nativas foram recusadas: o provider Ghidra integrado neste Windows declara suporte apenas a PE e raw 6502; Hopper não suporta Windows e IDA não está configurado.
- Ghidra 12.2 local importou e salvou o ELF; a autoanálise temporizada ficou parcial após 206 s. `llvm-objdump` forneceu as instruções das funções críticas.

## Próximas ações

1. Continuar a análise dirigida das funções Vulkan e threads; a análise automática completa do Ghidra excedeu 180 s e não é requisito para inspecionar assembly pontual.
2. Inventariar strings, assets e tabelas de localização sem expandir os contêineres CPK de 722 MB.
3. Criar instrumentação/patch somente após identificar com evidência a primeira falha e validar a semântica de cleanup parcial.
4. Implementar widescreen e pt-BR em suas camadas reais; não considerar mudança de manifesto como correção visual ou tradução completa.
5. Reconstruir/signar splits e validar em dispositivo somente depois dos patches.

## Referência técnica

- [Investigação pública Naruto Storm Android](https://github.com/apostolicfidei21/naruto-storm-android-reverse-engineering): registra a mesma versão e Build ID, causa imediata no cleanup e causa Vulkan original ainda em investigação.

## Execução controlada no S24 — 2026-10-24

- ADB confirmou SM-S921B, `versionCode=38`, `1.2.10`, `targetSdk=36`, SDK 37. Os cinco APKs instalados correspondem ao conjunto local.
- Foi iniciado somente o app já instalado; nenhuma permissão foi concedida, nenhum APK instalado e nenhum dado removido.
- A tentativa atual falhou com `SIGSEGV` (não o `SIGABRT` dos tombstones anteriores): thread `androidMain`, fault `0x98`, PC em `libvulkan.so!CreateAndroidSurfaceKHR+232`. O tombstone está copiado em `work/native/dropbox-tombstones.txt`; log filtrado em `work/native/runtime-launch-20261024.log`.
- Na mesma execução, a Activity abriu o diálogo de permissões de armazenamento e foi imediatamente pausada. A análise de `CreateSurface()` (objdump do ELF) mostra `GetWindow()` retornando o ponteiro que é colocado em `VkAndroidSurfaceCreateInfoKHR.window` e enviado a `vkCreateAndroidSurfaceKHR`, sem checagem local de nulo. A hipótese é que a janela nativa ainda não estava disponível nessa sequência; o fault ocorre dentro do loader Vulkan. Isso não prova falha de compatibilidade Xclipse nem substitui o crash anterior de `pthread_join`.
- O usuário autorizou a concessão e repetição. `pm grant` não alterou o pacote: `dumpsys package` mostra que `READ_EXTERNAL_STORAGE` e `WRITE_EXTERNAL_STORAGE` não constam em `requested permissions`; `INTERNET` já está concedida. Não há permissão de armazenamento disponível para conceder sem mudar o APK.
- As tentativas seguintes às 18:15:29 e 18:16:20 voltaram a `SIGABRT` em `pthread_join` com o mesmo handle inválido. Os resumos estão em `work/native/latest-crash-summaries.txt`.
- Nova abertura solicitada após a confirmação de concessão: `am start -W` reportou `GrantPermissionsActivity`, mas a checagem ~700 ms depois já encontrou o launcher; não havia diálogo ativo para conceder. A captura temporária foi removida do dispositivo e do workspace. Essa tentativa não acrescenta um `VkResult` ao diagnóstico.

## Candidato diagnóstico de lifecycle

- JADX e Smali confirmam que `MainActivity.onCreate()` executa `NativeActivity` via `super.onCreate()` e depois chama `ActivityCompat.requestPermissions()` para armazenamento e `INTERNET`. As checagens anteriores têm resultados descartados; o callback também não usa a decisão além de ler o primeiro inteiro.
- O primeiro tombstone registrou `window == nullptr` em `VkAndroidSurfaceCreateInfoKHR` durante `vkCreateAndroidSurfaceKHR`. A ordem do lifecycle torna a solicitação de permissões um fator plausível para a falha de superfície, ainda sem prova causal.
- Criado `scripts/patch-exynos-diagnostic.ps1`: em cópia, remove só o bloco de permissões de `MainActivity.onCreate()` e reconstrói um APK base sem assinatura. A inicialização da engine, os objetos Java e os APKs originais ficam preservados.
- Apktool 3.0.3 construiu o candidato; JADX 1.5.6 confirmou o método no APK reconstruído sem a chamada de permissão. Não é um pacote instalável completo e não foi instalado no S24. Detalhes: `patches/exynos/DIAGNOSTIC.md`.
- O resultado é um teste de hipótese de lifecycle, não uma correção Exynos. Os crashes posteriores em `pthread_join` e a primeira falha Vulkan ainda exigem captura independente.

## Limites confirmados para localização

- O split português inclui `values-pt-rBR` e `values-pt-rPT`, mas os textos encontrados são de AndroidX/Google Play Services; não são o menu do jogo.
- O base tem shaders SPIR-V, alguns recursos `.xfbin` de sistema e texturas; não apareceu catálogo de diálogos/tutoriais nos assets legíveis extraídos até aqui.
- A classificação inicial dos `.awb` como áudio foi corrigida pela leitura dos cabeçalhos: os três são contêineres CPK/@UTF. O inventário seletivo encontrou as tabelas de textos em data/event/eng/; ver a seção de localização abaixo.

## Análise nativa local

- `llvm-readelf` confirmou ABI/Build ID; `llvm-objdump` abriu assembly AArch64 em `CreateSurface()` e `InitializeRenderSystem()`.
- Ghidra 12.2 importou e salvou o ELF no projeto `work/native/ghidra-project`. A autoanálise ultrapassou o limite configurado de 180 s após 206 s de trabalho total e ficou parcial; há 459 símbolos externos não resolvidos. O arquivo não contém tabela de símbolos ELF.

## Fluxo Vulkan de inicialização — Ghidra 12.2

- A decompilação dirigida de `InitializeRenderSystem()` mostra `vkCreateInstance`, `InitializeVulkanDevice()` e `vmaCreateAllocator()` em sequência. `vkCreateInstance()` e os resultados de enumeração/`vkCreateDevice()` são verificados; enumerações repetem em `VK_INCOMPLETE` e convertem falhas em exceções Vulkan.
- `mmRenderManager_Vulkan::Initialize()` executa `CreateSurface()` e `CreateSwapchain()` antes da criação das threads. Depois ainda executa depth buffer, render pass, framebuffer, command buffers, layout e graphics pipeline; as duas chamadas `mmThread::Start()` vêm depois. Isso torna consistente que uma falha de inicialização anterior chegue a cleanup com handles de thread não iniciados, mas não identifica qual retorno disparou os aborts gravados.
- `CreateSurface()` grava o resultado de `GetWindow()` em `VkAndroidSurfaceCreateInfoKHR.window` e chama `vkCreateAndroidSurfaceKHR` sem validar nulo. No tombstone de 18:11:47, o ponteiro estava nulo e o processo recebeu `SIGSEGV` dentro do loader antes de qualquer `VkResult` dessa chamada.
- `CreateSwapchain()` enumera os formatos e repete em `VK_INCOMPLETE`, mas copia o primeiro `VkSurfaceFormatKHR` retornado para o formato usado. Depois verifica os retornos de `vkGetPhysicalDeviceSurfaceCapabilitiesKHR` e `vkCreateSwapchainKHR`; não foi provado qual retorno falhou nas execuções com `SIGABRT`.
- O probe isolado foi compilado com NDK 27.2, alinhado, assinado e validado. Foi instalado e removido, porém não obteve `SurfaceView`: o S24 estava bloqueado (`deviceLocked=1`), com foco em `NotificationShade` e `mFocusedApp=null`. Nenhuma consulta Vulkan do probe foi executada. Não contornei o bloqueio.

## Automação e proteção dos artefatos

- Criado `scripts/extract.ps1`; a execução confirmada não repetiu a desmontagem já existente, não reextraiu a .so e indexou apenas os metadados do InstallPack.
- Criado `.gitignore` para `original/`, `work/` e `output/`, evitando incluir APKs, assets e binários em um futuro Git.





## Confirmação em assembly do cleanup — 2026-10-24

- `mmThread_Impl` construtor (`0x9f856c`) zera os campos `+0` e `+0x18`, inicializa mutex em `+0x20` e `+0x28`; não inicializa `pthread_t` em `+0x10`.
- `mmThread_Impl::Start` (`0x9f6ec4`) chama `pthread_create` com destino `this + 0x10`, mas a instrução seguinte não testa `w0`/retorno. Assim, mesmo falha de criação pode deixar o campo inválido sem tratamento.
- `mmThread_Impl::WaitForEnd` (`0xabe8cc`) carrega `this + 0x10` e chama `pthread_join` sem validar o handle. `mmRenderManager_Vulkan::Finalize()` chama WaitForEnd incondicionalmente para os dois handles, inclusive em cleanup de inicialização parcial.
- Isso confirma um defeito real no cleanup capaz de explicar o `SIGABRT` após falha anterior. Não determina a causa Vulkan original. Nenhum patch nativo foi aplicado.
- O `llvm-objdump` confirmou endereços e instruções diretamente no ELF extraído. O telefone continua exigindo desbloqueio físico para executar o probe de superfície; não contornei a tela bloqueada.

## S24 desbloqueado: probe Vulkan e nova abertura — 2026-10-24 18:50–18:57

- O S24 foi confirmado desbloqueado (`deviceLocked=0`). O probe temporário, em pacote separado, validou `vkCreateInstance`, `vkCreateAndroidSurfaceKHR`, Xclipse 940, capabilities, filas e `vkCreateSwapchainKHR` com os parâmetros conhecidos do jogo: formato 37, extent 2340×1080, 5 imagens, uso `0x13`, transform identity, composite alpha inherit e FIFO; todos retornaram `VK_SUCCESS`.
- Os logs `GPU do not support native format(3)` e `PAL: Invalid format 0` também ocorreram durante o probe bem-sucedido de swapchain. Portanto, isoladamente, esses avisos do driver não localizam a falha que aborta o jogo.
- O engine mapeia `mmDataFormat=15` para `VK_FORMAT_D24_UNORM_S8_UINT` (129) no caminho do depth buffer. Na Xclipse, `vkGetPhysicalDeviceFormatProperties` retorna `optimalTilingFeatures=0` e `vkGetPhysicalDeviceImageFormatProperties` retorna `-11` para uso depth; 130 (`D32_SFLOAT_S8_UINT`) e 126 (`D32_SFLOAT`) são anunciados como suportados.
- Controle direto em probe: `vkCreateImage`, `vkAllocateMemory` e `vkBindImageMemory` retornaram sucesso também para 129. Logo, a ausência de suporte anunciado torna o formato 129 suspeito para uso posterior como depth attachment, mas ainda não prova que ele seja a primeira chamada que falha no jogo.
- A abertura do jogo original, sem reinstalação, voltou a `SIGABRT` em `pthread_join` (`pthread_t 0x2e79616c702e6469`), com stack em `mmRenderManager_Vulkan::Finalize()` e `InitializeRenderSystem()+468`. O jogo continua instalado; o pacote temporário do probe foi removido.
- Evidências: `work/native/s24-game-launch-20261024.log`, `work/native/s24-vulkan-probe-depth-20261024.log`, `work/native/s24-vulkan-imagecheck-20261024.log` e `work/native/s24-vulkan-memorycheck-20261024.log`.

## Interpretação intermediária — antes do probe com parâmetros do engine

A superfície nativa e a criação de swapchain com parâmetros do jogo funcionam em uma Activity independente no S24. Os warnings PAL que aparecem junto não bastam para explicar o crash. `mmDataFormat=15` aponta para um formato depth sem suporte anunciado, mas chamadas simples de criação/alocação/vinculação de imagem passam; falta instrumentação que identifique a primeira chamada Vulkan que falha no contexto do jogo. Não aplicar patch de formato ou tratar o `SIGABRT` como resolvido até essa evidência existir.

## Falha de depth reproduzida e candidato — 2026-10-24 19:04

A comparação dos testes anteriores com o assembly revelou uma diferença: os controles usavam tiling optimal e usage=0x20. O engine calcula tiling como `1 & ~optimalTilingFeatures`, pelo bit SAMPLED_IMAGE, e adiciona sampled/transfer ao uso depth. Para mmDataFormat=15 / VkFormat=129, os features da Xclipse são zero; portanto o engine solicita tiling linear e usage=0x27.

- Assembly: `CreateDepthBuffer` ELF 0xd1223c passa formato 15; 0xd12244 passa mmUsageType=2. A tabela de uso contém 0x3 para tipo 2. O caminho de imagem acrescenta 0x20 (depth) e 0x4 (sampled).
- `CreateTextureFromImageDesc` ELF 0x11c1a40 lê optimalTilingFeatures; 0x11c1a58 calcula o bit de tiling; 0x11c1ab4 grava VkImageCreateInfo.tiling. `vkCreateImage` é chamado em 0x11c1bac e seu resultado é testado em 0x11c1bb0.
- O probe no S24 reproduziu `vkCreateImage(format=129, usage=0x27, tiling=LINEAR, 2340x1080) = -3` (`VK_ERROR_INITIALIZATION_FAILED`). A substituição por 130 resulta em tiling optimal e sucesso de imagem, alocação, bind, image view, render pass e framebuffer depth-only. O teste equivalente com 126 também passou, mas perde stencil; o candidato usa 130 para preservar depth+stencil.
- Essa é uma reprodução isolada da chamada problemática deduzida do ELF; não é captura instrumentada do primeiro retorno dentro do processo original. O log está em `work/native/s24-engine-depth-20261024.log`.
- Criado `scripts/patch-exynos-depth.ps1`: altera apenas a entrada uint32 da tabela em offset ELF 0x6bf964 / Ghidra 0x7bf964, índice 15: bytes 81 00 00 00 -> 82 00 00 00. O script valida ELF/Build ID/valor anterior, proíbe escrita em original/ e na origem, produz hash/manifesto e suporta -Reverse. Aplicação e reversão foram executadas; o SHA-256 do resultado revertido é idêntico à origem. Guardas contra reaplicação e saída em original/ passaram.

A mudança da tabela é global e diagnóstica. A metadata lógica de bits por pixel continua 32, enquanto D32S8 ocupa mais memória; a alocação Vulkan usa requirements reais, mas readback/cópia de depth exigem investigação antes de tratar como solução final. O cleanup de threads ainda não foi modificado.

`scripts/build-exynos-diagnostic.ps1` construiu os cinco splits em `output/exynos-depth-candidate/`, com uma única chave local em `work/signing/`. Assinaturas, certificado comum, alinhamento de bibliotecas 16 KiB, manifests binários preservados e hash da biblioteca empacotada foram verificados. O usuário autorizou remover o original para teste, informando que não há dados do app a preservar. Instalação e aceitação do jogo serão registradas após o resultado real.


## Instalação do candidato e bloqueio OAuth — 2026-10-24

- Com autorização explícita do usuário, o pacote original foi desinstalado e os cinco APKs locais de `output/exynos-depth-candidate/` foram instalados com sucesso no SM-S921B. Os APKs originais em disco continuam disponíveis.
- O candidato renderizou a abertura CyberConnect2, o vídeo e a tela de título em duas aberturas completas. Não apareceu novo SIGABRT/SIGSEGV no buffer de crash da sessão. O patch de formato superou o crash de inicialização observado no original; isso ainda não valida menu, combate, depth/stencil em gameplay ou estabilidade prolongada.
- O fluxo para iniciar o jogo fica bloqueado por Google Play Games. O Logcat registra `DEVELOPER_ERROR` e a resposta OAuth informa que o aplicativo Android não está registrado para esse par package name/certificado SHA-1. O Play Store também registra `installed but certificate mismatch`. Essa evidência identifica a assinatura local como incompatível com o cliente OAuth publicado; não é uma permissão Android nem um novo crash Vulkan.
- Nenhuma verificação de licença, compra, integridade ou autenticação foi removida/modificada. O candidato permanece instalado; a validação de batalha ficou pendente. Fonte de evidência: `work/native/s24-auth-diagnostic.log` e capturas em `work/captures/depth-candidate-*`.
- Assinatura local atual (SHA-256): `17d4f698488d0eca80bcff7c4440426e8bc7e145abf0ec05d9692a815693f074`. A chave privada do editor não está disponível; registrar a chave local no OAuth do editor exigiria acesso ao projeto dele. Uma nova assinatura local não resolve esse vínculo. Testes futuros que preservem o APK oficial precisarão de um ambiente de instrumentação compatível, sem alterar a autenticação.

## Localização: contêineres e textos reais encontrados

- `scripts/inventory-cpk.py` leu apenas cabeçalhos e tabelas CPK/@UTF dentro do split armazenado, sem extrair os bancos completos. Os totais validados contra CPK.Files são 406 arquivos em installTimeDisc.awb, 34 em installTime.awb e 252 em sound.awb: 692 entradas. Inventário em `work/inventory/cpk-inventory.json`.
- Os arquivos `data/event/eng/message.bin.xfbin`, `message_btl.bin.xfbin` e `itemtext.bin.xfbin` existem, assim como versões fre/ger/ita/jpn/spa. As tabelas e os ranges dos arquivos foram validados. Os três textos ingleses foram extraídos e descomprimidos seletivamente com `scripts/extract-cpk-files.py` para `work/inventory/localization-eng/`: 847428, 50038 e 51433 bytes, respectivamente. O prefixo é NUCC, e os textos incluem `Free Battle`, `Ultimate Mission`, tutoriais e IDs como `NS1_Mobile_Error_Back_Title_Message`.
- A descompressão CRILAYLA verifica tamanho contra ExtractSize, limites do bitstream e back-references; nenhuma extração de payloads não selecionados foi feita. Ainda falta interpretar integralmente os registros/offsets NUCC, gerar catálogo com IDs estáveis, traduzir e provar round-trip do reempacotamento.
- Referências técnicas dos formatos: https://github.com/kamikat/cpktools/blob/master/cpkunpack.py e https://github.com/esperknight/CriPakTools/blob/master/CriPakTools/CPK.cs. Os scripts locais usam apenas a biblioteca padrão Python.

## APK alternativo 1.2.9 — candidato Exynos gerado

- Entrada preservada: `C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\naruto-ultimate-ninja-storm.apk`, versão 1.2.9 / versionCode 37, APK único de 3471342213 bytes, assinado originalmente com certificado Debug (SHA-256 a052076edcc6adc9368b9428afaeaf630fd670fb15fdc7ca62c338d7afa7d8bd).
- A biblioteca ARM64 tem Build ID d6c3c1ca40aa936ceb5b585da96f4a4a. Assembly confirma mmDataFormat=15 em CreateDepthBuffer (ELF 0xd18a3c), tabela em VMA/file offset 0x6c6128, entrada 15 em 0x6c6164 com valor 129. A escolha de tiling usa o mesmo `bic w24,w22,w8` em 0x11c8258. O perfil novo foi adicionado a scripts/patch-exynos-depth.ps1; aplicar e reverter produziu hash idêntico à biblioteca de entrada.
- Saída: `C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\output\naruto-ultimate-ninja-storm-exynos.apk`, 3484961255 bytes. Patch gráfico 129 -> 130; assinatura v3 local e alinhamento 16 KiB verificados após assinatura. Biblioteca final SHA-256 6989DB81BADDBD8B140E0B79CFA8A1C5926EA309D549E16DB28A03764E553507.
- `scripts/repack-native-apk.py` preservou CRC/tamanho dos outros 570 payloads. Manifest e os dois DEX têm SHA-256 idêntico ao arquivo recebido; o Java não foi modificado. A assinatura antiga é substituída pela local. `validation.json` acompanha o APK final. Os APKs intermediários gerados foram removidos após validação; a entrada não foi sobrescrita.
- A entrada já contém `com.adshim.AdShimProvider` e `AdTimerCallback` em classes2.dex, inicializados por ContentProvider. O callback abre um endereço externo no navegador a cada 180 segundos de Activity ativa. Esse código foi preservado. O Java ainda usa o cliente Google Play Games e sua autenticação; não há evidência de que esta versão evite o bloqueio OAuth com assinatura local. Não foi instalada nem testada no S24 nesta etapa; widescreen e pt-BR não integram esse candidato.

### Verificação de alinhamento do repack

O primeiro teste completo detectou que o assinador deslocava a biblioteca apesar do alinhamento prévio. O campo Android ZIP 0xd935 precisa conter um uint16 com o múltiplo de alinhamento, seguido de padding (fonte AOSP: https://android.googlesource.com/platform/tools/apksig/+/master/src/main/java/com/android/apksig/ApkSigner.java). O repacker foi corrigido e um fixture pequeno passou por repack -> assinatura -> zipalign -c -P 16; depois o APK completo passou pelas mesmas verificações. O uso de ZIP clássico foi limitado a 4 GiB para evitar ZIP64 incompatível com o assinador.

## Instalação do APK único 1.2.9 — 2026-10-24

O usuário relatou falha na instalação manual. O log do S24 confirmou `INSTALL_FAILED_VERSION_DOWNGRADE`: versionCode 37 do novo APK contra 38 ainda registrado no perfil de trabalho (user 11), após remoção apenas no perfil pessoal. A remoção do perfil de trabalho também foi observada no log; as consultas seguintes já não encontravam o pacote.

A instalação foi repetida via `adb install --no-incremental --user 0` com o APK final e retornou `Success`. A versão e o caminho instalado no perfil pessoal foram consultados depois. Essa etapa valida instalação; não houve novo teste de abertura/batalha nem alteração adicional no APK. Evidência: `work/external-1.2.9/install-result.txt`; o validation.json junto ao APK foi atualizado.

## Consolidação da documentação das duas versões — 2026-10-24

Criados README.md e docs/EXYNOS_FIX.md como entrada e guia técnico consolidado. O guia registra diferenças de distribuição/Build ID/offsets, diagnóstico do depth e do cleanup, conteúdos dos candidatos, assinatura e alinhamento, reprodução dos builds, instalação por perfil, downgrade, reversão, autenticação OAuth e evidências de assets/localização. Os comandos documentam as limitações dos scripts existentes e exigem novas saídas para evitar sobrescrita.

Após a instalação da 1.2.9, o usuário respondeu “Deu Certo!”. Esse relato foi incluído no guia e no validation.json associado ao APK como evidência do usuário, sem inferir comprovação específica de menu ou batalha. O topo deste histórico foi atualizado para distinguir a instalação mais recente da 1.2.9 dos testes anteriores da 1.2.10. Nenhum APK ou script de implementação foi alterado nesta tarefa de documentação.

## APK único 1.2.10 recebido posteriormente — 2026-10-24

Gerado `C:\Users\Thiago Aciole\Projetos\UltimateNinjaStorm\output\Ultimate-Ninja-Storm-1.2.10-exynos.apk` a partir do APK único informado pelo usuário, sem substituir o arquivo de entrada nem a instalação 1.2.9 no aparelho. A biblioteca mantém Build ID c3e506f9be350dfb4a00c79228754028, mas tem 675 bytes pré-alterados em relação à biblioteca dos splits originais. O assembly relevante foi conferido novamente; o patch gráfico alterou somente o byte em 0x6bf964, 0x81 -> 0x82, preservando todas as diferenças recebidas.

Reversão por hash, assinatura v3, alinhamento de 16 KiB após assinatura, biblioteca empacotada, identidade de manifest/DEX por SHA-256 e CRC/tamanho dos outros 571 payloads foram validados. APK final SHA-256: 1863fe2760b6595ddca2047d996f5a6f17bc33477ff4401b5efac55eaa696679. O intermediário APK gerado foi removido após validação para recuperar espaço. Relatório específico: [APK_UNICO_1_2_10.md](APK_UNICO_1_2_10.md). Nenhuma validação em dispositivo deste APK único foi executada.

## Atualização para o APK único 1.2.10 — 2026-10-24

Após solicitação explícita do usuário, executado `adb install --no-incremental -r --user 0` com `Ultimate-Ninja-Storm-1.2.10-exynos.apk`. Resultado: `Success`. A consulta posterior confirmou versionCode 38 / versionName 1.2.10, targetSdk 36, um base.apk instalado no perfil pessoal e os mesmos inodes CE 1690236 e DE 1649050 da 1.2.9. Não houve desinstalação. Abertura, autenticação e batalha não foram testadas nesta etapa. Log: `work/external-single-1.2.10/update-result.txt`; relatório do APK, README e guia específico atualizados.

## Definição da versão principal — 2026-10-24

O usuário definiu o APK único 1.2.10 como principal. A entrada canônica para os próximos ajustes é UltimateNinjaStorm/Ultimate-Ninja-Storm-1.2.10.apk; o artefato principal é output/Ultimate-Ninja-Storm-1.2.10-exynos.apk nessa mesma pasta. README, guia específico, guia consolidado e metadados foram atualizados. A 1.2.9 e os cinco splits anteriores ficaram identificados como históricos. Nenhum APK foi recompilado ou reinstalado nesta mudança de referência; o nível de validação de abertura/batalha permanece pendente para a base principal.

## Tradução pt-BR e widescreen no APK principal — 2026-10-24

Extraídos e remontados os três catálogos ingleses com 7.104 textos únicos / 13.209 campos. Traduções em patches/ptbr/catalogs; editor XFBIN valida SHA de origem, estrutura, IDs, vozes e controles de formatação. Fonte com fallback nativo para os acentos, confirmado estaticamente e pela renderização de configurações/Não/à/Ação no S24. O português ocupa o slot English; selecionar setas não aplica a troca até sair das Opções e confirmar retorno ao título. Isso explicou a interface que continuava em japonês durante a escolha.

Widescreen: dimensões reais de render/composição, remoção de DrawLetterBox, câmera Hor+, matriz uniforme da interface e conversão inversa do toque. ASM em patches/widescreen/stubs.S; cave de140bytes sem referências externas ao interior. Plano dourado do título ampliado separadamente de±640 a±780 em X, com bounds correspondentes; logo/UI/textura/UV/animações idênticos.

Prévia parcial instalada e observada na vila em2340×1080 sem faixas. APK completo com os quatro assets reconstruídos instalado por atualização com Success, código38/1.2.10, lastUpdateTime20:54:04. Assinatura v3, alinhamento16KiB, hashes da biblioteca/CPK e leitura dos quatro assets do APK assinado conferidos;570outros payloads preservados, manifest/DEX idênticos. Português persistiu após reiniciar e toques em Voltar/Sim funcionaram. Capturas finais mostram textos acentuados e laterais preenchidas na transição do título; o título avançou à escolha de modo durante a captura, sem aceitação prolongada do logo parado.

Saída: output/ptbr-widescreen/Ultimate-Ninja-Storm-1.2.10-ptBR-widescreen.apk, SHA256E6077D708ACFCF314893E2C62F27DC9C8AE1D6BFD356BEEE613EFB8B3232C12D. [Guia específico](PTBR_WIDESCREEN.md). Texto desenhado em imagens ainda não traduzido; combate, vídeos e todas as quebras de linha não homologados. Originais e APK Exynos anterior preservados; nenhuma desinstalação ou limpeza de dados.
# Planejamento widescreen integral — 2026-10-26

- Especificação de layout e âncoras por tela: [WIDESCREEN_LAYOUT_SPEC.md](WIDESCREEN_LAYOUT_SPEC.md).
- Matriz de assets, fluxos e rotas: [WIDESCREEN_ASSET_MAP.md](WIDESCREEN_ASSET_MAP.md).
- Plano por tarefas e gates: [plano de execução](superpowers/plans/2026-10-26-naruto-storm-widescreen-app-completion.md).
- Evidência e hashes da base/rotas: `work/candidates/widescreen-app-completion/{base-manifest.json,screen-state-ledger.json,render-route-ledger.json,native-function-map.json,ledger.md}`.
- Candidato assinado e verificado estaticamente: `D:\NarutoStorm_appcompletion_candidate_20261026\NarutoStorm-appcompletion-s24-candidate-verified.apk`; a integridade de todos os 572 payloads passou, com alterações limitadas à biblioteca e dois AWBs declarados.
- Estado: planejamento consolidado e primeiro candidato integrado; falta ligar sprites/UV/bounds/hitboxes de cada tela e fazer aceite dos 20 fluxos no aparelho. O `adb` permanece sem dispositivo, e a build não pode ser declarada definitiva nem promovida ainda.
- Mapeamento estático adicional do tutorial: `ccDispTutorial::Setup` cria `0x25b → cmn_tutorial.xfbin#xcmn_tutorial_win00` e `0x25e → #xcmn_tutorial_dmy`; o cabeçalho `ccWindowHeader` usa clump `0x36e → xcmn_mobile.xfbin#xcmn_hbase01_a01`. A escala X do painel já acompanha a largura lógica. O texto da captura está ligado a `dialog_014_01` (registro 11565), e o caminho de entrada passa pelo botão comum; `ccButtonSet` é separado. Ainda falta associar o registro ativo à lista de imagens, reconciliar paths lógicos com o CPK, medir bounds/hitboxes e comprovar visual/toque no S24. Evidência em `docs/WIDESCREEN_NATIVE_ASSET_BINDINGS_20261026.md` e nos decompilados `ghidra-tutorial-*-output.txt` e `ghidra-common-touch-input2-output.txt`.

