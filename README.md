# Naruto Storm Android

Modificações e documentação para Naruto: Ultimate Ninja Storm no Android. A única base ativa é o APK único 1.2.10 (`versionCode 38`); a entrada original fica em `origin/Ultimate-Ninja-Storm-1.2.10.apk`.

## Estado atual

- Correção de composição widescreen instalada no Galaxy S24 (SM-S921B) por atualização ADB, sem desinstalar nem limpar dados.
- O usuário confirmou após abrir o jogo: a margem lateral e o desalinhamento dos toques foram corrigidos.
- APK ativo: `build/Naruto Ultimate Ninja Storm.apk` (versão 1.2.10, código 38).
- SHA-256: `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86`.
- Detalhes do patch e validação: [relatório da correção e aceite no S24](docs/WIDESCREEN_COMPOSITION_VALIDATION_20261026.md).
- A aceitação registrada é para o S24 em 2340×1080; outras proporções e o jogo completo não foram homologados.

## Comece por aqui

1. [Guia de pt-BR e widescreen](docs/PTBR_WIDESCREEN.md) — fontes, construção, instalação e evidências.
2. [Base principal 1.2.10 e patch Exynos](docs/APK_UNICO_1_2_10.md) — origem, patch nativo e limites.
3. [Patch Exynos 1.2.9/1.2.10](docs/EXYNOS_FIX.md) — histórico técnico e diferenças entre distribuições.
4. [Progresso e histórico](docs/PROGRESS.md) — sequência de investigações e validações.

## Mapa do projeto

| Caminho | Conteúdo |
|---|---|
| `patches/exynos/` | Probe nativo e diagnóstico Vulkan. |
| `patches/ptbr/catalogs/` | Catálogos de tradução com IDs e textos de origem. |
| `patches/widescreen/` | Stubs usados na análise do patch de tela larga. |
| `scripts/` | Extração, inventário, patch, repack e preparação de texturas. |
| `docs/` | Guias de uso, evidências, limites e histórico. |
| `audit/` | Frames de referência para análise visual widescreen; preservar. |
| `origin/` | APK único original 1.2.10 usado como entrada. |
| `build/` | Somente o APK integrado aceito para uso no S24. |
| `work/` | Insumos temporários de extração, patch e assinatura; APKs de teste e conjuntos antigos de auditoria foram removidos. |

## Fluxo de trabalho

- Leia o guia da tarefa antes de executar scripts. Os scripts validam hashes, Build IDs, offsets e arquivos de entrada; use sempre uma nova saída.
- Para pt-BR e widescreen, siga as etapas e comandos de [PTBR_WIDESCREEN.md](docs/PTBR_WIDESCREEN.md).
- Para o patch Exynos, siga [APK_UNICO_1_2_10.md](docs/APK_UNICO_1_2_10.md) e use a entrada original fora do repositório.
- Preserve a entrada canônica 1.2.10. Gere candidatos fora de `build/`; copie para lá somente o APK final escolhido.
- A chave de assinatura e a senha ficam em `work/signing/`; nunca as adicione ao Git nem publique.

## Git e artefatos

O diretório ainda não está inicializado como repositório Git. `.gitignore` exclui APKs, dados de trabalho e bytecode Python para evitar que artefatos grandes ou privados sejam adicionados acidentalmente. Os únicos APKs mantidos são a entrada em `origin/` e a saída aceita em `build/`. APKs de teste e candidatos antigos foram removidos de `work/`.
