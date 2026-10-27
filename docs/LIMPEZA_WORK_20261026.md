# Limpeza de `work/` — 26/10/2026

## Motivo

O disco `C:` encheu durante o build do fundo da seleção de personagem. Os comandos do terminal falharam com `ENOSPC`, porque a saída era gravada no volume do sistema. Após liberar espaço, foram removidos os intermediários de build e os experimentos substituídos.

## Removido

**Intermediários de build** (regeneráveis pelos scripts):

- `work/s24-charsel-v2/`: `unsigned.apk`, `aligned.apk`, `unsigned-dataRegion.awb`, `signed.apk`, `signed.apk.idsig`.
- `work/s24-touchstart/`: `unsigned.apk`, `aligned.apk`, `installTimeDisc.awb`.
- `work/s24-charsel-v3/dataRegion.awb`: sobra da tentativa que parou por falta de espaço.

**Experimentos substituídos:**

- `work/s24-coverage/NarutoStorm-widescreen-responsive-unsigned.apk` (3,6 GB) e `NarutoStorm-edge-to-edge-unsigned.apk` (3,4 GB). Os `.repack.json` foram mantidos.
- `work/s24-coverage/patched-awb/installTime.awb` e `installTimeDisc.awb`.
- `work/candidates/widescreen-followup-20261026-02/installTime.awb` e `installTimeDisc.awb`. As capturas `device-*.png` e os manifests foram mantidos.
- `work/ptbr-translation/preview/installTimeDisc.awb` e o `.apk.idsig` do preview.
- Bibliotecas nativas de variantes: `work/native/exynos-depth-d32s8/`, `work/native/exynos-depth-restored/`, `work/s24-ui-touch/rebuilt/`, `work/s24-ui-touch/incremental/`, `work/s24-composition/patched/`, `work/restore-20261024/transform-audit/installed.so`.

Espaço livre em `C:` passou de 16 GB para 25 GB.

## Mantido

- `work/signing/`: chave e senha do certificado local. Não publicar.
- `work/s24-charsel/`: textura original extraída e as artes `fundo/` e `fundo-expandido/`.
- `work/s24-charsel-v2/extracted/`, `work/s24-charsel-v2/native/`, `work/s24-charsel-v2/candidate/`, `work/s24-charsel-v2/inventory.json`, `replacements*.json`: entradas para regenerar.
- `work/s24-touchstart/extracted/`, `candidate/`, `xtitle_fd01.png`: fonte e referência do texto "Toque para iniciar".
- `work/s24-charsel-v3/build.sh`: pipeline do fundo com escala 752, ainda não executado com sucesso.
- `work/s24-title/`, `work/s24-controls/`, `work/captures/`, `work/widescreen-expansion-source-20261026/`.
- `work/ptbr-translation/` (`translated/`, `jobs/`, `unique-source.json`, `coverage.json`, `final/`, `final-s24/`), `work/localization-format/`, `work/graphic-ptbr/`, `work/inventory/`.
- `work/external-single-1.2.10/`: base Exynos exigida por `scripts/patch-widescreen.py`.
- `work/native/libultimateninjastorm.so` e os manifests de análise citados em `docs/`.
- `work/candidates/widescreen-followup-20261026-02/libultimateninjastorm.so`, `source-native.so` e `source-assets/`: não estavam na lista de remoção.

## Não verificado

- `work/ptbr-translation/final/` e `final-s24/`: não foi conferido qual `installTimeDisc.awb` corresponde ao APK em `build/`. Mantidos por segurança.
- `work/decoded/` e `work/jadx/`: mantidos. São regeneráveis a partir do APK, mas refazer leva tempo.

## Como regenerar

- Fundo da seleção de personagem: `scripts/patch-charsel-bg-s24.py`, com entrada `msel1_bg.xfbin` extraído por `scripts/extract-cpk-files.py`.
- Texto "Toque para iniciar": `scripts/patch-touchstart-s24.py`, com entrada `xtitle.xfbin` do membro `assets/data/disc/installTimeDisc.awb`.
- Repack: `scripts/patch-cpk.py` (troca um arquivo dentro de um `.awb`) e `scripts/repack-native-apk.py` (monta o APK).
- Assinatura: `apksigner` do Build Tools 36.0.0, com `work/signing/naruto-local.p12`. Depois conferir com `zipalign -c -P 16 4`.

## Pendente

- Build do fundo com escala 752 (`work/s24-charsel-v3/build.sh`): não concluído. O erro anterior foi a falta de espaço.
- Build do texto menor: não gerado ainda na sequência final.
- Nenhuma das versões foi instalada ou testada no S24.
