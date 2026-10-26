# Root cause — Naruto Storm no Galaxy S24

## Conclusão

**Causa imediata comprovada:** o processo aborta porque `pthread_join()` recebe um `pthread_t` inválido durante `mmRenderManager_Vulkan::Finalize()`. O crash acontece enquanto `mmGPUDevice_Android::InitializeRenderSystem()` executa limpeza em seu caminho de falha.

**Causa anterior ainda não identificada:** o tombstone e a desmontagem não mostram qual operação Vulkan falhou nem seu `VkResult`. Portanto, ainda não há evidência para atribuir a falha ao Exynos, ao driver ou a um parâmetro específico do swapchain.

## Evidência observada

- `crash.txt`: `SIGABRT`, mensagem `invalid pthread_t 0x2e79616c702e6469 passed to pthread_join`; a pilha passa por `mmThread_Impl::WaitForEnd()`, `mmRenderManager_Vulkan::Finalize()`, `mmGPUDevice_Android::Finalize()` e `InitializeRenderSystem()`.
- `naruto-s24.log` (execução de 23:36:34): às `.815`, o processo registra `GPU do not support native format(3)`; às `.824`, o driver PAL registra quatro `Invalid format 0` e `CreateInternalImage failed -1`; às `.829`, ocorre o `pthread_join` inválido. É uma correlação temporal forte com criação/formato de imagem, mas `-1` é resultado interno PAL, não o `VkResult` da chamada Vulkan do jogo.
- O endereço de retorno `0xD37A10` fica no handler de exceção de `InitializeRenderSystem`; a desmontagem em `initialize-render.asm` mostra a chamada indireta de finalização nesse endereço.
- Ghidra 12.1.4 importou o ELF headless; a listagem corrigida confirma `InitializeRenderSystem` em endereço Ghidra `0xE3783C` (base de imagem `+0x100000` em relação ao endereço ELF `0xD3783C`), com cleanup no endereço Ghidra `0xE37A10`.
- O README da referência descreve quatro operações abrangidas pelo try: `CreateVulkanInstance`, `InitializeVulkanDevice`, `vmaCreateAllocator` e `mmRenderManager_Vulkan::Initialize`. A sequência estática também põe `CreateSwapchain` antes do início das threads de renderização. Isso torna coerente que a limpeza tente aguardar uma thread ainda não iniciada; não prova a origem do valor inválido.
- No assembly local, `vmaCreateAllocator` tem tratamento explícito de retorno não zero (limpeza e retorno `0x80000000`). Isso o distingue de uma exceção Vulkan e reduz sua prioridade como origem do `pthread_join` observado.
- A hipótese de que `pthread_create()` falhou para a primeira thread do renderizador não explica esse caminho: a referência situa os `Start()` depois da criação dos recursos gráficos. O identificador inválido pode decorrer de uma limpeza prematura, mas a escrita/estado do campo não foi observado em runtime.

## Hipóteses abertas

1. Uma chamada de WSI/renderer tenta criar imagem com formato inválido/não suportado; a proximidade dos logs PAL a torna a hipótese prioritária, sem provar que o formato veio do swapchain.
2. `vkCreateSwapchainKHR` retorna erro (o assembly testa `w0` e desvia ao bloco ELF `0x11AF374` / Ghidra `0x12AF374`), ou a consulta/criação subsequente das imagens falha.
3. Outra chamada encapsulada em `CreateVulkanInstance`, `InitializeVulkanDevice` ou `mmRenderManager_Vulkan::Initialize` converte um erro em exceção C++.

Os resíduos ASCII no `pthread_t` sugerem campo não inicializado ou memória sobrescrita; isso é uma inferência, não prova de corrupção pelo Play Core.

## Estado da investigação

- **Comprovado:** crash de limpeza em `pthread_join`, chamada pela rota de tratamento de falha gráfico.
- **Não comprovado:** primeira chamada Vulkan com erro, código de retorno, causa do erro e correção funcional.
- **Próximo dado decisivo:** primeiro `VkResult != VK_SUCCESS`, identificado junto à função Vulkan e ao respectivo `VkSurfaceCapabilitiesKHR`.

Fontes locais: `crash.txt`, `initialize-render.asm`, `create-swapchain.asm`. Referência de análise: [README do projeto](https://github.com/apostolicfidei21/naruto-storm-android-reverse-engineering).
