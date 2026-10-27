# Prompts GameSir no Naruto Storm — plano de implementação

**Objetivo:** começar a substituir prompts PlayStation do jogo por rótulos GameSir e conectar a mudança ao perfil experimental de HUD.

**Abordagem:** editar deterministicamente apenas `xmode00` e `xmode00_1` do XFBIN Android de seleção. Como esse atlas contém triângulo e círculo, a primeira etapa usa a correspondência física de posição triângulo → Y (topo) e círculo → B (direita), sem afirmar equivalência semântica das ações. O build continua restrito à base S24 já aceita e ao caminho `--controls --console-ui`.

**Limites da etapa:** não inventa prompts A/X onde o atlas não contém esses sprites, não expõe o editor Duel e ainda não alterna os glyphs dinamicamente ao conectar/desconectar. Não instalar nem declarar aceito no aparelho durante a análise estática.

## Etapas

1. [x] Criar patch de XFBIN com hash de entrada, identidade/dimensões/hash das duas texturas, substituição determinística dos glyphs e releitura.
2. [x] Ligar o XFBIN ao banco CPK da base S24 somente com `--console-ui`, preservando os demais membros pelas rotinas CPK/repack existentes.
3. [x] Rodar verificação estática em memória (`--check-only`) sobre a base exata e atualizar PRD/arquitetura com o escopo implementado e os limites restantes.
4. [ ] Executar a composição CPK/APK em saída temporária e inspecionar o pacote resultante; depois obter aceite visual no S24 antes de chamar a variante de pronta.
