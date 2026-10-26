# Candidato de UI e toque — 26/10/2026

APK: `build/Naruto Ultimate Ninja Storm - UI e toque ajustados.apk`.

**Achado posterior:** este candidato ainda contém uma chamada 16:9 em `nuccSys::ChangeRender`. A [análise da composição](WIDESCREEN_COMPOSITION_FINDINGS.md) reproduziu em emulação a imagem de 2340 px iniciada em X=210 por essa rota. O ajuste de UI/toque não deve ser tratado como correção completa do recorte; a composição precisa ser validada separadamente.

Base: último build documentado de 24/10, SHA-256 `717a253525f03e3f5d7fe308f7c3bdddc1927b9a97b01bf5c0fbabb4375a2b3d`. Essa base e a cópia restaurada em `build/Naruto Ultimate Ninja Storm.apk` foram preservadas.

## Alteração

O candidato integra a origem atual `ui_uniform = -metade da largura do viewport` e ajusta `input_inverse` para a mesma origem: após a normalização original do engine, o toque X é multiplicado por `k = largura × 9 / (altura × 16)`, sem o deslocamento em torno de 640 usado pelo stub anterior. Y permanece inalterado. A guarda existente mantém o caminho sem escala adicional quando `k <= 1`, sistema nulo ou altura zero.

Foi alterado o corpo de `input_inverse` em `patches/widescreen/stubs.S` e atualizada a fórmula de conferência em `scripts/patch-widescreen.py`. O `ui_uniform` já estava alterado no fonte antes desta geração; ele agora é integrado junto da conversão de toque correspondente.

Os 101 bytes diferentes da biblioteca do build de 24/10 estão contidos na cave antiga de 140 bytes e no branch de toque de 4 bytes. A biblioteca reconstruída usa 112 bytes de stubs, mantém tamanho total e patch Exynos. SHA-256 nativo: `1e72dbed69038ce1b8561c2091b8ff9bc678dcf643819d55042d90e6875c9a2a`.

Os dois bancos de UI são os mesmos de 24/10. Não foram integrados os candidatos de cobertura/fade, camadas de título ou imagem de controles de 26/10. Áudio/vídeo foram comparados por SHA-256 com os payloads armazenados no APK base e preservados; seus CRCs ZIP antigos, inconsistentes, são recalculados durante o empacotamento. Isso valida os bytes preservados, não o playback.

## Validação

O teste de correspondência falhou com o par de stubs anterior à mudança e passou após o ajuste de toque. A emulação executa 6 preparações de UI e 18 conversões completas de toque para 1920×1080, 2340×1080 e 2560×1080. Verifica ida/volta X, Y e registrador preservado, usando os bytes ARM64 montados do fonte atual.

```powershell
python work/s24-ui-touch/verify_transforms.py
```

O estado de composição usado na emulação é sintético: fullscreen e offsets zero. Essas verificações não identificam nem reproduzem integralmente a rota real do título/termos. O candidato precisa de teste no S24 para confirmar recorte, alinhamento de botões e toque em outras telas. Não foi instalado nesta entrega.

Relatórios, planos incrementais, cópias dos dois fontes anteriores à mudança, verificação de assinatura e hash final ficam em `work/s24-ui-touch/`. O resultado final do empacotamento deve ser consultado em `build-report.json` nessa pasta; o hash do APK também acompanha o arquivo em `.sha256`.
