# Interface de console com gamepad — análise estática (27/10/2026)

## Estado e escopo

O GameSir-X5 Lite já funciona no Galaxy S24 com a biblioteca de controle instalada. Esta etapa examinou o fluxo de UI para mostrar indicações de botões de gamepad e ocultar os controles táteis quando houver controle ativo. A solicitação anterior de manter a investigação estática foi preservada: não houve interação com o aparelho, alteração do APK instalado ou validação visual em execução.

O APK de referência usado pelo REA foi `build/UNSM-S24-FIX-PTBR-EN-v2.apk`, SHA-256 `7333fef226ac9147fc8b40de0c49a6824304c2e3ec2b1a69c27e8de3d71514ea`, pacote `com.bandainamcoent.ultimateninjastorm`, versão `1.2.10`/código `38`. As análises REA/JADX confirmaram o manifesto e localizaram `com.google.android.games.paddleboat.GameControllerManager`; elas são evidência estática do APK e não provam execução.

## Fluxos confirmados

- A entrada de opções do Android mostra configurações de **controles táteis**: ativação, sensibilidade e botões. Não é um editor de mapeamento físico do GameSir.
- `ccKeyConfig` tem um fluxo de configuração de teclado/controle com desenho, navegação e salvamento. Os slots da classe base `ccKeyConfig` para inicialização/controle são stubs de quatro bytes, mas a classe especializada `ccKeyConfigDuel` implementa `InitButtonSet`, `InitContentSet`, `InitKeyConfig` e `CtrlKeyConfig`; a vtable confirma esses overrides. Portanto, a lógica de configuração Duel não está ausente.
- A página Android `ccOptionControlPad` é a configuração de controles táteis: `Setup()` chama apenas `ccDispPad::Setup()`. Nesta análise não apareceu uma chamada de menu que instancie `ccKeyConfigDuel`, então falta estabelecer como expor a UI especializada ao jogador; não basta restaurar os stubs da base.
- O levantamento de xrefs de Ghidra para o construtor `ccKeyConfigDuel` não encontrou referências de chamada de código: os resultados são referências de dados/entrada externa, enquanto a vtable registra os métodos virtuais especializados. Isso reduz a chance de existir uma rota Android direta, mas não exclui despacho por fábrica/registro indireto; portanto, ainda não é seguro ligar a classe a um item de menu por patch.
- `ccButtonSet::SetTouchEnable` percorre os botões e chama `ccTouchButton::SetTouchEnable`. A evidência de código mostra que esse caminho habilita/desabilita a interação; não é suficiente para concluir que o desenho some.
- A camada visual usa rotas próprias, incluindo `ccDispTouchButton::Draw`, `ccTouchStick::Draw`, `ccDuelAttackButton::Draw`, `ccDuelTouchStick::Draw`, `ccChangeCommonTouchButton::Draw` e `ccChangeAnimationTouchButton::Draw`. Para ocultar o HUD tátil, o patch precisa alcançar o conjunto correto de desenhos sem suprimir a UI normal dos menus.
- `ccDuelPad::Setup` monta o HUD de batalha em grupos: botões comuns, quatro botões animados, analógico esquerdo e lista de itens. `ccDuelPad::SetPadEnable` só atualiza a visibilidade desses elementos quando `GetPadCtrlLv()` retorna zero; a implementação de `ccDuelPad::GetPadCtrlLv()` retorna constante `1`. Portanto, essa API existente não é um caminho automático de ocultação baseado na conexão do GameSir.
- Existem setters visuais (`ccTouchStick::SetVisible`, `ccCommonTouchButton::SetVisible`, `ccChangeCommonTouchButton::SetVisible` e `ccDuelAttackButton::SetVisible`). Eles confirmam mecanismos de visibilidade, mas a inspeção não estabeleceu um único dono global que receba automaticamente o estado de conexão do controle.
- Os atlas `xmode00` e `xmode00_1` de `xmode.xfbin` Android foram extraídos e inspecionados: ambos contêm símbolos PlayStation de triângulo e círculo; não há A/B/X/Y nesses dois recursos. Isso não exclui glyphs em outros atlas. `ccSelectCharacter::CtrlCaptionControls` cria clumps de interface e fontes para legendas; seu caminho de desenho existe. A presença dos dois símbolos não prova cobertura de prompts por tela.
- O atlas `cmn_button00` contém glyphs ABXY coloridos e gatilhos. A análise dos mapas de chunks e dos `nuccChunkSprite` em `cmn.xfbin` confirmou referências diretas dos sprites `xcmn_triangle`, `xcmn_batsu`, `xcmn_square`, `xcmn_circle` e variantes `xcmn_ani_*` para `nuccChunkTexture cmn_button00`; os sprites `xcmn_ana_*` referenciam `cmn_button01`. A tabela nativa `DISP_ELEMENT_ID` associa os quatro sprites aos IDs `0x0f`, `0x10`, `0x11` e `0x12`, nessa ordem. `ccKeyConfigDuel::InitButtonSet` chama `ccKeyConfig::CreateSpriteButton` com esses quatro IDs, além de um ícone adicional `0x1e9`. Portanto, a tela Duel de configuração já instancia os quatro sprites de face existentes; ainda falta comprovar os UVs exatos, expor essa tela pelo menu Android e fazer prompts contextuais refletirem bindings alterados.
- A tabela `DISP_ELEMENT_ID` registra elementos de `data/interface/battle/pad/xbattle_pad.xfbin` nos IDs `0x31c–0x320`, `0x3e3–0x3f5`, `0x3f8–0x3fb`, `0x3fd` e `0x402–0x40f`; `ccDuelPad::Setup` inicializa os controles táteis com esses dados e também cria `xcmn_pad_tag` (`0x3fc`). Extraí apenas esse XFBIN do CPK do APK de referência e inspecionei as texturas: `xbattle_pad01` contém gestos/ícones táteis, `xbattle_pad02` mostra o stick virtual e `xbattle_pad07` um gesto de toque. Essa família é do HUD tátil, não é a arte ABXY para prompts de controle.
- O XFBIN extraído tem SHA-256 `ca7767141ad6cce3404e1dc70aefea98ff699e34f7e04eb33700f423356082c3`; o inventário validou o caminho no banco `assets/data/disc/dataRegion.awb`. A extração foi limitada a `data/interface/battle/pad/xbattle_pad.xfbin`; APK, banco e demais membros não foram alterados.
- `cmn_button00` já tem sprites de face nomeados, IDs de exibição e uso no editor `ccKeyConfigDuel`; não é necessário inventar um atlas novo para a tela de configuração. Os dados compactados de `nuccChunkSprite` ainda precisam ser decodificados para provar UVs/dimensões; fora do editor, os callsites de prompts precisam ser ligados ao estado ativo do Paddleboat e ao mapa efetivo de bindings.
- Paddleboat exporta `Paddleboat_getControllerStatus`; a documentação oficial define `ACTIVE=1` e `INACTIVE=0`. `nummInputGetControllerType` consulta o tipo do `nummInputManager`, mas os xrefs do Ghidra não localizaram chamadas diretas a esse helper. Não há evidência de que a UI atual faça a troca de ícones em resposta à conexão.
- `nuccSys::GetControllerButtonName` converte as máscaras em glyphs PlayStation (`×`, `△`, `□`, `○`). Os xrefs no ELF mostram a exportação/wrapper PLT, mas nenhum consumidor interno de UI. Alterar esse helper pode trocar rótulos em consumidores externos; não está provado que altere os prompts renderizados nas telas.
- O catálogo Android inclui 25 mensagens `NS1_DirectInput_00..24_STEAM`: título, seleção de jogador 1/2, sucesso/falha e instruções de atribuição para BACK, START, oito glyphs (`iconF0/F1/F3/F2`, `icon02/01/03/00`), analógico esquerdo, `icon10/11` e analógico direito. Isso confirma que existem textos do fluxo DirectInput no catálogo empacotado, mas o sufixo `_STEAM` e a presença das mensagens não provam que a tela esteja roteada ou funcional no Android. Os nomes `iconXX` não foram semanticamente associados aos botões ABXY nesta análise.

## Decisão técnica para a próxima implementação

1. Preservar o controle funcional e usar o estado ativo do Paddleboat como condição de apresentação, com restauração imediata do HUD tátil quando o controle desconectar.
2. Separar o desenho do HUD tátil da navegação/realce de seleção dos menus. Não aplicar um `Draw` global que também remova botões e destaques da interface.
3. Manter `xbattle_pad.xfbin` no caminho dos controles táteis. Para prompts de gamepad, reutilizar os sprites `xcmn_*` já ligados a `cmn_button00`, confirmar seus UVs e callsites, e depois ligar cada glyph ao mapa normalizado de Paddleboat. O atlas ABXY já disponível é preferível a criar glyphs novos.
4. Expor o editor de mapeamento Duel existente depois de localizar a fábrica/rota de tela Android que cria `ccKeyConfigDuel`; sua inicialização já usa os IDs de sprite `0x0f–0x12` para as quatro faces. Não reimplementar de início as operações especializadas que já estão presentes.

## Limites ainda abertos

- Como o usuário poderá personalizar o mapa no Android. O binário contém defaults e editor Duel, mas a rota Android do editor não foi localizada.
- Se o fluxo `NS1_DirectInput_*_STEAM` é apenas conteúdo compartilhado no banco de mensagens ou se há uma rota Android omitida; não ligar uma entrada de menu a `ccKeyConfigDuel` até localizar o contrato de navegação, inicialização e retorno da tela.
- Quais UVs dos sprites `xcmn_*` selecionam cada glyph de `cmn_button00`; a rota Android para `ccKeyConfigDuel`; e como prompts de cada tela refletem Paddleboat e bindings personalizados.
- Se algum consumidor de tela usa `nuccSys::GetControllerButtonName`; os xrefs atuais mostram apenas o wrapper/exportação, não uma chamada interna de UI.
- Quais atlas e rotas desenham cada prompt de ação em menus, seleção e tutoriais.
- Preferência escolhida pelo usuário: ABXY do GameSir. O mapeamento abaixo comprova os quatro comandos principais do perfil padrão; bindings alterados no editor e prompts de ações contextuais ainda precisam acompanhar a configuração efetiva.
- A localização central e o ciclo de vida que permitem sincronizar conexão, desconexão, visibilidade e seleção sem atrasos.
- Compilação, instalação e aceite visual no S24. Nenhuma dessas etapas faz parte desta análise estática.

## Associação padrão entre ações e ABXY

A relação do perfil padrão foi reconstruída juntando a tabela de nomes de `ccKeyConfig::InitTextTbl`, os valores inicializados por `ccSaveData::InitKeyConfigDuel` e a tabela de conversão executada por `nummController::Update`. A enumeração oficial do Paddleboat define A/B/X/Y nos bits `0x10/0x20/0x40/0x80`.

| Ação do jogo | Máscara default em `ccSaveData` | Glyph PlayStation nativo | Entrada Paddleboat | GameSir |
|---|---:|---|---:|---|
| `KeyAttack` | `0x2000` | `○` | `0x20` | B |
| `KeyJump` | `0x4000` | `×` | `0x10` | A |
| `KeyChakraLoad` | `0x1000` | `△` | `0x80` | Y |
| `KeyShuriken` | `0x8000` | `□` | `0x40` | X |

Uma verificação cruzada em `nuccSys::GetControllerButtonName` confirma os símbolos: `0x4000` retorna `×`, `0x1000` retorna `△`, `0x8000` retorna `□` e `0x2000` retorna `○`. Pela posição física no GameSir, a conversão adequada é A, Y, X e B, respectivamente. Isso confirma o perfil padrão, mas não prova que os prompts de todas as telas usem esse helper nem que bindings reconfigurados sejam refletidos no HUD. O atlas `xmode` permanece uma substituição estática por posição, sem troca dinâmica pelo controle ativo.

## Implementação concreta — HUD de batalha

Foi criado `scripts/patch-controls-console-ui.py` com o stub `patches/controls-diag/console-ui.S`. Ele recebe apenas a biblioteca de gamepad já validada (SHA-256 `2923db436931bb2f3a0b7178a7b1c007434e28d269e5ec5a81c5be4a73e96db7`) e exige o manifesto anterior, Build ID e prólogo esperados. O patch consulta `Paddleboat_getControllerStatus(0)`: se retornar `ACTIVE` (`1`), `ccDuelPad::Draw` não desenha botões nem sticks táteis e faz tail-call à rotina original da lista de itens; se estiver inativo, restaura argumentos, reproduz a instrução substituída e continua o desenho original. A API retorna o enum de status diretamente; `ACTIVE` significa conectado e ativo, conforme a [documentação oficial Android](https://developer.android.com/reference/games/game-controller/group/paddleboat).

O primeiro candidato nativo (v1, supersedido) teve SHA-256 `e14065f116bd8c50f023e73b8ce155568d95e9eb3ddcdda3f11e7d54ef774ea6`. A inspeção Ghidra mostrou que a lista de itens é desenhada por uma chamada separada no fim de `ccDuelPad::Draw`. A versão atual (v2) mantém essa chamada como tail-call quando o controle está ativo, omitindo o HUD tátil sem remover a seleção visual de itens. O SHA-256 v2 é `557b842e7f3372b1498843fce78df8b32bab43e26030d4092ef6c66ce290cb9e`.

O candidato v2 foi compilado e inspecionado com `llvm-objdump`: quando ativo, restaura os registradores, aponta para `ccPlayerItemListBase` no offset `+0xc38` e faz tail-call à mesma função de desenho usada pelo caminho original. `--check-only`, `py_compile`, hash da releitura e `git diff --check` passaram. Continua um candidato estático/host, **não instalado nem validado no S24**. Não altera foco/realce dos menus nem expõe o editor Duel. A conexão ativa só é consultada durante a batalha. Para reproduzir, passe a biblioteca validada em `--input` e escolha uma saída nova fora de `build/` e `original/`; `--check-only` não grava arquivos. O repacker pode usá-la com o APK base cujo membro nativo corresponde a `sourceSha256` no manifesto.

## Provedor REA

O REA abriu o ELF do candidato e confirmou hash `557b842e...ce290cb9e`, mas `binary_overview` retornou `provider_unavailable`: Ghidra P0 do REA aceita PE, Hopper não suporta este host, e IDA/Kuna não estão configurados. A chamada REA para o APK também retornou `capability_unavailable`, porque o processo MCP ativo reporta `REA_JADX_MCP_JAR` não configurado, embora a configuração local do Codex tenha sido preparada anteriormente. Não repeti chamadas sem alteração de configuração. A análise nativa focada foi feita com Ghidra headless 12.2 em projeto separado sob `work/controls-console-ui-20261027/`; nenhum banco existente foi alterado. Nesta sessão, REA confirmou a identidade do ELF e os limites dos providers; o pseudocódigo veio do Ghidra local.

Na continuação, REA reabriu o ELF local e confirmou novamente o SHA-256 completo. `search_procedures("ccKeyConfigDuel")` permaneceu indisponível: o diagnóstico local mostra Ghidra instalado, mas o provider REA rejeita ELF ARM64 neste host Windows; Hopper não é suportado no host, IDA não está configurado e Kuna não está disponível. O diagnóstico também aponta drift no registro Codex; o dry-run de reparo propõe editar `~/.codex/config.toml` e substituir a cópia compartilhada da skill. Não apliquei esse plano porque restaurar o registro não torna o provider Ghidra compatível com este alvo. A análise do construtor e dos xrefs foi conferida nos resultados do Ghidra headless 12.2 já existentes, sem abrir ou alterar banco de análise. A investigação permaneceu estática e não usou ADB.

## Rota confirmada dos glyphs ABXY no editor Duel

O `DISP_ELEMENT_ID` associa `0x0f–0x12` a `xcmn_triangle`, `xcmn_batsu`, `xcmn_square` e `xcmn_circle`. `ccKeyConfigDuel::InitButtonSet` instancia os quatro IDs por `ccKeyConfig::CreateSpriteButton` (na ordem do código: círculo, cruz, triângulo, quadrado). Ghidra confirmou que `CreateSpriteButton` delega a `ccKeyConfig::CreateSprite`, que chama `ccDispSprite::Create` com o ID recebido e aplica escala. Assim o editor nativo reutiliza sprites que apontam para `cmn_button00`, cujo atlas já contém os rótulos A/B/X/Y. Isso dá base concreta para uma tela de configuração com ícones GameSir sem desenhar novos assets, mas o caminho de abertura da tela no Android segue sem referência de chamada confirmada.

O dump de xrefs dos métodos `ccKeyConfigDuel::InitKeyConfig` e do construtor `ccKeyConfigDuel` mostra somente referências de dados, vtable e indirection; não há caller de código identificado nesse ELF. Como comparação, `ccDispManager::Entry(unsigned short)` tem branches explícitos para as páginas Android de opções (`0xa8` áudio, `0xa9` câmera, `0xaa` controles, `0xab` gráficos, `0xac` idioma) e não instancia `ccKeyConfigDuel`. Isso delimita um ponto de integração plausível — o despacho do `ccDispManager` e a navegação das opções — mas ainda não define uma alteração segura: falta identificar o contrato de criação/retorno do objeto de configuração e o item de menu que o abriria. O dump de referências foi preservado em `work/controls-console-ui-20261027/keyconfig-route-xrefs-static.txt`; a decompilação de `Entry` está em `work/controls-console-ui-20261027/disp-manager-entry-static.txt`.

Como checagem adicional, REA abriu `work/native/libultimateninjastorm.so` (SHA-256 `ad9b07806ed2c0a9ba4fbb2da9d0b680bd5998880a8a166f862d6cb9e38475d2`), porém não disponibiliza provider de análise para ELF ARM64 neste Windows. Ghidra headless 12.2 local confirmou `ccDispSprite::Create(unsigned short)` e um caller direto que é somente wrapper indireto; essa referência não identifica consumidores de UI. As referências de `InitButtonSet` e a tabela de IDs vieram do dump Ghidra existente, não de execução. Os UVs exatos e o menu Android continuam pendentes.

## Skin estática de prompts GameSir — etapa parcial

Foi criado `scripts/patch-controls-prompts.py` e integrado ao caminho `--controller-base-apk --controls --console-ui`. Ele valida o hash da biblioteca da base S24 (`8797e444...`), o hash de `xmode.xfbin` (`887bfc1f...`) e os hashes/dimensões/formatos dos atlas `xmode00` e `xmode00_1`. A transformação limpa apenas as áreas dos dois glyphs existentes, desenha Y na posição superior e B na posição direita, reimporta as texturas e confirma a releitura pixel a pixel. O novo XFBIN substitui só esse membro no AWB; os outros membros passam pelo repacker com CRC/tamanho preservados.

A validação em memória na APK-base gerou XFBIN candidato SHA-256 `be78fd1ecc9a611d6c0f636c89d925e42b6833db906ed560e89bc5a80a1a0cda`. A prévia está em `work/controls-console-ui-20261027/xmode00-gamepad-prompts-preview.png`. É uma correspondência **por posição física** (triângulo acima → Y; círculo à direita → B), não uma prova de que essas ações do jogo sejam mapeadas aos botões Android correspondentes. A skin é estática no APK, cobre somente esses dois prompts e não cria A/X; sem um patch dinâmico, os glyphs GameSir também permanecem quando o controle está desconectado. Não houve repack CPK/APK, instalação nem validação no S24.


## Menus Grobal e OptionSelect — análise estática

Ghidra headless 12.2 com `-noanalysis` no projeto `sprite-xrefs-static-20261027`, imagem base `0x100000`. Saída em `work/controls-console-ui-20261027/menu-decomp-static.txt` (ferramenta: `work/tools/DecompileAddrs.java`).

- `ccDispGrobalMenuList::Init` (`0xd46310`) cria o sprite de fundo (`ccDispSprite::Create(0x25b)`), a barra `xcmn_tutorial_gauge_b`, o botão de fechar (`ccButtonSetSingle`, texto `NS1_Mobile_Close`) e chama `UpdateScrollItem`. Não instancia nenhuma página de opções nem chama `ccDispManager::Entry`.
- `ccDispGrobalMenuList::Ctrl` (`0xd46634`) só processa toque/botão Voltar e fecha a lista. Não há roteamento para configuração de controles.
- `ccDispOptionSelectObj::ApplyIndex` (`0xd56370`) e `SetCurrentIndex` (`0xd56360`) atualizam texto, setas e cor do item selecionado. São widgets de opção, não rota de tela.
- `SetAndCollision` (`0xd47c84`) apenas guarda o ponteiro de colisão.

Conclusão: nenhum dos menus analisados abre o editor `ccKeyConfigDuel`. A rota de integração continua sendo o despacho de `ccDispManager::Entry` (tipo `0xAA`, controles). Ainda falta descobrir quem solicita esse tipo a partir da navegação de opções.

Ferramentas: REA abriu o ELF e confirmou o SHA-256, mas `search_procedures` retornou `provider_unavailable` (ELF ARM64 em win32). Análise feita com Ghidra headless local. Nenhum patch, APK ou ADB foi usado nesta etapa.

## Rota da página de controles e retorno — continuação estática

No projeto Ghidra `sprite-xrefs-static-20261027`, com imagem base `0x100000`, `-noanalysis` e `-readOnly`, a decompilação de `ccOptionControl::StepInit` (`0xd56944`) mostra a chamada direta `ccDispManager::Entry(..., 0xaa)` e guarda o identificador retornado em `this + 0x590`. Portanto, `0xAA` é uma parte da tela de controles táteis gerida por `ccOptionControl`, não a entrada do editor Duel.

Em batalha, `ccPauseMenuDuel::StepKeyConfig` (`0xc3ca9c`) cria `ccOptionControl(1)`, chama `ccOptionBase::Ctrl` e espera o campo `+0x50` sinalizar término; então libera o objeto, inicia fade-in e retorna ao passo 0, subpasso 3. `ccPauseMenuDuel::Ctrl` despacha o passo 4 para esse método. `ccOptionControl::StepMain` (`0xbe13c8`) processa o botão voltar de `ccOptionControlPad` e passa ao passo 4; `ccOptionControl::StepEnd` (`0xd3a504`) libera o identificador guardado, reaplica configurações do HUD quando presente, reserva autosave sob condições e marca `+0x50 = 1`.

Esses achados identificam o ciclo de vida da tela tátil e um ponto de extensão plausível dentro de `ccOptionControl`, preservando a entrada existente. Não provam como criar, controlar, desenhar ou encerrar `ccKeyConfigDuel`, nem sua compatibilidade com o mapa Paddleboat e a persistência. A menor integração segura ainda não está determinada; trocar simplesmente `Entry(0xaa)` eliminaria a página tátil e não foi proposto como patch. A origem exata da seleção que chega ao passo 4 também precisa ser comprovada, pois `StepIndex` usa passos e subpassos.

Evidências: `work/controls-console-ui-20261027/option-control-navigation-static.txt` e `work/controls-console-ui-20261027/pause-control-navigation-static.txt`. Os dois endereços `0xbc3ca9c` e `0xbc591c8` no primeiro dump retornaram `NOFUNC` por erro de endereço; a função de pausa foi obtida no segundo dump com o endereço correto. Nenhum APK foi gerado, nenhum dispositivo foi acessado e não houve validação em execução.
