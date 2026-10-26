# Validação e limites

## Feito nesta investigação

- Confirmado com `llvm-readelf -h -n`: ELF64, `DYN`, AArch64 e Build ID `c3e506f9be350dfb4a00c79228754028`.
- Calculado SHA-256 do ELF local: `AD9B07806ED2C0A9BA4FBB2DA9D0B680BD5998880A8A166F862D6CB9E38475D2`.
- Importado o ELF em Ghidra 12.1.4 headless com autoanálise desligada; confirmado loader base `0x100000` e comparadas instruções nos endereços Ghidra ajustados com `llvm-objdump` e o tombstone. Projeto temporário: `%TEMP%\naruto-ghidra-12.1.4\project_noanalysis\NarutoStorm.gpr`; release oficial: [Ghidra 12.1.4](https://github.com/NationalSecurityAgency/ghidra/releases/tag/Ghidra_12.1.4_build).
- ADB confirmou SM-S921B, Android 17 / SDK 37, ABI arm64-v8a. `dumpsys package` mostrou versão 1.2.10 / code 38 e ausência da flag `DEBUGGABLE`.
- `cmd gpu vkjson` confirmou Samsung Xclipse 940, API Vulkan 1.3.304, driver Samsung Proprietary/SPAL 25.3.3 e suporte a `VK_KHR_swapchain`.
- `naruto-s24.log` foi cruzado por PID/thread/timestamp: avisos de formato às `.815`, erros internos de imagem PAL às `.824`, abort às `.829`. É evidência sobre a execução gravada, não uma captura de `VkResult`.
- Nenhum APK, biblioteca instalada ou arquivo do jogo foi alterado. Foram criados somente estes relatórios.

## Não validado / pendências

- A autoanálise Ghidra completa não foi concluída: `GccExceptionAnalyzer` emitiu grande volume de erros em LSDAs. A listagem foi feita com autoanálise desligada; pseudocódigo dessa sessão não é base para conclusões.
- Não foram obtidos capabilities da superfície Android vinculada à janela do jogo; `vkjson` não os expõe.
- Não houve instrumentação em runtime dos retornos `VkResult`, execução de patch, build, teste de falha parcial ou validação de renderização. Nenhum patch é declarado funcional.
- A origem exata da primeira falha e uma correção de compatibilidade permanecem em aberto.

## Evidências usadas

Arquivos locais: `crash.txt`, `naruto-s24.log`, `initialize-render.asm`, `create-swapchain.asm`, `libultimateninjastorm.so`. Referência: [README de engenharia reversa](https://github.com/apostolicfidei21/naruto-storm-android-reverse-engineering). Regras de compatibilidade: [VkSurfaceCapabilitiesKHR](https://docs.vulkan.org/refpages/latest/refpages/source/VkSurfaceCapabilitiesKHR.html) e [VkSwapchainCreateInfoKHR](https://docs.vulkan.org/refpages/latest/refpages/source/VkSwapchainCreateInfoKHR.html).
