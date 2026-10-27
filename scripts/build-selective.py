#!/usr/bin/env python3
"""Gera o APK com os ajustes escolhidos, a partir do APK 1.2.10 original.

Ajustes:
  (sempre)      correção Exynos: base exigida pelo widescreen e pelos demais ajustes
  --ptbr        textos e letreiros em português (Brasil)
  --widescreen  tela larga (patch-widescreen.py, parte do Exynos)
  --controller-base-apk  usa como base um APK S24 cuja biblioteca já tenha o hash widescreen aceito
  --controls    habilita a máscara Paddleboat no --controller-base-apk validado com GameSir-X5 Lite
  --console-ui  oculta o HUD tátil da batalha com gamepad ativo (experimental; exige --controls)

Saída: um único APK final, que substitui o anterior (padrão: build/Naruto Ultimate Ninja Storm.apk)
e um manifesto ao lado. Todos os intermediários ficam em work/build-tmp-* e são apagados
ao fim de cada execução, mesmo se a build falhar.

Uso:
  python scripts/build-selective.py --apk CAMINHO/Ultimate-Ninja-Storm-1.2.10.apk --keystore K --ks-pass F [--widescreen] [--ptbr] [--controls] [--console-ui]
  python scripts/build-selective.py --apk CAMINHO/...apk --unsigned                 # sem assinatura, não instalável
  python scripts/build-selective.py --controller-base-apk build/UNSM-S24-FIX-PTBR-EN-v2.apk --controls --unsigned --output work/candidate.apk
  python scripts/build-selective.py --clean                                         # remove restos de execuções anteriores
"""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORK_DIR = ROOT / 'work'
TEMP_PREFIX = 'build-tmp-'
DEFAULT_OUTPUT = ROOT / 'build' / 'Naruto Ultimate Ninja Storm.apk'
NATIVE_MEMBER = 'lib/arm64-v8a/libultimateninjastorm.so'
# SHA-256 da biblioteca do APK 1.2.10 recebido, registrado em docs/APK_UNICO_1_2_10.md.
ORIGINAL_LIB_SHA256 = 'C631E7127E73ECDE32DA7C8B8054AC6810A375875CD00749D3F4DF5DB29DB79E'
CONTROLLER_BASE_LIB_SHA256 = '8797E4446449B505BD20D704C4123F4BDBEDEEC8B9E1E71A87414A876572CFD0'
SDK = Path.home() / 'AppData' / 'Local' / 'Android' / 'Sdk'


def sha256(data):
    return hashlib.sha256(data).hexdigest().upper()


def run(*args, cwd=ROOT):
    command = [str(arg) for arg in args]
    print('>', ' '.join(command), flush=True)
    subprocess.run(command, cwd=cwd, check=True)


def latest_build_tools():
    versions = sorted((SDK / 'build-tools').iterdir(), key=lambda p: [int(x) for x in p.name.split('.') if x.isdigit()])
    if not versions:
        raise FileNotFoundError(f'Nenhum build-tools em {SDK / "build-tools"}; use --build-tools.')
    return versions[-1]


def clean_stale():
    """Remove pastas temporárias que sobraram de execuções interrompidas."""
    removed = [p for p in WORK_DIR.glob(TEMP_PREFIX + '*') if p.is_dir()]
    for path in removed:
        shutil.rmtree(path, ignore_errors=True)
    return len(removed)


def build_in(tmp, origin, native_bytes, args, build_tools):
    """Gera o APK final dentro de tmp. Devolve (apk, biblioteca final)."""
    input_lib = tmp / 'input' / 'libultimateninjastorm.so'
    input_lib.parent.mkdir()
    input_lib.write_bytes(native_bytes)

    # 1. Exynos (sempre). O script PowerShell usa caminhos relativos à raiz do projeto.
    exynos_lib = tmp / 'exynos' / 'libultimateninjastorm.so'
    run('powershell', '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', 'scripts/patch-exynos-depth.ps1',
        '-InputLibrary', os.path.relpath(input_lib, ROOT),
        '-OutputLibrary', os.path.relpath(exynos_lib, ROOT))
    final_lib = exynos_lib

    # 2. Widescreen (depende do Exynos).
    if args.widescreen:
        widescreen_lib = tmp / 'widescreen' / 'libultimateninjastorm.so'
        run(sys.executable, 'scripts/patch-widescreen.py', '--input', exynos_lib, '--output', widescreen_lib)
        final_lib = widescreen_lib

    # 3. Textos pt-BR (gera o plano de substituição do APK).
    replacements = None
    if args.ptbr:
        ptbr_dir = tmp / 'ptbr'
        run(sys.executable, 'scripts/build-ptbr-assets.py', origin, ptbr_dir)
        replacements = ptbr_dir / 'apk-plan.json'

    # 4. Repack do APK com a biblioteca final e, se houver, as substituições pt-BR.
    unsigned = tmp / 'unsigned.apk'
    repack = [sys.executable, 'scripts/repack-native-apk.py', origin, final_lib, unsigned]
    if replacements:
        repack += ['--replacements', replacements]
    run(*repack)

    # 5. Alinhamento e assinatura, quando há keystore.
    if args.unsigned:
        return unsigned, final_lib
    aligned = tmp / 'aligned.apk'
    signed = tmp / 'signed.apk'
    run(build_tools / 'zipalign.exe', '-P', '16', '-f', '4', unsigned, aligned)
    sign = [build_tools / 'apksigner.bat', 'sign', '--ks', args.keystore,
            '--ks-pass', f'file:{args.ks_pass.resolve()}', '--out', signed]
    if args.key_alias:
        sign += ['--ks-key-alias', args.key_alias]
    run(*sign, aligned)
    run(build_tools / 'apksigner.bat', 'verify', signed)
    return signed, final_lib


def build_from_controller_base(tmp, base_apk, args, build_tools):
    """Apply controller patches to the previously accepted S24 widescreen APK."""
    controls_lib = tmp / 'controls' / 'libultimateninjastorm.so'
    run(sys.executable, 'scripts/patch-controls-flow-diag.py', '--apk', base_apk,
        '--output', controls_lib, '--enable-gamepad', '--no-flow-logs')
    final_lib = controls_lib
    if args.console_ui:
        console_ui_lib = tmp / 'console-ui' / 'libultimateninjastorm.so'
        run(sys.executable, 'scripts/patch-controls-console-ui.py', '--input', final_lib,
            '--output', console_ui_lib)
        final_lib = console_ui_lib

    replacements = None
    if args.console_ui:
        prompts_dir = tmp / 'controller-prompts'
        run(sys.executable, 'scripts/patch-controls-prompts.py', '--apk', base_apk,
            '--output-dir', prompts_dir)
        replacements = prompts_dir / 'apk-plan.json'

    unsigned = tmp / 'unsigned.apk'
    repack = [sys.executable, 'scripts/repack-native-apk.py', base_apk, final_lib, unsigned]
    if replacements:
        repack += ['--replacements', replacements]
    run(*repack)
    if args.unsigned:
        return unsigned, final_lib
    aligned = tmp / 'aligned.apk'
    signed = tmp / 'signed.apk'
    run(build_tools / 'zipalign.exe', '-P', '16', '-f', '4', unsigned, aligned)
    sign = [build_tools / 'apksigner.bat', 'sign', '--ks', args.keystore,
            '--ks-pass', f'file:{args.ks_pass.resolve()}', '--out', signed]
    if args.key_alias:
        sign += ['--ks-key-alias', args.key_alias]
    run(*sign, aligned)
    run(build_tools / 'apksigner.bat', 'verify', signed)
    return signed, final_lib


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--apk', type=Path, help='Caminho do seu APK 1.2.10 original')
    parser.add_argument('--controller-base-apk', type=Path,
                        help='APK widescreen S24 aceito, com biblioteca SHA-256 8797E444…')
    parser.add_argument('--output', type=Path, default=DEFAULT_OUTPUT, help='APK final (substitui o existente)')
    parser.add_argument('--ptbr', action='store_true', help='Incluir textos e letreiros pt-BR')
    parser.add_argument('--widescreen', action='store_true', help='Incluir tela larga')
    parser.add_argument('--controls', action='store_true', help='Ativar GameSir/Paddleboat no --controller-base-apk')
    parser.add_argument('--console-ui', action='store_true',
                        help='Ocultar HUD tátil da batalha e trocar prompts de seleção triângulo/círculo por Y/B (estático; exige --controls)')
    parser.add_argument('--keystore', type=Path, help='Keystore local para assinar')
    parser.add_argument('--ks-pass', type=Path, help='Arquivo com a senha do keystore')
    parser.add_argument('--key-alias', help='Alias da chave, se o keystore tiver mais de uma')
    parser.add_argument('--unsigned', action='store_true', help='Gerar sem assinatura (não instalável)')
    parser.add_argument('--build-tools', type=Path, help='Pasta build-tools (padrão: a mais recente do SDK)')
    parser.add_argument('--clean', action='store_true', help='Só remove restos de execuções anteriores')
    args = parser.parse_args()

    if args.clean:
        print(f'Pastas temporárias removidas: {clean_stale()}')
        return 0
    if bool(args.apk) == bool(args.controller_base_apk):
        parser.error('Informe exatamente um entre --apk e --controller-base-apk')
    if args.console_ui and not args.controls:
        parser.error('--console-ui exige --controls')
    if args.controller_base_apk and not args.controls:
        parser.error('--controller-base-apk exige --controls')
    if args.controller_base_apk and (args.ptbr or args.widescreen):
        parser.error('--controller-base-apk já contém sua composição; não repita --ptbr/--widescreen')
    if args.controls and not args.controller_base_apk:
        parser.error('--controls precisa da base S24 exata; use --controller-base-apk')
    if args.console_ui and not args.controller_base_apk:
        parser.error('--console-ui exige --controller-base-apk')
    if (args.keystore is None) != (args.ks_pass is None):
        parser.error('--keystore e --ks-pass devem ser usados juntos.')
    if args.keystore is None and not args.unsigned:
        parser.error('Informe --keystore e --ks-pass, ou --unsigned para gerar sem assinatura.')

    origin = (args.controller_base_apk or args.apk).resolve()
    if not origin.is_file() or origin.suffix.lower() != '.apk':
        print(f'APK não encontrado ou extensão inválida: {origin}', file=sys.stderr)
        return 1
    final_path = args.output.resolve()
    if final_path == origin or final_path.is_relative_to(ROOT / 'origin') or final_path.is_relative_to(ROOT / 'original'):
        print(f'Saída proibida; é a entrada ou fica em pasta protegida: {final_path}', file=sys.stderr)
        return 1
    with zipfile.ZipFile(origin) as apk:
        native_bytes = apk.read(NATIVE_MEMBER)
    expected_library = CONTROLLER_BASE_LIB_SHA256 if args.controller_base_apk else ORIGINAL_LIB_SHA256
    if sha256(native_bytes) != expected_library:
        expected_label = 'base S24 widescreen aceita' if args.controller_base_apk else 'base original 1.2.10'
        print(f'A biblioteca do APK não corresponde à {expected_label}; abortado.', file=sys.stderr)
        return 1

    build_tools = None if args.unsigned else (args.build_tools or latest_build_tools())
    WORK_DIR.mkdir(exist_ok=True)
    clean_stale()
    tmp = Path(tempfile.mkdtemp(prefix=TEMP_PREFIX, dir=WORK_DIR))
    # Cópia com nome provisório ao lado do destino, para a troca final ser atômica.
    staged = final_path.with_name(final_path.name + '.partial')
    try:
        if args.controller_base_apk:
            final_apk, final_lib = build_from_controller_base(tmp, origin, args, build_tools)
        else:
            final_apk, final_lib = build_in(tmp, origin, native_bytes, args, build_tools)
        final_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(final_apk, staged)
        os.replace(staged, final_path)

        manifest = {
            'origin': str(origin),
            'originLibrarySha256': expected_library,
            'sourceMode': 'accepted-s24-controller-base' if args.controller_base_apk else 'original-1.2.10',
            'features': ({'controls': True, 'consoleUi': args.console_ui,
                          'controllerPromptSkin': args.console_ui, 'baseComposition': 'preserved'}
                         if args.controller_base_apk else
                         {'exynos': True, 'widescreen': args.widescreen, 'ptbr': args.ptbr,
                          'controls': False, 'consoleUi': False}),
            'finalLibrarySha256': sha256(final_lib.read_bytes()),
            'apk': str(final_path),
            'apkSha256': sha256(final_path.read_bytes()),
            'signed': not args.unsigned,
        }
        manifest_path = final_path.with_name(final_path.name + '.build.json')
        manifest_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(f'APK gerado (substituiu o anterior, se existia): {final_path}')
        print(f'Manifesto: {manifest_path}')
        return 0
    finally:
        if staged.exists():
            staged.unlink()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == '__main__':
    sys.exit(main())
