# GameSir-X5 Lite no S24 — habilitação e validação

## Resultado funcional

Em 27/10/2026, o usuário confirmou que o candidato com a máscara `0x23` funcionou **nos menus e na batalha**. Em seguida, confirmou que o controle voltou a funcionar após desconectar e reconectar, **sem fechar o jogo**. O aparelho é o Galaxy S24 SM-S921B; o controle é o GameSir-X5 Lite por USB/OTG.

O candidato instrumentado passou nesses testes. Depois, a versão de uso, com a mesma habilitação e sem os hooks de diagnóstico, foi instalada por atualização; o usuário confirmou: **“Sim, continua funcionando”**. Essa versão ficou instalada no S24. Não extrapolar estes resultados para outros controles, aparelhos ou cobertura completa do jogo.

## Causa e menor mudança aplicada

O jogo sobrescrevia a máscara de inicialização com `0x22`, que seleciona teclado e toque, sem gamepad. A conversão para os dispositivos Android resulta em `0x14`. A recriação da entrada finaliza o gerenciador anterior quando existe, incluindo `Paddleboat_destroy`, e cria a entrada nova sem controle.

O patch reproduz a gravação original em `androidMain` e aplica OR com 1 **somente ao inteiro local da máscara**: `0x22 → 0x23`. A máscara Android passa a `0x15`, acrescentando controle e preservando teclado/toque. A constante compartilhada em `.rodata` e o campo adjacente de memória não são modificados. Referências: [análise da máscara](CONTROLLER_MASK_FINDINGS_20261027.md) e [histórico das capturas](CONTROLLER_INVESTIGATION_20261027.md).

O stub mantém `x9`, SP, LR, flags e os demais registradores usados no trecho. A versão sem logs modifica apenas a instrução em VA `0xCEEFD4` e 28 bytes em VA `0x9B134C`, após os stubs widescreen. As funções originais de processamento de eventos e leitura de dados permanecem intactas nessa versão.

## Evidência no aparelho

| Rodada | Observação |
|---|---|
| Diagnóstico antes da habilitação, 60 s | 442 eventos identificados do GameSir, todos com retorno 0; nenhuma leitura no callsite instrumentado de dados. Usuário confirmou ausência de resposta. |
| Candidato `0x23`, 90 s | 212 eventos do GameSir: 172 tratados e 40 não tratados. Houve **1.138 leituras de dados, todas com retorno 0 (sucesso)**, incluindo máscaras de botões não zero. O hook não registra keycode/action, portanto os 40 retornos não tratados não foram classificados individualmente. |
| Teste funcional | Usuário: “Funcionou nos menus e na batalha”. Logs normais também registraram `GameControllerThread: registerInputDeviceListener`, ausente no diagnóstico anterior. |
| Segunda captura, 60 s | 1.332 leituras de dados com retorno de sucesso. Usuário: “Reconectei; voltou a funcionar”, em resposta ao teste de reconexão sem fechar o jogo. A confirmação de reconexão é evidência do usuário; os eventos de remoção/adição não foram correlacionados individualmente nos logs retidos. |
| Falhas fatais nas janelas capturadas | Zero marcadores `FATAL EXCEPTION`/`Fatal signal` nos logs filtrados. Isso não é ensaio prolongado de estabilidade nem medição de FPS/latência. |

As contagens são de chamadas e leituras de estado, não de pressionamentos completos. As capturas estão em `work/controls-mask-test-20261027/runtime-131704/` e `runtime-131919/`, com os resultados visuais informados pelo usuário nos respectivos `summary.json`.

A primeira tentativa dessa rodada foi encerrada por um erro no script local de captura: a variável da duração havia sido sobrescrita pela lista de argumentos do logcat. A variável foi corrigida e a captura válida de 90 s foi iniciada em seguida. Esse erro não alterou o APK nem os dados do aplicativo.

## Versão sem instrumentação

Geração da biblioteca a partir do APK de uso preservado:

```powershell
python -B scripts/patch-controls-flow-diag.py --apk "build/UNSM-S24-FIX-PTBR-EN-v2.apk" --enable-gamepad --no-flow-logs --output "work/NOVA-RODADA/libultimateninjastorm.so"
python -B scripts/test-controls-flow-diag.py
```

O script exige o hash da biblioteca S24 conhecida, Build ID e bytes originais; verifica o espaço executável e recusa sobrescritas. A biblioteca desta rodada tem SHA-256 `2923DB436931BB2F3A0B7178A7B1C007434E28D269E5EC5A81C5BE4A73E96DB7`. Não contém a tag `CTRLFLOW`. Os primeiros 24 bytes do stub são idênticos aos da versão instrumentada; os branches de ambas retornam ao mesmo VA `0xCEEFD8`.

**Cinco testes de host passaram**, incluindo recusa de entrada divergente/já alterada, proteção de saída, preservação dos stubs widescreen e da constante compartilhada, reversão byte a byte e ausência dos hooks/tag de logging na versão de uso. O teste novo foi observado falhando antes da implementação. As instruções ARM64 foram conferidas por disassembly.

O repack usa a mesma base pt-BR/inglês e substitui somente a biblioteca nativa. A assinatura é comparada à da base; alinhamento de 16 KiB, hash instalado e limpeza do temporário fazem parte da instalação. Não houve desinstalação ou limpeza de dados. Os APKs de uso anteriores não são sobrescritos. O único caminho temporário reutilizado é `work/build-tmp-controls-flow-20261027-01`, cuja limpeza já foi autorizada pelo usuário.

Manifestos e resultados da versão sem logs ficam em `work/controls-gamepad-clean-20261027/`. O APK temporário não é retido após instalação e conferência; a reprodução usa a base preservada, o script, os stubs e o manifesto. Atualização posterior: o build seletivo agora tem o modo `--controller-base-apk <APK-S24> --controls`, que exige a biblioteca `8797E444…` e aplica o patch sem logs. A cadeia foi validada por hash/`--check-only`, mas não foi executada como repack/assinatura nesta rodada. O caminho com `--apk` original continua recusando `--controls`, porque seu widescreen padrão gera outra biblioteca.

## Instalação final aceita

- APK instalado: SHA-256 `A9288675A6D66B235349F1B20B81E9ADF95CD9FA6AEB69B2811138D14BFD32FD`, conferido no aparelho contra o arquivo assinado antes da limpeza.
- Biblioteca nativa: SHA-256 `2923DB436931BB2F3A0B7178A7B1C007434E28D269E5EC5A81C5BE4A73E96DB7`, com habilitação de 28 bytes e sem `CTRLFLOW`.
- Alinhamento de 16 KiB, assinatura e igualdade do certificado com a base: aprovados. Os demais payloads mantiveram CRC/tamanho, incluindo pt-BR/inglês.
- Método: atualização `adb install --no-incremental -r --user 0`; sem desinstalação ou limpeza de dados. O usuário confirmou resposta do controle na versão final; não foi feita comparação independente dos arquivos de save.
- Limpeza: pasta temporária autorizada removida; APKs anteriores preservados. A versão final ficou instalada, sem restaurar a base que desabilitava o gamepad. `acceptance.json` registra o aceite e os sinais do log retido do processo final.

## Ocorrência na primeira abertura

A primeira abertura da versão sem logs, PID `25166`, terminou em `SIGSEGV` após aproximadamente 2 segundos. O backtrace situa a falha em `libvulkan.so`, `vulkan::driver::CreateAndroidSurfaceKHR +232`, com leitura de ponteiro nulo no endereço `0x98`. Os frames do jogo passam por `mmRenderManager_Vulkan::CreateSurface`, `Initialize`, `nuccSys::InitRender` e `libnucc_Init`.

O usuário reabriu o jogo e confirmou o funcionamento. O processo corrente conferido, PID `26262`, apresentou listener registrado, zero mensagens `CTRLFLOW` e zero marcadores fatais no seu log retido. O aceite funcional do controle permanece válido, mas **não se afirma estabilidade de abertura**. A causa dessa ocorrência e sua relação com a atualização não foram determinadas; não foi repetido um teste de abertura contra a base sem gamepad.

Evidências privadas: `startup-crash-buffer.log`, `accepted-game-process.log`, `accepted-current-process-26262.log` e `acceptance.json` em `work/controls-gamepad-clean-20261027/`. Não foi aplicado patch adicional de renderização nesta tarefa.
