# Controle externo — retomada estática em 27/10/2026

**Resultado posterior:** a máscara `0x22`, que desabilitava o gamepad, foi habilitada localmente para `0x23`. O usuário validou menus, batalha e reconexão no S24; a versão sem logs foi instalada e aceita. Ver [validação final](CONTROLLER_S24_VALIDATION_20261027.md) e [análise da máscara](CONTROLLER_MASK_FINDINGS_20261027.md). O restante deste documento mantém o histórico anterior à correção.

## Resultado

O jogo contém uma cadeia de entrada nativa para gamepad, incluindo processamento de eventos, conexão, leitura de botões/eixos e consumo pelos menus. Esta rodada esclareceu o fluxo e corrigiu uma hipótese anterior; **não identificou a causa definitiva nem produziu patch de suporte a controle**.

Após a solicitação do usuário para continuar somente a análise estática, não foram realizados novos testes no aparelho. Nenhum APK foi gerado, instalado ou substituído; nenhum dado do jogo foi alterado.

## Identidade e evidências

- Entrada original: `work/external-single-1.2.10/libultimateninjastorm.so`, SHA-256 `C631E7127E73ECDE32DA7C8B8054AC6810A375875CD00749D3F4DF5DB29DB79E`, Build ID `c3e506f9be350dfb4a00c79228754028`.
- Os dois APKs presentes, `build/UNSM-S24-FIX.apk` e `build/UNSM-S24-FIX-PTBR-EN-v2.apk`, contêm biblioteca nativa com SHA-256 `8797E4446449B505BD20D704C4123F4BDBEDEEC8B9E1E71A87414A876572CFD0`. Os seis intervalos de controle comparados são idênticos à entrada original. Isso não prova qual APK está instalado.
- O nome documentado `build/Naruto Ultimate Ninja Storm.apk` não estava presente nesta rodada. Não foi recriado nem houve renomeação dos arquivos disponíveis.
- Evidências locais em `work/controls-investigation-20261027/`: disassembly focado, `branches.json`, `vtables.json` e `available-build-comparison.json`. Conteúdo de `work/` permanece privado e fora do Git.
- Método: LLVM do NDK 27.2, leitura de seções ELF/dynsym/RELA e varredura de instruções AArch64 `B`/`BL` em `.text`, sem dependências novas. Endereços abaixo são VAs ELF; nos intervalos de código examinados, offset de arquivo = VA − `0x4000`. Logs antigos do Ghidra usam base adicional de `0x100000`.

## Fluxo confirmado no binário

| Etapa | Localização | Evidência e limite |
|---|---|---|
| Inicialização | `mmInput::Initialize` em `0xCFCCC8`; `mmControllerManager_Android::Initialize` em `0x1188120` | O inicializador genérico chama o slot de inicialização do gerenciador existente. `Paddleboat_init` é chamado em `0x118814C`; `Paddleboat_isInitialized`, em `0x1188150`. Ambos os retornos são descartados. Não há prova de sucesso em execução. |
| Atualização | `mmInput::Update` em `0x1187BC0` | Chama a plataforma por vtable em `0x1187C0C`; depois, atualiza o controle quando o bit 0 da máscara está ativo e o gerenciador existe. `mmPlatformLibrary::Update`, em `0x118CD48`, fornece máscara `0x1F`. A execução desses caminhos não foi observada nesta rodada. |
| Retirada da fila | `mmInput_Android::UpdatePlatform` em `0x9E7B54` | Processa eventos pendentes de ciclo de vida, consulta `AInputQueue_getEvent`, chama `AInputQueue_preDispatchEvent` e, se este retornar zero, entrega o evento ao gerenciador em `0x9E7BD0` ou `0x9E7C60`. Há chamadas a `AInputQueue_finishEvent` em `0x9E7C30` e `0x9E7CBC`. Se predispatch retornar diferente de zero, segue para outro evento sem finalizar esse evento nesse caminho. Não se conclui que isso seja defeito sem observar o retorno e a redistribuição pelo Android. |
| Entrega ao Paddleboat | `NotifyInputEvent` em `0x9E7D38` | Encaminha `AInputEvent*` a `Paddleboat_processInputEvent` em `0x9E7D40`. Retorna verdadeiro somente quando Paddleboat retorna 1. O chamador foi identificado; não há uma chamada ausente a adicionar com base nesta evidência. |
| Aceitação do evento | `paddleboat::GameControllerManager::processInputEvent` em `0x1189110` | Exige instância do gerenciador, fonte compatível e correspondência do device ID com um slot elegível. Sem correspondência, retorna zero. Encaminha teclas e movimento por caminhos próprios. Os valores reais dessas condições continuam desconhecidos. |
| Conexão e leitura | `ControllerStatusCallback` em `0x11881CC`; `Update` em `0x931550`; `mmController_Android::Update` em `0x93160C` | O callback atualiza conexão e índice. A atualização chama `Paddleboat_update`; o controle conectado consulta `Paddleboat_getControllerData` em `0x931670`. Quando essa consulta retorna zero, usa os dados de botões e eixos. |
| Consumo no menu | `ccMenuPad::Ctrl` em `0x9A05E0` | Percorre índices configurados, aplica o mapa de IDs e chama `nuccSys::GetControllerActiveUser` em `0x9A0638`, com argumento 2. A função em `0x99E990` seleciona um estado de 96 bytes usando mapa de usuário, modo e índice ativo. A semântica exata do argumento 2 e o estado efetivo no menu ainda precisam ser rastreados; não foi interpretado como bloqueio de gamepad. |

## Correção da hipótese de vtable

`_ZTV16nummInputManager` está em `0x139D6D0` e tem **32 bytes**, segundo `.dynsym`. Depois dos dois campos de cabeçalho, os únicos slots são os destrutores em `0xF75638` e `0xF75730`. `IsControllerConnected`, em `0xF75194`, não está nessa tabela.

O script antigo `work/tools/ControlCallers.java` percorria `0x80` bytes a partir da tabela. Assim, parte do que foi listado como slots pertencia a dados posteriores ao símbolo. Não se deve usar esses valores como prova de métodos virtuais.

A varredura não encontrou `B`/`BL` para `IsControllerConnected` nem relocação RELA cujo símbolo ou destino resolvido fosse essa função. Isso limita a utilidade de instrumentar apenas sua entrada; **não prova ausência de lógica equivalente inline, referências construídas em execução ou outros caminhos indiretos**.

Os oito campos consultados pela função são `+0x74`, `+0x134`, `+0x1F4`, `+0x2B4`, `+0x374`, `+0x434`, `+0x4F4` e `+0x5B4`. Ela retorna verdadeiro quando pelo menos um deles é zero. Essa convenção difere do byte de conexão de `mmController_Android`, onde não zero indica conexão; os dois níveis não devem ser confundidos.

## Limites do diagnóstico existente

`python -B scripts/patch-controls-diag.py --check-only` passou: montou os stubs, verificou entrada/Build ID/bytes e tamanho da cave, sem gravar biblioteca ou APK. Isso verifica a construção do diagnóstico, não seu comportamento no Android.

O diagnóstico atual registra o ponteiro antes de `Paddleboat_processInputEvent` e os campos de `IsControllerConnected`. Ele não registra o sucesso da inicialização, o retorno de predispatch, a aceitação do evento, o callback de conexão nem o resultado de leitura do controle. Portanto, silêncio no hook de conexão não basta para concluir que o controle não foi detectado.

Além disso, a entrada aceita por esse script é a biblioteca **somente com Exynos**, e a cave desativa `DrawLetterBox`. Ele não é um diagnóstico integrado à biblioteca widescreen atualmente disponível. Não instalar esse resultado como substituto do APK de uso.

## Próxima investigação recomendada

1. **Estática:** continuar do caminho de consumo descrito abaixo para rastrear a máscara de dispositivos e as alterações dos mapas de slots. O campo `+0xB44` é usado como quantidade de slots e como índice do estado de fallback; não foi comprovado como índice do controle físico ativo.
2. **Quando testes no aparelho forem autorizados:** preparar instrumentação compatível com a biblioteca de uso para capturar init/isInitialized, retirada/predispatch/finalização, device ID/fonte/tipo, retorno do Paddleboat, callback e leitura de botões/eixos. Preservar o APK aceito, pt-BR/inglês, widescreen, Exynos e progresso.
3. **Somente após localizar a falha:** escolher o menor patch. Se eventos chegam com dados válidos, investigar seleção/mapeamento; se não chegam, investigar fila/ciclo de vida; se init falha, investigar sua causa. Não forçar conexão nem converter gamepad em toque sem evidência que justifique a mudança.

O aceite continua sendo navegar nos menus e jogar com o controle físico no S24. Esta rodada não atende esse aceite.

## Continuação: teste anterior informado e caminho de consumo

O usuário forneceu o resumo de uma captura anterior em batalha: **827 eventos em 30 segundos, zero entradas observadas em `IsControllerConnected` e zero crashes detectados**. São resultados históricos informados pelo usuário; os logs brutos desse teste não foram revalidados nesta continuação. Zero crashes nessa janela não equivale a estabilidade geral.

Se o contador foi obtido com `nie_hook` de `patches/controls-diag/stubs.S`, ele registra apenas `input_event ptr=%p`, **antes** da chamada à Paddleboat. O chamador entrega os eventos da fila antes de separar toque/teclado, e o hook não registra fonte, tipo, device ID nem resultado. Portanto, o contador comprova entradas nesse ponto de instrumentação, mas não identifica quantas vieram do GameSir, quantas foram aceitas e quantas produziram dados válidos. A hipótese de perda depois da recepção permanece plausível, sem excluir recusa dentro da Paddleboat.

### Caminho alternativo confirmado estaticamente

| Ponto | Evidência |
|---|---|
| Atualização do sistema | `nuccSys::MainStart` chama `UpdateInputDevice` em `0x9AA154`. Esta rotina chama `nummInputUpdateEx` em `0x9AAAA4` usando a máscara armazenada em `+0xADC`. |
| Conversão por slot | `nummInputManager::UpdateDevice`, em `0xF75540`, chama `nummController::Update` para os oito slots quando o bit 0 está ativo. Não depende de `IsControllerConnected`. |
| Conexão consultada diretamente | `nummController::Update`, em `0xF73C48`, obtém o dispositivo pelo ID em `+0x60` e lê diretamente o byte `mmController +0x8` em `0xF73C7C`. Grava status zero para conectado e `-1` para desconectado no próprio `+0x64`. Sem conexão, retorna sem converter botões. Isso explica como o motor verifica conexão sem executar o hook antigo. |
| Conversão de botões | Quando conectado, essa função converte cinco máscaras de botões usando uma tabela de 24 entradas e o mapper. Escreve as máscaras em `+0x70` a `+0x80` e converte os quatro eixos em valores inteiros. `nummController::Initialize`, em `0xC9431C`, registra 24 correspondências identidade; a hipótese de ausência completa de mapeamento padrão não é sustentada por esse inicializador. Alterações posteriores continuam possíveis. |
| Cópia para o consumidor | `InputInitialize`, em `0xCDB4A4`, define oito slots em `+0xB44`, aloca estados com passo `0x60` e monta em `+0xB00` o mapa obtido por `nummInputDeviceIndex(1, slot)`. `UpdateInputDevice` usa esse mapa para chamar `nummInputGetState`, diretamente em `0x9AAB0C` ou por acumulação em `0x9AABE4`, conforme `+0xB40`. |

O status `nummController +0x64` corresponde a `nummInputManager +0x74` no primeiro slot, pois o primeiro objeto começa em `manager +0x10`. Os campos vistos pelo diagnóstico antigo pertencem a essa camada de conversão, não ao byte físico consultado na atualização.

### Seleção de usuário: resultado e correção de interpretação

`SetInputActiveUser`, em `0xBF5F50`, escreve um valor de 16 bits em `nuccSys +0xAE0`. `Framework::Initialize` usa valor 2 em `0xCECB4C`; `ccStartMenu::Start`, em `0xCF31C8`, também usa 2; `ccGameDuel::LoadSetup`, em `0xBF6D64`, usa 2. `ccMenuPad::Ctrl` consulta `GetControllerActiveUser` com argumento 2. Nesses caminhos, **não há divergência estática entre o valor configurado e o consultado**; mudanças em execução não foram observadas.

O byte `+0xB44` vale inicialmente 8, limita os loops dos slots e seleciona o estado de fallback quando o modo de usuário não coincide ou o índice solicitado é `-1`. A interpretação anterior de que esse campo seria simplesmente o índice físico ativo era prematura. `+0xB10` é um mapa de associação consultado por `GetControllerActiveUser`; seus valores em execução ainda são desconhecidos.

O chamador de `InputInitialize` foi localizado em `nuccSys::Initialize`, em `0xCDC5BC`: repassa a máscara de `nuccInitParam +0x14`. Esta continuação não determinou o valor final dessa máscara após todas as configurações do jogo.

### Fronteira ainda sem prova

A ausência de chamadas a `IsControllerConnected` deixou de ser um indicador útil de falha. A instrumentação relevante passa a ser: fonte/device ID e retorno de `Paddleboat_processInputEvent`; callback de conexão; retorno e dados de `Paddleboat_getControllerData`; byte físico de conexão; máscara de atualização; máscaras antes/depois de `nummController::Update`; estado selecionado pelo consumidor. **Ainda não há evidência suficiente para escolher um patch.**

Disassembly e referências adicionais ficaram em `work/controls-investigation-20261027/consumer-branches.json` e nos arquivos `*-consumer.txt`. Nenhum teste novo no aparelho foi realizado nesta continuação.

## Captura no S24 após reconexão do GameSir

Após o usuário informar que o S24 estava com joystick e ADB de rede conectados, foi realizada uma nova captura passiva de 45 segundos. O jogo não estava em execução; foi aberto com `am start`, sem atualização, reinstalação, force-stop ou limpeza de dados. Pacote 1.2.10, versionCode 38; PID da sessão: `17840`. Não foi identificado por hash o APK instalado.

O Android reconheceu `GameSir-X5 Lite`, vendor `0x3537`, product `0x1116`, como `KEYBOARD | GAMEPAD | JOYSTICK | EXTERNAL`, controller number 1. O dispositivo físico estava em `/dev/input/event9`; o InputReader o agrupava com a interface Consumer Control sob device ID 30. Esses IDs são específicos desta conexão.

| Verificação nesta captura | Resultado |
|---|---|
| Entrada física de botões | 70 transições `EV_KEY`, incluindo pressionamentos e liberações de `BTN_GAMEPAD`, `BTN_NORTH`, `BTN_WEST`, `BTN_START` e `BTN_THUMBR`. Não equivale a 70 pressionamentos completos. |
| Entrada física de eixos | 614 atualizações `EV_ABS` em `ABS_X`, `ABS_Y`, `ABS_Z`, `ABS_RZ`, `ABS_HAT0X` e `ABS_HAT0Y`. |
| Fronteira Android/aplicativo | 175 mensagens `ViewPostIme key` no log filtrado pelo PID do Naruto. O canal atual do jogo terminou com `status=NORMAL, responsive=true`. Essas mensagens não revelam os valores internos da Paddleboat nem estabelecem correspondência um a um com os eventos físicos. |
| Resposta do jogo | O usuário confirmou que usou o controle e o jogo não respondeu. |
| Diagnóstico interno e falhas | Zero mensagens `CTRLDIAG` e zero marcadores `FATAL EXCEPTION`/`Fatal signal` no log do processo durante a captura. A ausência desses marcadores não é homologação de estabilidade nem prova de execução das rotinas de diagnóstico. |

Evidências privadas: `work/controls-live-20261027-121053/`, com manifesto, eventos físicos, log do processo, snapshots de entrada e `summary.json`. O bloco **Input Dispatcher State at time of last ANR** do `dumpsys` é histórico e foi separado do estado corrente; não deve ser apresentado como ANR desta sessão.

**Resultado:** o sintoma foi reproduzido com entrada física comprovada e canal Android responsivo. A aceitação por `Paddleboat_processInputEvent`, o retorno de `Paddleboat_getControllerData` e as máscaras convertidas ainda não foram observados. A próxima instrumentação deve medir esses pontos, preservando a biblioteca de uso e evitando a cave já ocupada pelo widescreen. Nenhum APK foi gerado ou instalado nesta captura.

## Diagnóstico de fluxo preparado

Implementação: `scripts/patch-controls-flow-diag.py` e `patches/controls-diag/flow-stubs.S`. O diagnóstico anterior permanece separado. O novo script lê a biblioteca diretamente do APK informado, exige o SHA-256 nativo `8797E444...`, valida Build ID, segmento executável, mapeamento VA/arquivo, o RET de `DrawLetterBox` e os bytes das duas chamadas substituídas. Também recusa branches diretos de endereços externos que entrem no intervalo reservado. Não gera, assina nem instala APK.

Os stubs ocupam **212 bytes**, de `0x9B134C` até `0x9B1420`, dentro do limite `0x9B145C`. Os 140 bytes anteriores usados pelo widescreen permanecem intactos. A entrada por `DrawLetterBox` continua desativada; os hooks são chamados somente nos dois callsites alterados. Nenhum cabeçalho, segmento ou relocação ELF foi modificado. O hash exato da entrada impede aplicação sobre variantes que já ocupem essa área, incluindo candidatos antigos com stubs de coverage.

| Hook e callsite | Log, significado e limite |
|---|---|
| `flow_event`, chamado em `0x9E7D40` | `event ret=%d src=%x dev=%d`: executa a chamada original e registra seu retorno, a fonte e o device ID do evento. `ret=1` é o valor que o wrapper original considera aceito. Permite separar eventos do GameSir de outros dispositivos, usando os IDs da conexão atual. Não registra keycode, tipo nem eixos. |
| `flow_data`, chamado em `0x931670` | `data ret=%d slot=%d buttons=%x`: executa a leitura original e, somente quando `ret=0`, lê a máscara de botões em `Paddleboat_Controller_Data +0x8`. Em erro, `buttons=0` é um placeholder, não uma leitura válida. Esse callsite só é alcançado se o byte de conexão do controle estiver ativo; silêncio nesse hook não prova ausência de atualização do motor. |

Ambos os hooks preservam os registradores callee-saved utilizados, LR, alinhamento de pilha e retorno inteiro original. Não escrevem no estado do evento ou no buffer do controle. Logging ocorre por evento e por leitura de frame, podendo acrescentar latência; é diagnóstico, não correção de jogabilidade. A validade desses cuidados foi inspecionada no assembly/disassembly, mas ainda não foi testada no Android.

Verificação sem saída:

```powershell
python -B scripts/patch-controls-flow-diag.py --apk "build/UNSM-S24-FIX-PTBR-EN-v2.apk" --check-only
python -B scripts/test-controls-flow-diag.py
```

Geração de biblioteca separada, com caminho novo:

```powershell
python -B scripts/patch-controls-flow-diag.py --apk "build/UNSM-S24-FIX-PTBR-EN-v2.apk" --output "work/controls-flow-diag-NOVA-RODADA/libultimateninjastorm.so"
```

A biblioteca desta rodada está em `work/controls-flow-diag-20261027/libultimateninjastorm.so`, com manifesto `.patch.json`. SHA-256 de saída: `521021BA96A8C3051B9446CFDA42A40203DFCE6390F0E860236A59809CDE001C`. Não repetir a geração no mesmo destino: o script recusa sobrescrita. O manifesto usa como `sourceSha256` a biblioteca do APK de entrada e pode ser consumido por `repack-native-apk.py` sobre esse mesmo APK, preservando pt-BR/inglês e os demais membros.

Validação de host: **3 testes passaram**. Conferem tamanho/cabeçalhos e preservação dos stubs widescreen; revertem os três intervalos modificados e exigem igualdade byte a byte com a entrada; recusam biblioteca diferente ou já diagnosticada; preservam saída existente e bloqueiam destino em `build/`. Montagem, limites da cave, chamadas ARM64, GOT de `__android_log_print` e hash da releitura também foram conferidos. Nenhum APK foi criado ou instalado nesta preparação.

Para a futura rodada no aparelho, ainda será necessário empacotar temporariamente e assinar o diagnóstico com o certificado compatível, instalar por atualização preservando dados e recolher a tag `CTRLFLOW`. Preservar os APKs de uso e obedecer às regras de arquivos temporários; a biblioteca sozinha não permite capturar os retornos no S24.

## Execução do diagnóstico no S24

O usuário autorizou instalar o diagnóstico e confirmou a limpeza somente de `work/build-tmp-controls-flow-20261027-01`. Antes da alteração, o APK instalado e `build/UNSM-S24-FIX-PTBR-EN-v2.apk` foram comparados integralmente: ambos tinham SHA-256 `7333FEF226AC9147FC8B40DE0C49A6824304C2E3EC2B1A69C27E8DE3D71514EA`. Essa é a referência de restauração desta rodada.

O repack substituiu somente a biblioteca nativa, preservando CRC/tamanho dos demais payloads (572 membros). Alinhamento de 16 KiB e assinatura foram verificados, e o certificado do diagnóstico foi comparado ao do APK de uso. A instalação utilizou `adb install --no-incremental -r --user 0`; houve `Success` e conferência do hash do APK instalado contra o diagnóstico assinado. Não houve desinstalação nem limpeza de dados. A pasta temporária autorizada foi removida após instalação e verificação. Manifestos e logs permanecem em `work/controls-flow-diag-20261027/`.

A primeira tentativa de captura foi abortada porque o snapshot não continha o gamepad. A leitura seguinte confirmou novamente o GameSir. A captura válida é `runtime-123006`, com 60 segundos e PID `29252`; o GameSir estava sob device ID 33. O usuário confirmou que testou os comandos e o jogo não respondeu.

| Sinal observado | Resultado |
|---|---|
| `Paddleboat_processInputEvent`, GameSir, fonte `0x501` | 322 chamadas; **todas retornaram 0**. |
| `Paddleboat_processInputEvent`, GameSir, fonte `0x1000010` | 120 chamadas; **todas retornaram 0**. |
| Outros eventos instrumentados | 28 eventos de toque, fonte `0x1002`, device ID 6, separados dos eventos do GameSir. |
| Leitura de controle | **Zero chamadas ao callsite instrumentado de `Paddleboat_getControllerData`**. Não equivale a retorno de erro dessa função: ela não foi observada nesse ponto. |
| Entrada física e falhas | `getevent` registrou 164 transições `EV_KEY` e 658 atualizações `EV_ABS`; zero marcadores fatais no log filtrado da captura. Eventos físicos e chamadas nativas não têm necessariamente correspondência um a um. |

**Conclusão confirmada:** há um bloqueio observável já na etapa da Paddleboat: os eventos identificados do GameSir são entregues à função, mas nenhum foi tratado nessa janela. A antiga hipótese de que o problema necessariamente estaria *depois de dados válidos entregues ao jogo* não é sustentada por essa captura. Não há evidência de botões válidos chegando ao consumidor.

### Hipótese seguinte: conexão e ciclo de vida

O log completo do processo contém `GameControllerManager: setNativeReady`, mas não contém mensagens `GameControllerThread`, `registerInputDeviceListener`, `onInputDeviceAdded` ou `onInputDeviceRemoved`. Esse resultado negativo está limitado ao log retido daquela sessão; não prova sozinho que o listener nunca foi registrado.

Na implementação Java decompilada disponível, `GameControllerManager.onStart()` inicia ou reativa `GameControllerThread`; a thread registra um `InputDeviceListener` e emite log incondicional. O construtor faz um scan inicial, e `setNativeReady()` entrega os dispositivos que estavam pendentes. No nativo, `mmControllerManager_Android::NotifyStartActivity`, em `0xD04844`, chama `Paddleboat_onStart`; este encaminha para `paddleboat::GameControllerManager::onStart`, em `0x118A688`, que chama o método Java quando a instância existe.

A hipótese de trabalho passa a ser **registro de conexão/slot ou entrega de ciclo de vida incompletos**, especialmente quando o controle é reconectado após o scan inicial. Deve ser confirmada medindo os callbacks de conexão e a entrega de `onStart`, inclusive com o GameSir presente desde antes de abrir o jogo. `setNativeReady` não é uma medição do código de retorno de `Paddleboat_init`, e a ausência de leitura também pode depender das máscaras de atualização. Não há patch de jogabilidade aprovado por esta evidência.

### Restauração concluída

Após a captura, o APK de uso foi reinstalado com `adb install --no-incremental -r --user 0`. O instalador retornou `Success`; o hash do APK no aparelho voltou a `7333FEF226AC9147FC8B40DE0C49A6824304C2E3EC2B1A69C27E8DE3D71514EA`, idêntico ao registrado antes do diagnóstico. A restauração levou 309,7 segundos, incluindo transferência e conferência. Não houve desinstalação nem limpeza de dados; o progresso salvo não foi inspecionado dentro do jogo após a atualização.

Evidência: `work/controls-flow-diag-20261027/restoration.json` e `restore.log`. A pasta temporária de APK foi removida, os APKs de uso não foram sobrescritos e o S24 **não ficou com o diagnóstico instalado**. Esta rodada concluiu a instrumentação e a reprodução da recusa de eventos; o suporte a controle permanece sem correção.
