# Plano de correção

## Estratégia

Não remover `pthread_join()`. Corrigir o ciclo de vida incompleto e corrigir a incompatibilidade Vulkan que vier a ser demonstrada, em mudanças separadas.

1. Instrumentar cada etapa de criação Vulkan e registrar nome da operação, argumentos relevantes e `VkResult` antes de qualquer conversão para exceção. Registrar também a exceção C++ no catch, sem depender de texto de log do driver.
2. Fazer a limpeza usar estado explícito de inicialização por recurso/thread. Só executar `WaitForEnd()` para thread cujo `Start()`/`pthread_create()` confirmou sucesso; inicializar handle/flags a estado sentinela. Tornar `Finalize()` seguro para execução parcial e repetida, destruindo somente recursos válidos e na ordem inversa de criação.
3. Se a captura apontar falha de WSI, selecionar parâmetros a partir das capacidades reais: clamp de extent apenas quando `currentExtent` for variável; uso de `currentExtent` quando definido; selecionar somente flags de `imageUsage` necessárias e suportadas; escolher `preTransform`/alpha dentre os bits suportados; escolher formato e modo retornados. Preservar uso de transfer se o restante do renderer realmente o exige.
4. Exercitar falha induzida após cada etapa e verificar que o retorno original é preservado, cleanup não dá abort, handles válidos são destruídos uma vez, e o caso de sucesso continua inicializando e apresentando quadros.

## Instrumentação proposta

Preferência: build de diagnóstico controlada ou instrumentação nativa sem substituir a instalação oficial. Em dispositivo de teste com acesso suficiente, Frida pode interceptar `vkCreateInstance`, `vkCreateDevice`, `vkCreateAndroidSurfaceKHR`, `vkGetPhysicalDeviceSurfaceCapabilitiesKHR`, consultas de formatos/modos, `vkCreateSwapchainKHR`, `vkGetSwapchainImagesKHR` e `vkCreateImage`, gravando `VkResult` no retorno e argumentos/estruturas na entrada. Priorizar swapchain/imagens pelos erros PAL correlatos no log. Interceptar também `__cxa_throw` com stack trace identifica onde um erro vira exceção. Validar que os hooks veem as chamadas; se necessário, hookar a chamada PLT de swapchain em `0x11AEBEC`.

O pacote no aparelho não tem a flag `DEBUGGABLE`, o Android é `user/release-keys` e `adb shell id` é `shell`, sem root. As regras Android 17 vedam camadas externas e tracing/interceptação de apps não debuggable salvo metadata explícita `com.android.graphics.injectLayers.enable`; a instalação original não deve ser modificada para habilitá-la ([requisito Android 17](https://source.android.com/docs/compatibility/17/android-17-cdd)). Portanto, sem root, build de diagnóstico autorizado ou camada OEM, instrumentação dinâmica no S24 atual não está disponível. `cmd gpu vkjson` não revela capacidades da superfície do jogo.

## Critério para aprovar patch

Não alterar o ELF/APK original. Só escolher uma correção de swapchain depois de capturar o primeiro `VkResult` e comparar os parâmetros efetivamente passados com capabilities da mesma superfície. Uma alteração de limpeza pode ser preparada depois de validar a estrutura do estado das threads; não remover o join indiscriminadamente, pois isso pode deixar threads ativas usando recursos liberados.
