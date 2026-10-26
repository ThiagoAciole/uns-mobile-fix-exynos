# Análise Vulkan

## Identidade do binário e do aparelho

| Item | Observação |
|---|---|
| ELF | `libultimateninjastorm.so`, ELF64, AArch64, shared object |
| Build ID | `c3e506f9be350dfb4a00c79228754028` — confirmado por `llvm-readelf -h -n` |
| SHA-256 do ELF local | `AD9B07806ED2C0A9BA4FBB2DA9D0B680BD5998880A8A166F862D6CB9E38475D2` |
| Aparelho via ADB | Samsung SM-S921B / `e1s`, Android 17 / SDK 37, ABI `arm64-v8a` |
| Vulkan via `cmd gpu vkjson` | Samsung Xclipse 940, API 1.3.304, driver Samsung Proprietary / SPAL 25.3.3 (`9d9e5e5dc2`), extensão de dispositivo `VK_KHR_swapchain` presente |

## Logs do caminho de falha

Na execução registrada em `naruto-s24.log`, processo `17150`, thread `17199`: o jogo emite `GPU do not support native format(3)` em `23:36:34.815`; o PAL emite quatro `Invalid format 0` e `CreateInternalImage failed -1` em `.824`; o abort por `pthread_join` ocorre em `.829`. Isso direciona a próxima captura para `vkCreateSwapchainKHR`, `vkGetSwapchainImagesKHR` e `vkCreateImage`, além das quatro etapas do try. O `-1` da PAL é log do backend do driver e não identifica, por si só, um `VkResult` nem a função Vulkan pública que o provocou.

## Endereços

Os endereços são coordenadas da imagem ELF examinada. O tombstone registra offset APK de `0x140000`; os PCs do backtrace são offsets relativos à biblioteca dentro do APK. O `Build ID` coincide com o ELF local, então `0xD3783C` e `0x11AE91C` podem ser comparados diretamente com os rótulos de `.text` das desmontagens fornecidas.

| Endereço | Resultado da conferência |
|---|---|
| `0xD3783C` (Ghidra `0xE3783C`) | `mmGPUDevice_Android::InitializeRenderSystem` |
| `0x11AE91C` (Ghidra `0x12AE91C`) | `mmRenderManager_Vulkan::CreateSwapchain` |
| `0x11AEB58` (Ghidra `0x12AEB58`) | chamada `vkGetPhysicalDeviceSurfaceCapabilitiesKHR` |
| `0x11AEBEC` (Ghidra `0x12AEBEC`) | chamada `vkCreateSwapchainKHR`; `x0=device`, `x1=&createInfo`, `x2=null allocator`, `x3=&swapchain`; retorno `w0` testado em ELF `0x11AEBF0` / Ghidra `0x12AEBF0` |

**Ghidra:** o REA não oferece importação deste ELF no host Windows. Para cumprir a análise estática, Ghidra 12.1.4 foi obtido da release oficial com o SHA-256 publicado verificado e o ELF foi importado em projeto headless, sem alterar o binário. O loader aplicou base `0x100000`, então a coordenada Ghidra é a coordenada ELF + `0x100000`. A listagem ajustada confirma os callsites e o teste do retorno. A autoanálise completa não foi aproveitada: `GccExceptionAnalyzer` emitiu grande volume de erros ao percorrer LSDAs e o processo foi interrompido; pseudocódigo dessa sessão não é tratado como evidência. O desvio após `vkCreateSwapchainKHR` chega ao bloco de erro em Ghidra `0x12AF374`, mas o log não revela o retorno observado.

## `InitializeRenderSystem` e operações no caminho protegido

O assembly local e a listagem Ghidra em base `+0x100000` confirmam as chamadas e a ordem, a partir de ELF `0xD378A8` / Ghidra `0xE378A8`:

1. `CreateVulkanInstance()` em `0xD378AC`.
2. `InitializeVulkanDevice()` em `0xD378B4`.
3. `vmaCreateAllocator()` em `0xD37918`; o código testa o retorno e, se não zero, finaliza e retorna `0x80000000`.
4. `mmRenderManager_Vulkan::Initialize()` em `0xD37940`; essa rotina inicia os recursos WSI, inclusive superfície/swapchain.

A região de exceção/landing pad em `0xD379F0` é também descrita no README de referência. O handler chama `Finalize()` via vtable em `0xD37A10`, endereço de retorno que aparece no tombstone. A desmontagem comprova esse caminho de limpeza, mas não nomeia o objeto de exceção ou o `VkResult` original.

## Parâmetros observáveis do swapchain

Antes da criação, a função consulta `vkGetPhysicalDeviceSurfaceFormatsKHR` (ELF `0x11AE9A8`/`0x11AE9C4`) e `vkGetPhysicalDeviceSurfaceCapabilitiesKHR` (ELF `0x11AEB58`); o retorno não zero da última vai para o handler em `0x11AF2D8`. `vkCreateSwapchainKHR` em `0x11AEBEC` também tem teste do retorno; valor não zero vai para `0x11AF374`. Portanto, o primeiro erro pode ocorrer nas consultas WSI, na criação do swapchain ou na criação subsequente das imagens; a análise estática não distingue qual aconteceu no aparelho.

Na chamada ELF `0x11AEBEC` / Ghidra `0x12AEBEC`, a estrutura começa em `sp+0x60`. A listagem confirma `sType`, `pNext=null`, `flags=0`, superfície, contagem derivada de `minImageCount`, formato/cor vindos do primeiro `VkSurfaceFormatKHR`, dimensões próprias, `imageArrayLayers=1`, compartilhamento exclusivo, fila sem índices e `oldSwapchain=null`. Os literais/campos restantes abaixo vêm do README da referência; não foram decompilados de modo confiável nesta sessão:

| Campo indicado | Valor/seleção reportado | Regra que precisa ser confrontada |
|---|---|---|
| `minImageCount` | `minImageCount + 1`, limitado se `maxImageCount != 0` | faixa de imagens da superfície |
| `imageFormat`, `imageColorSpace` | primeiro formato retornado | par precisa ser retornado para essa superfície |
| `imageExtent` | `s_deviceWidth × s_deviceHeight` | `currentExtent` ou faixa `[minImageExtent,maxImageExtent]`; dimensões não podem ser zero |
| `imageArrayLayers` | `1` | não exceder `maxImageArrayLayers` |
| `imageUsage` | `19`: `COLOR_ATTACHMENT(16) | TRANSFER_SRC(1) | TRANSFER_DST(2)` | subconjunto de `supportedUsageFlags` |
| `preTransform` | `IDENTITY(1)` | precisa estar em `supportedTransforms`; `currentTransform` é alternativa compatível usual |
| `compositeAlpha` | `INHERIT(8)` | precisa estar em `supportedCompositeAlpha` |
| `presentMode` | `FIFO(2)` | precisa constar nos modos reportados; FIFO é requisito básico de WSI |
| `clipped` | `true` | booleano; não depende de capacidade de superfície listada acima |

O `VkSurfaceCapabilitiesKHR` também contém `minImageCount`, `maxImageCount`, `currentExtent`, `minImageExtent`, `maxImageExtent`, `maxImageArrayLayers`, `supportedTransforms`, `currentTransform`, `supportedCompositeAlpha` e `supportedUsageFlags`. A especificação exige que usage seja subconjunto, transform e alpha sejam suportados, extent respeite os limites, e present mode esteja disponível ([capabilities](https://docs.vulkan.org/refpages/latest/refpages/source/VkSurfaceCapabilitiesKHR.html), [criação](https://docs.vulkan.org/refpages/latest/refpages/source/VkSwapchainCreateInfoKHR.html)).

## Comparação com o S24

`cmd gpu vkjson` comprova dispositivo, versão de API, driver e extensão `VK_KHR_swapchain`; ele não cria a `VkSurfaceKHR` da janela do jogo e não retorna as capacidades da superfície. Portanto, **não é possível afirmar neste momento** se usage 19, `INHERIT`, `IDENTITY`, extent ou formato são aceitos no S24. A presença da extensão de swapchain tampouco prova que a criação de um swapchain para esta janela terá sucesso.

## Evidência ainda necessária

Capturar no mesmo processo/janela: `VkSurfaceCapabilitiesKHR` integral, formatos, present modes, `VkSwapchainCreateInfoKHR` efetivamente passado e o primeiro retorno de erro entre `vkCreateInstance`, `vkCreateDevice`, criação da superfície, consultas WSI e `vkCreateSwapchainKHR`. A entrada `vkCreateSwapchainKHR` já está identificada em `0x11AEBEC`.
