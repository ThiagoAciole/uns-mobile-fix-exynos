# Base principal — APK único 1.2.10 com patch Exynos

Registro de 24/10/2026. Esta entrada é diferente do conjunto oficial de cinco APKs 1.2.10 analisado anteriormente. O diagnóstico compartilhado está em [EXYNOS_FIX.md](EXYNOS_FIX.md).

**Designada pelo usuário como versão principal em 24/10/2026.** Os próximos ajustes de Exynos, widescreen e pt-BR devem partir deste APK único. A 1.2.9 e os cinco splits antigos são referências históricas; seus resultados de teste não devem ser atribuídos automaticamente a esta base.

## Entrada e saída

| Artefato | Caminho |
|---|---|
| APK original único, preservado | `origin/Ultimate-Ninja-Storm-1.2.10.apk` |
| APK final Exynos + widescreen + pt-BR | `build/Naruto Ultimate Ninja Storm.apk` |
| SHA-256 do APK final aceito no S24 | `5DAC1302663CBEC6ABC678B7F9C84976C2A2A1FEA487F183FEBD2D42D2147D86` |

Pacote `com.bandainamcoent.ultimateninjastorm`, versão 1.2.10, versionCode 38, minSdk 28 e targetSdk 36. A entrada tem certificado APKVISION.ORG, SHA-256 `a54b28d5675941c1d39d6937b4f8e4c69966dede417aca2785bd8dc840c8d1d8`, e código adicional em `classes2.dex`.

## Verificação antes do patch

A biblioteca tem o mesmo Build ID do conjunto 1.2.10 anterior, `c3e506f9be350dfb4a00c79228754028`, mas outro SHA-256. A comparação encontrou 675 bytes diferentes em 231 intervalos na biblioteca recebida. Portanto, o Build ID isolado não foi tratado como prova de identidade integral.

LLVM confirmou que os pontos necessários ao patch permanecem iguais:

| Ponto | Endereço ELF |
|---|---|
| GetImageDataFormat e base da tabela | Função `0x910890`, tabela `0x6bf928` |
| Formato 15 passado ao depth buffer | `0xd1223c` |
| Cálculo do tiling por `bic` | `0x11c1a58` |
| Entrada uint32 alterada, índice 15 | Offset de arquivo `0x6bf964` |

## Alteração realizada

Aplicado [patch-exynos-depth.ps1](../scripts/patch-exynos-depth.ps1) em uma cópia da biblioteca:

```text
mmDataFormat=15: VkFormat 129 → 130
81 00 00 00 → 82 00 00 00
```

Somente um byte difere da biblioteca recebida: `0x6bf964`, de `0x81` para `0x82`. As alterações nativas pré-existentes foram preservadas. Aplicar e reverter o patch em outra cópia produziu SHA-256 idêntico à entrada.

| Estado | SHA-256 da biblioteca |
|---|---|
| Recebida neste APK único | `C631E7127E73ECDE32DA7C8B8054AC6810A375875CD00749D3F4DF5DB29DB79E` |
| Patchada | `CCEA158F39368ED13254A2F29E608E1FD7E5DCB4A1427ED4461B6A05F3C194CA` |

O [repacker](../scripts/repack-native-apk.py) substituiu somente a biblioteca e os metadados de assinatura/alinhamento necessários. Os outros 571 payloads preservaram CRC32 e tamanho; manifest e os dois DEX também foram conferidos por SHA-256. Não foram acrescentadas alterações de Java ou autenticação.

## Validação do artefato

- Assinatura v3 verificada com o certificado local comum aos candidatos anteriores.
- Alinhamento de 16 KiB verificado antes e depois da assinatura.
- Hash da biblioteca extraída do APK final igual ao manifesto do patch.
- Pacote, versão e SDKs conferidos no APK final.
- SHA-256 do APK Exynos-only intermediário (substituído): `1863fe2760b6595ddca2047d996f5a6f17bc33477ff4401b5efac55eaa696679`. O hash do APK final integrado está na tabela acima.

O APK final mantém a versão 1.2.10 / código 38, com patch Exynos, widescreen e catálogos/letreiros pt-BR. O hash e a aceitação visual da versão integrada estão registrados em [WIDESCREEN_COMPOSITION_VALIDATION_20261026.md](WIDESCREEN_COMPOSITION_VALIDATION_20261026.md); os artefatos temporários removidos não são necessários para instalar o APK final.

## Instalação e limites

Este APK único foi instalado por atualização sobre a 1.2.9 em 24/10/2026, após solicitação explícita do usuário. O ADB retornou `Success`; versionName 1.2.10 e versionCode 38 foram confirmados no perfil pessoal. Não houve desinstalação, e os diretórios CE/DE mantiveram os mesmos inodes. Abertura e gameplay deste arquivo ainda não foram validados. Os testes anteriores de abertura da 1.2.10 pertencem ao candidato baseado nos cinco splits.

Se o aparelho ainda usa a 1.2.9 gerada nesta sessão, os dois candidatos têm o mesmo certificado local e a 1.2.10 tem versionCode superior. A atualização pode ser solicitada por ADB, preservando os dados do pacote em vez de desinstalá-lo:

```powershell
adb install --no-incremental -r --user 0 'C:\Users\Thiago Aciole\Projetos\Jogos\Naruto Ultimate Ninja Storm\build\Naruto Ultimate Ninja Storm.apk'
```

Esse comando foi executado com sucesso. O resultado foi salvo em `work/external-single-1.2.10/update-result.txt` e no relatório associado ao APK. Uma instalação assinada com outra chave exige tratamento diferente; não presuma compatibilidade com a assinatura do editor ou com o APK recebido.

Este guia registra a base do patch Exynos; o único artefato ativo é a versão integrada indicada na tabela, com widescreen e pt-BR. A autenticação e o comportamento do código de terceiros recebido não foram alterados.
