# Controle: gamepad desabilitado na máscara de inicialização

**Atualização:** a habilitação foi aplicada, validada pelo usuário nos menus, na batalha e na reconexão, e instalada em versão sem logs no S24. Ver [CONTROLLER_S24_VALIDATION_20261027.md](CONTROLLER_S24_VALIDATION_20261027.md). As seções de análise abaixo registram a etapa anterior ao teste.

## Resultado

**Confirmado estaticamente no APK de uso:** a inicialização seleciona teclado e toque, deixando o bit de gamepad desligado. A máscara do jogo é `0x22`; sua conversão para os dispositivos Android produz `0x14`. A criação do gerenciador de controle depende do bit 0, ausente nesses dois valores.

Essa configuração explica um mecanismo compatível com a captura anterior: a infraestrutura de entrada é recriada sem gamepad, e a finalização do gerenciador anterior, quando existente, destrói a instância Paddleboat. A captura já havia demonstrado 442 eventos do GameSir com retorno zero e nenhuma leitura no callsite instrumentado de dados. **A cadeia foi verificada no binário; ainda não foi aplicado nem testado no S24 um candidato que habilite o bit.** Outros bloqueios, especialmente ciclo de vida e reconexão, podem aparecer depois.

## Método REA e identidade

A skill `reverse-engineer-anything` foi aplicada para separar identidade do artefato, chamadas, estado e evidência de execução. A chamada MCP `inspect_android_package` retornou `capability_unavailable`: o provedor Android não tem `REA_JADX_MCP_JAR` configurado. Não houve instalação de ferramentas nem alteração da configuração. Esse retorno não produziu uma análise bem-sucedida do APK pelo MCP; não atribuir as conclusões abaixo ao provedor indisponível.

O trabalho continuou com JADX local sobre `classes.dex` extraído diretamente de `build/UNSM-S24-FIX-PTBR-EN-v2.apk`, Ghidra 12.2 headless em **projeto novo**, LLVM e leitura estruturada dos bytes. O DEX tem SHA-256 `111CD285F406CD3ECA540A24AE914312F8DDCDFA1CB19A9D1F3CA49C917A2B63`; a biblioteca do APK tem SHA-256 `8797E4446449B505BD20D704C4123F4BDBEDEEC8B9E1E71A87414A876572CFD0`.

O projeto Ghidra novo usa a biblioteca canônica `C631E712...`, em `work/external-single-1.2.10/libultimateninjastorm.so`. Os intervalos relevantes abaixo, incluindo o wrapper `nummInputInitEx`, e a constante da máscara foram comparados byte a byte com a biblioteca do APK de uso: todos são idênticos. A biblioteca antiga em `work/native/` difere da canônica em 675 bytes; ela não foi usada como autoridade para esta nova análise.

Limite do Ghidra: a análise global atingiu o orçamento de 120 segundos e ficou incompleta. As sete funções selecionadas foram decompiladas depois disso; os pontos essenciais da conclusão foram conferidos também em disassembly e bytes, sem presumir cobertura global de referências. Os VAs abaixo são ELF; o projeto Ghidra soma `0x100000` a esses endereços.

## Cadeia verificada

| Ponto | Evidência |
|---|---|
| `androidMain`, `0xCEEF5C` | Constrói `nuccInitParam`. Em `0xCEEFC0`, carrega o par de constantes em `0x66D2E8`: `22 00 00 00 00 00 F0 00`. Em `0xCEEFD4`, grava esse par a partir de `param +0x14`. O primeiro inteiro é a máscara `0x22`; o segundo, `0x00F00000`, pertence a outro campo e deve ser preservado. |
| `libnucc_Init`, `0xC44380` | Preserva o ponteiro dos parâmetros em `x19` e o repassa a `nuccSys::Initialize` em `0xC443F4`; o prefixo examinado não altera a máscara. |
| `nuccSys::Initialize` | Em `0xCDC5B4`, lê `param +0x14` em `w2`; chama `InputInitialize` em `0xCDC5BC`. |
| `nuccSys::InputInitialize`, `0xCDB4A4` | Grava a máscara em `this +0xADC` e chama `nummInputInitEx` em `0xCDB4C4`. O wrapper chama `nummInputManager::Initialize`. |
| `nummInputManager::Initialize`, `0xCDB35C` | Destrói e desaloca o `mmInputManager` anterior, quando existe. Converte a máscara e cria outro gerenciador/dispositivos. Para `p=0x22`, a expressão decompilada `(p>>1)&2 \| p&1 \| (((p>>1)&1)<<2) \| ((p>>1)&0x18)` resulta em `0x14`. Armazena também a máscara original para atualizações posteriores. |
| `mmInput_Android::CreateDevices`, `0xCEFBA4` | O teste `tbz w1,#0` em `0xCEFBB4` pula a criação de `mmControllerManager_Android` quando o bit de gamepad está desligado. Com `0x14`, cria teclado (bit 2) e toque (bit 4), sem controle. |
| Destruição anterior | `mmInputManager::~mmInputManager`, `0xD0FF14`, chama `mmInput::Finalize`, `0xD0FF70`. Esta destrói o gerenciador de controle quando existe. O destrutor em `0xBB92B0` chama `Finalize`, `0xBB92D4`, que remove o callback e chama `Paddleboat_destroy` em `0xBB9348`. |
| Consequência para eventos | `NotifyInputEvent` não usa o seu ponteiro de gerenciador para encaminhar o evento: chama a API global Paddleboat. Em `processInputEvent`, a ausência da instância global leva ao retorno zero. Isso permite haver log de entrada sem um gerenciador de controle ativo. A ausência efetiva da instância naquela captura ainda não foi medida diretamente. |

Comparação da mudança candidata:

| Configuração | Máscara do jogo | Máscara Android | Dispositivos criados |
|---|---|---|---|
| Atual | `0x22` | `0x14` | Teclado e toque |
| Candidata, ainda não aplicada | `0x23` | `0x15` | Controle, teclado e toque |

## Próximo teste mínimo

Recomenda-se habilitar **somente o bit 0 da máscara local de inicialização**, mantendo os demais campos. O ponto de gravação em `androidMain` está em VA `0xCEEFD4`, offset de arquivo `0xCEAFD4`, bytes originais `00 41 01 FC` (`stur d0,[x8,#0x14]`). A mudança deve reproduzir essa gravação e acrescentar o bit no inteiro correspondente, preservando registradores, pilha e o campo adjacente. Não alterar cegamente a constante compartilhada em `.rodata`: seu uso exclusivo ainda não foi provado.

1. Gerar um candidato separado, guardado pelo hash da biblioteca S24, Build ID e bytes esperados, preservando os patches existentes e os conteúdos pt-BR/inglês.
2. Testar com o GameSir conectado **antes** de abrir o jogo e capturar `CTRLFLOW`: procurar eventos de controle com retorno 1 e leituras `data ret=0` com máscara de botões variando.
3. Verificar menus, batalha, analógicos e manutenção do toque; depois testar desconexão/reconexão e retorno do app ao primeiro plano. Se o listener continuar ausente, instrumentar a entrega de `onStart` separadamente.

A decompilação nova do DEX confirma que `GameControllerManager.onStart()` inicia/reativa a thread de dispositivos; isso não prova que o método tenha sido chamado na captura anterior. A máscara desativada tem evidência estática direta e passa a ser o primeiro bloqueio a testar, antes de alterar o ciclo de vida.

## Evidências e estado final

Evidências privadas em `work/controls-rea-20261027/`: `mask-proof.json`, `artifact-identity.json`, `rea-provider-error.json`, disassembly focado, `GameControllerManager.java`, `focused-decomp.txt` e projeto/log Ghidra. Nenhum APK foi gerado, instalado ou modificado nesta rodada. O APK de uso restaurado na rodada anterior continua sendo a referência; seu estado no aparelho não foi novamente consultado nesta análise estática.

## Candidato instrumentado implementado após autorização

O usuário pediu para prosseguir. `scripts/patch-controls-flow-diag.py --enable-gamepad` agora acrescenta um hook local à gravação em `androidMain`, mantendo os dois hooks `CTRLFLOW`. Sem essa opção, o diagnóstico anterior continua sendo gerado com os mesmos bytes.

O novo stub começa em `0x9B1420`: reproduz `stur d0,[x8,#0x14]`, salva `x9` com alinhamento de pilha de 16 bytes, aplica OR com 1 somente ao inteiro de máscara, restaura `x9`/SP e retorna por `B` a `0xCEEFD8`. Não altera LR, flags, a constante em `.rodata` nem o campo adjacente de `0x00F00000`. O payload total tem 240 bytes, dentro dos 272 disponíveis após os stubs widescreen.

**Quatro testes de host passaram**, incluindo reversão byte a byte, preservação da constante compartilhada, guarda da instrução original, uso de branch sem link e recusa de saída existente/entrada divergente. O disassembly do stub foi revisado. Isso ainda não é aceite de controle no aparelho.

Biblioteca candidata: `work/controls-mask-test-20261027/libultimateninjastorm.so`, SHA-256 `9C8CB2E0C65A3F3BCD0E5A80669009E6021C610ABCCC59A565840416C5A51858`. Antes do empacotamento, o hash do APK instalado foi novamente conferido contra a base de restauração: ambos `7333FEF226AC9147FC8B40DE0C49A6824304C2E3EC2B1A69C27E8DE3D71514EA`. O temporário reutiliza somente o caminho de limpeza já autorizado, `work/build-tmp-controls-flow-20261027-01`; os resultados desta rodada ficam separados dos logs anteriores.
