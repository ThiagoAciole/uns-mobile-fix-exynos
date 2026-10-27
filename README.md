# Naruto Storm Mobile Fix Exynos

Correções e documentação para **Naruto: Ultimate Ninja Storm** no Android: patch Exynos, widescreen, português (Brasil) e, em investigação, controle externo.

A base ativa é o APK único **1.2.10** (`versionCode 38`).

## Galeria

<table>
  <tr>
    <td align="center"><img src="docs/screenshots/01-tela-titulo.jpg" width="260" alt="Tela de título"><br><sub>Tela de título</sub></td>
    <td align="center"><img src="docs/screenshots/02-selecao-modo.jpg" width="260" alt="Seleção de modo"><br><sub>Seleção de modo</sub></td>
    <td align="center"><img src="docs/screenshots/03-menu-opcoes.jpg" width="260" alt="Menu de opções"><br><sub>Menu de opções</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/04-configuracoes-controle.jpg" width="260" alt="Configurações de controle"><br><sub>Configurações de controle</sub></td>
    <td align="center"><img src="docs/screenshots/05-batalha.jpg" width="260" alt="Batalha"><br><sub>Batalha</sub></td>
    <td align="center"><img src="docs/screenshots/06-vila-missao.jpg" width="260" alt="Vila com missão"><br><sub>Vila com missão</sub></td>
  </tr>
</table>

## Estado atual

- Correção de composição widescreen instalada no Galaxy S24 (SM-S921B) por atualização ADB, sem desinstalar nem limpar dados.
- O usuário confirmou após abrir o jogo: a margem lateral e o desalinhamento dos toques foram corrigidos.
- APK ativo: `build/Naruto Ultimate Ninja Storm.apk` (versão 1.2.10, código 38).
- SHA-256: `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`.
- Relatório da correção e aceite no S24: [WIDESCREEN_COMPOSITION_VALIDATION_20261026.md](docs/WIDESCREEN_COMPOSITION_VALIDATION_20261026.md).
- A aceitação registrada é para o S24 em 2340×1080. Outras proporções e o jogo completo não foram homologados.

## Recursos

| Recurso | Situação |
|---|---|
| **Correção Exynos** | Aplicada e verificada por hash. Entra sempre nas builds. |
| **Widescreen** | Validado somente no Galaxy S24 em 2340×1080. Outras proporções não foram testadas. |
| **Português (Brasil)** | Incluído nos textos e letreiros. Dublagem e algumas artes continuam no idioma original. |
| **Controle externo** | ⚠️ **Não funciona ainda.** Investigação em andamento; não use como referência de funcionamento. |

Uma variante mantém português e coloca inglês no lugar de francês. O usuário confirmou o funcionamento do inglês no S24; veja a construção e os limites em [Inglês no espaço do francês](docs/ENGLISH_NO_FRANCES.md).

## Para quem vai usar

Este repositório **não distribui o jogo**. Você precisa do seu próprio APK 1.2.10 (`versionCode 38`), obtido legalmente.

**Requisitos:** Windows com PowerShell, Python 3, Android SDK Build-Tools (`apksigner`, `zipalign`), ADB e um certificado de assinatura local criado por você.

Escolha só os ajustes que quiser com [`scripts/build-selective.py`](scripts/build-selective.py). A correção Exynos entra sempre, porque o widescreen depende dela.

```powershell
# só Exynos
python scripts/build-selective.py --apk "C:\caminho\Ultimate-Ninja-Storm-1.2.10.apk" --keystore K --ks-pass F

# Exynos + pt-BR
python scripts/build-selective.py --apk "C:\caminho\Ultimate-Ninja-Storm-1.2.10.apk" --keystore K --ks-pass F --ptbr

# Exynos + widescreen + pt-BR
python scripts/build-selective.py --apk "C:\caminho\Ultimate-Ninja-Storm-1.2.10.apk" --keystore K --ks-pass F --widescreen --ptbr
```

- O APK final vai para `build/Naruto Ultimate Ninja Storm.apk` e **substitui** o anterior. Use `--output` para outro destino.
- Os arquivos intermediários ficam em `work/build-tmp-*` e são apagados ao fim de cada execução.
- Sem `--keystore`/`--ks-pass`, use `--unsigned` para gerar um APK que não instala.
- `--apk` é obrigatório e pode estar em qualquer pasta. Não é preciso copiar o APK para `origin/`.

**Passos resumidos** (detalhes em [PTBR_WIDESCREEN.md](docs/PTBR_WIDESCREEN.md#construção)):

1. Tenha o seu APK original 1.2.10 em qualquer pasta.
2. Gere a build com o script acima.
3. Assine o APK com seu certificado e confira `apksigner verify` e `zipalign -c -P 16 4`.
4. Instale com `adb install --no-incremental -r --user 0`, sem desinstalar nem limpar dados.

> Não publique a chave de assinatura, a senha, APKs do jogo nem o conteúdo de `work/`.

## Comece por aqui

1. [Guia de pt-BR e widescreen](docs/PTBR_WIDESCREEN.md): fontes, construção, instalação e evidências.
2. [Base principal 1.2.10 e patch Exynos](docs/APK_UNICO_1_2_10.md): origem, patch nativo e limites.
3. [Patch Exynos 1.2.9/1.2.10](docs/EXYNOS_FIX.md): histórico técnico e diferenças entre distribuições.
4. [Progresso e histórico](docs/PROGRESS.md): sequência de investigações e validações.

## Mapa do projeto

| Caminho | Conteúdo |
|---|---|
| `patches/exynos/` | Probe nativo e diagnóstico Vulkan. |
| `patches/ptbr/catalogs/` | Catálogos de tradução com IDs e textos de origem. |
| `patches/widescreen/` | Stubs usados no patch de tela larga. |
| `scripts/` | Extração, inventário, patch, repack e preparação de texturas. |
| `docs/` | Guias de uso, evidências, limites e histórico. |
| `docs/screenshots/` | Capturas de tela da galeria acima. |
| `origin/` | APK original 1.2.10, se você quiser guardar uma cópia aqui. |
| `build/` | APK integrado aceito para uso no S24. |
| `assets/` | Arte versionada usada como referência ou entrada de patch. Índice em [assets/README.md](assets/README.md). |
| `work/` | Insumos temporários de extração, patch e assinatura. Inventários e textos extraídos do jogo ficam em `work/inventory/`. |

## Fluxo de trabalho

- Leia o guia da tarefa antes de executar scripts. Os scripts validam hashes, Build IDs, offsets e arquivos de entrada.
- Para pt-BR e widescreen, siga as etapas de [PTBR_WIDESCREEN.md](docs/PTBR_WIDESCREEN.md).
- Para o patch Exynos, siga [APK_UNICO_1_2_10.md](docs/APK_UNICO_1_2_10.md) e use a entrada original fora do repositório.
- Preserve a entrada canônica 1.2.10. Gere candidatos fora de `build/`.
- A chave de assinatura e a senha ficam em `work/signing/`. Nunca as adicione ao Git nem publique.

## Git e artefatos

O diretório é um repositório Git (branch `main`). O `.gitignore` exclui APKs, dados de trabalho e bytecode Python para evitar que artefatos grandes ou privados sejam adicionados por engano.
