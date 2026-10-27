# Inglês no espaço do francês

O candidato mantém o português no espaço `eng` e usa os assets ingleses originais no espaço `fre`. Os rótulos do seletor, em todos os seis idiomas, passam a identificar esses espaços como **Português (Brasil)** e **English**. O francês deixa de estar disponível nesse candidato.

## Como funciona

O script `scripts/english_in_french.py` exige os hashes conhecidos do APK original e da base local pt-BR. Nos três contêineres que têm caminhos por idioma, ele usa os dados ingleses originais nos 259 caminhos franceses, depois de conferir cada bloco contra o original. Em 110 títulos de missão, adapta também os caminhos internos de recursos para `fre`, após conferir os caminhos correspondentes no arquivo francês original; o conteúdo gráfico continua inglês. No arquivo de mensagens do francês, usa o conteúdo inglês original e altera os dois rótulos do seletor. Os outros cinco catálogos são mantidos e recebem apenas os rótulos atualizados.

O letreiro e o modelo originais ingleses são usados juntos na tela de título: a redução do modelo da versão portuguesa foi feita para um texto mais largo. Os arquivos que não pertencem à troca são preservados; a biblioteca nativa permanece igual à base.

## Gerar e conferir

O destino deve ser um arquivo novo. O script produz um APK **sem assinatura**; assine com o certificado local antes de instalar. Não substitua o APK existente.

```powershell
python scripts/english_in_french.py --original "origin/Ultimate-Ninja-Storm-1.2.10.apk" --base "build/UNSM-S24-FIX.apk" --output "build/UNSM-S24-FIX-PTBR-EN.apk"
python scripts/verify-english-in-french.py --original "origin/Ultimate-Ninja-Storm-1.2.10.apk" --base "build/UNSM-S24-FIX.apk" --candidate "build/UNSM-S24-FIX-PTBR-EN.apk"
```

O verificador compara os 259 pares, o conteúdo exato dos seis arquivos de mensagens e os demais membros do APK por CRC e tamanho. A assinatura e o alinhamento devem ser conferidos separadamente com `apksigner verify` e `zipalign -c -P 16 4`.

## Limites de validação

O usuário confirmou que o inglês funciona no aparelho. A versão francesa original tem um campo de voz não vazio que está vazio na inglesa; o candidato usa a versão inglesa. A confirmação recebida não detalha a cobertura de missões, dublagem, telas widescreen ou toque.

Em 27/10/2026, o candidato revisado foi assinado em v3 e passou na conferência de alinhamento de 16 KiB e no verificador dos 259 pares, incluindo os 110 títulos com caminhos internos ajustados, e seis catálogos. A biblioteca e os demais membros não envolvidos foram preservados em relação à base local, por hash da biblioteca e CRC/tamanho dos demais membros.

O primeiro candidato foi instalado no perfil de trabalho 11 com autorização explícita. Posteriormente, o pacote não apareceu instalado em nenhum perfil consultado. A pedido do usuário, o candidato revisado foi instalado por USB com `adb install --no-incremental -r --user 0`, sem desinstalação ou limpeza de dados executadas pelo agente. O Android retornou `Success`, confirmou versão 1.2.10 / código 38 e instalação apenas no perfil Pessoal; o SHA-256 instalado correspondeu ao candidato (`7333fef226ac9147fc8b40de0c49a6824304c2e3ec2b1a69c27e8de3d71514ea`). Isso ainda não comprova o funcionamento visual ou sonoro dos idiomas.

No S24, o jogo abriu na seleção de modo com textos e arte em português; a opção **English** foi observada no seletor de idioma. Capturas: `work/captures/language-personal-start.png` e `work/captures/language-personal-mode2.png`. Em 27/10/2026, o usuário testou e informou que o inglês está funcionando. O retorno ao português, os títulos de missão e a dublagem não foram descritos nessa confirmação.
