# AGENTS.md

Instruções para agentes de código e colaboradores que trabalham neste repositório.

Escrito para: agentes de IA e desenvolvedores que vão alterar scripts, patches ou documentação.

## Projeto em uma frase

Patches de APK para Naruto: Ultimate Ninja Storm 1.2.10 no Android (Galaxy S24, SM-S921B): correção Exynos, widescreen, português (Brasil) e, ainda sem patch, controle externo.

Leia antes de mexer: [README.md](README.md), [docs/PRD.md](docs/PRD.md) e [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Regras que não são negociáveis

- **Nunca** commite, publique ou cole em respostas: `work/signing/` (chave e senha), APKs do jogo, `origin/`, `build/` ou qualquer conteúdo de `work/`.
- A entrada do build é o APK 1.2.10 original passado em `--apk`, de qualquer pasta. O script nunca o altera. `origin/` é opcional, só para o desenvolvedor guardar sua cópia.
- `build/Naruto Ultimate Ninja Storm.apk` é o APK final. Cada build do `build-selective.py` **substitui** esse arquivo e o `.build.json` ao lado. Não rode a build sobre `build/` sem confirmação do usuário, porque o APK anterior não é guardado.
- Testes de APK são **sempre limpos**: o `build-selective.py` usa uma pasta temporária `work/build-tmp-*`, apagada ao fim de toda execução, inclusive em falha. Não deixe APK intermediário fora dela. Para limpar restos de execuções interrompidas: `python scripts/build-selective.py --clean`.
- Não crie APK de teste em pasta própria sem apagá-lo logo após a verificação. Se a verificação for só de hash, prefira não gerar o APK inteiro.
- `original/` é somente leitura para evidência.
- Não rode `adb uninstall` nem limpe dados do pacote. Instalação segura: `adb install --no-incremental -r --user 0 <apk>`.
- Não faça commit, push nem branch sem pedido explícito do usuário.
- Não apague nada de `work/` sem confirmar o caminho exato com o usuário.

## Comandos principais

Build seletivo (recomendado): gera um único APK final em `build/`, substituindo o anterior.

```powershell
python scripts/build-selective.py --apk CAMINHO/Ultimate-Ninja-Storm-1.2.10.apk --keystore K --ks-pass F [--widescreen] [--ptbr]
python scripts/build-selective.py --apk CAMINHO/...apk --unsigned                  # sem assinatura, não instalável
python scripts/build-selective.py --clean                                          # remove restos de execuções interrompidas
```

- `--output` muda o destino (padrão: `build/Naruto Ultimate Ninja Storm.apk`).
- Sem `--keystore` e sem `--unsigned` o script recusa.

- A correção Exynos entra sempre.
- `--controls` aplica o patch Paddleboat validado no S24 somente com `--controller-base-apk`, cuja biblioteca exigida é identificada por SHA-256. Não tente aplicar sobre o APK original usando a saída diferente do patch widescreen seletivo.
- `--console-ui` é experimental, exige `--controller-base-apk --controls`, oculta o HUD tátil de batalha e substitui os dois glyphs do atlas Android de seleção (triângulo/círculo) por Y/B. A troca de glyphs é estática no APK e ainda não muda dinamicamente com conexão/desconexão; não instalar nem declarar aceito sem evidência no S24.

Ferramentas usadas pelo build (chamadas pelo orquestrador; rode direto só para depurar):

| Script | Função |
|---|---|
| `scripts/patch-exynos-depth.ps1` | Troca 1 byte (`0x81`→`0x82`) no offset do Build ID conhecido. |
| `scripts/patch-widescreen.py` | Patch nativo de widescreen com guardas de hash e Build ID. |
| `scripts/build-ptbr-assets.py` | Gera os XFBIN/CPK com os catálogos de `patches/ptbr/catalogs/`. |
| `scripts/repack-native-apk.py` | Substitui só a biblioteca nativa e as substituições pt-BR; confere CRC. |

Testes: os scripts `scripts/test-*.py` validam widescreen e cobertura. Rode os que cobrem a área que você alterou.

## Ambiente

- Windows, PowerShell e Git Bash. Python 3.13.
- Android SDK em `%USERPROFILE%\AppData\Local\Android\Sdk`: Build-Tools 36.0.0 (`zipalign`, `apksigner`) e NDK 27.2 (`llvm-bin`, usado pelo widescreen).
- Ghidra 12.2 headless: `%USERPROFILE%\AppData\Local\Programs\AndroidTools\ghidra_12.2_PUBLIC\support\analyzeHeadless.bat`. Para xrefs, use `work/tools/RatioXrefs.java` em um projeto **novo** dentro de `work/` (não altere `work/native/ghidra-5dac-project`).
- Ferramenta REA (`mcp__rea__*`): não funciona com ELF arm64 neste Windows. Use Ghidra.
- ADB sem fio para o S24: pareamento pela tela de Depuração sem fio. O cabo USB fica livre para o controle OTG.

## Convenções

- Antes de novas análises de controles, consulte `analysis/controls/catalog.json` e `analysis/controls/findings.md`; atualize-os com evidência e confiança ao confirmar achados.
- Por padrão, não crie relatórios Markdown datados: atualize o catálogo e o estado atual. Crie relatório separado somente quando solicitado ou necessário para uma evidência que não caiba nesses registros.
- Inventário sem alterações: `python scripts/inventory-artifacts.py --dry-run`. As categorias são conservadoras e não autorizam exclusão.
- Documentação em português (Brasil). Código e nomes de símbolos em inglês, como já está no projeto.
- Scripts novos: Python para orquestração e patches; PowerShell só onde o fluxo já existe (Exynos).
- Todo patch valida: hash da entrada, Build ID, bytes esperados e releitura da saída. Mantenha esse padrão.
- Mudança pequena e verificável. Não faça refatoração ampla sem pedido.
- Ao registrar um resultado, separe o que foi **validado no aparelho** do que foi só verificado por hash ou leitura.

## Armadilhas conhecidas

- Os caminhos do Windows com espaços exigem aspas em todo comando de shell.
- `build-ptbr-assets.py` e os patches de widescreen recusam pasta de saída existente. Isso é intencional.
- O patch Exynos só funciona para os Build IDs listados no script. Outro Build ID aborta.
- Os arquivos `scripts/patch-charsel-bg-s24.py` e `scripts/patch-touchstart-s24.py` ainda não estão commitados.
