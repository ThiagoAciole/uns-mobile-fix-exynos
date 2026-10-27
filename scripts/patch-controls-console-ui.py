"""Hide the battle touch HUD while Paddleboat controller 0 is active.

This is a second-stage patch for the device-validated GameSir-enabled library.
It does not add ABXY prompts or restore the Android remapping screen.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = '2923db436931bb2f3a0b7178a7b1c007434e28d269e5ec5a81c5be4a73e96db7'
BUILD_ID = 'c3e506f9be350dfb4a00c79228754028'
VA_DELTA = 0x4000
DRAW = 0x9F26A4
DRAW_RESUME = DRAW + 4
DRAW_PROLOGUE = bytes.fromhex('fd7bbea9')
MASK_CAVE = 0x9B134C
UI_CAVE = MASK_CAVE + 28
CAVE_END = 0x9B145C
STATUS_TARGET = 0x1188360
ITEM_LIST_DRAW = 0x12D1C30
NATIVE_MEMBER = 'lib/arm64-v8a/libultimateninjastorm.so'
DEFAULT_LLVM = Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/windows-x86_64/bin'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def branch(source, target):
    delta = target - source
    if delta % 4 or not -(1 << 27) <= delta < (1 << 27):
        raise ValueError('Destino B AArch64 fora do alcance ou desalinhado')
    return struct.pack('<I', 0x14000000 | ((delta // 4) & 0x3FFFFFF))


def verify_no_branch_into_cave(data):
    phoff = struct.unpack_from('<Q', data, 32)[0]
    phsize, phnum = struct.unpack_from('<HH', data, 54)
    for index in range(phnum):
        kind, flags, offset, va, _, filesz, _, _ = struct.unpack_from('<IIQQQQQQ', data, phoff + index * phsize)
        if kind != 1 or not flags & 1 or not va <= UI_CAVE < CAVE_END <= va + filesz:
            continue
        if va - offset != VA_DELTA:
            raise ValueError('Mapeamento VA/arquivo inesperado')
        for position in range(offset, offset + filesz - 3, 4):
            at = va + position - offset
            if UI_CAVE <= at < CAVE_END or at == 0xCEEFD4:
                continue
            word = struct.unpack_from('<I', data, position)[0]
            if word & 0x7C000000 != 0x14000000:
                continue
            immediate = word & 0x3FFFFFF
            if immediate & 0x2000000:
                immediate -= 0x4000000
            target = at + immediate * 4
            if UI_CAVE <= target < CAVE_END:
                raise ValueError(f'Branch existente entra na cave de UI: {at:#x} -> {target:#x}')
        return
    raise ValueError('Cave fora do segmento executável')


def build_patch(data, prior_manifest, llvm_bin):
    if sha(data) != SOURCE_SHA:
        raise ValueError('SHA-256 diferente da biblioteca GameSir validada')
    if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', data, 18)[0] != 183:
        raise ValueError('Esperado ELF64 little-endian AArch64')
    if data[0x318:0x328].hex() != BUILD_ID:
        raise ValueError('Build ID diferente')
    if not prior_manifest.get('enableGamepad') or prior_manifest.get('outputSha256', '').lower() != SOURCE_SHA:
        raise ValueError('Manifesto anterior não comprova o patch de gamepad esperado')
    base_sha = prior_manifest.get('sourceSha256', '').lower()
    if len(base_sha) != 64:
        raise ValueError('Manifesto anterior sem hash da biblioteca do APK base')
    if data[DRAW - VA_DELTA:DRAW - VA_DELTA + 4] != DRAW_PROLOGUE:
        raise ValueError('Prólogo de ccDuelPad::Draw diferente do esperado')
    mask_patch = next((p for p in prior_manifest.get('patches', [])
                       if p.get('purpose', '').startswith('Local gamepad mask stub')), None)
    if not mask_patch or mask_patch.get('elfVa') != hex(MASK_CAVE):
        raise ValueError('Manifesto não registra a cave preexistente do gamepad')
    old_stub = bytes.fromhex(mask_patch['after'])
    if len(old_stub) != 28 or data[MASK_CAVE - VA_DELTA:MASK_CAVE - VA_DELTA + len(old_stub)] != old_stub:
        raise ValueError('Stub de gamepad não confere com o manifesto')
    verify_no_branch_into_cave(data)

    with tempfile.TemporaryDirectory(prefix='storm-console-ui-') as folder:
        folder = Path(folder)
        obj, elf, binary = folder / 'console.o', folder / 'console.elf', folder / 'console.bin'
        def run(tool, *args):
            return subprocess.check_output([str(llvm_bin / tool), *map(str, args)], text=True)
        run('clang.exe', '--target=aarch64-linux-android28', '-c', ROOT / 'patches/controls-diag/console-ui.S', '-o', obj)
        run('ld.lld.exe', '-Ttext=' + hex(UI_CAVE), '--entry=console_draw',
            '--defsym=STATUS_TARGET=' + hex(STATUS_TARGET), '--defsym=DRAW_RESUME=' + hex(DRAW_RESUME),
            '--defsym=ITEM_LIST_DRAW=' + hex(ITEM_LIST_DRAW),
            obj, '-o', elf)
        run('llvm-objcopy.exe', '-O', 'binary', '--only-section=.text', elf, binary)
        payload = binary.read_bytes()
        if not payload or UI_CAVE + len(payload) > CAVE_END:
            raise ValueError('Stub de UI excede a cave validada')

    result = bytearray(data)
    new_entry = branch(DRAW, UI_CAVE)
    result[DRAW - VA_DELTA:DRAW - VA_DELTA + 4] = new_entry
    cave_offset = UI_CAVE - VA_DELTA
    result[cave_offset:cave_offset + len(payload)] = payload
    output = bytes(result)
    if len(output) != len(data) or output[DRAW - VA_DELTA:DRAW - VA_DELTA + 4] != new_entry:
        raise AssertionError('Releitura do patch nativo falhou')
    manifest = {
        'status': 'host-verified-controller-conditional-battle-touch-hud-not-device-tested',
        'sourceSha256': base_sha,
        'inputLibrarySha256': SOURCE_SHA,
        'outputSha256': sha(output),
        'buildId': BUILD_ID,
        'caveVa': hex(UI_CAVE),
        'caveBytes': len(payload),
        'controllerStatus': {'api': 'Paddleboat_getControllerStatus', 'index': 0, 'activeValue': 1},
        'patches': [
            {'elfVa': hex(DRAW), 'before': DRAW_PROLOGUE.hex(), 'after': new_entry.hex(),
             'purpose': 'Route ccDuelPad::Draw through controller status gate'},
            {'elfVa': hex(UI_CAVE), 'before': data[cave_offset:cave_offset + len(payload)].hex(),
             'after': payload.hex(), 'purpose': 'Skip battle touch HUD while controller 0 is active'}
        ],
        'limit': 'Hides the touch HUD in battle while preserving the original item-list draw; ABXY prompts, remapping UI, menus and device acceptance are not included.'
    }
    return output, manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True, help='Biblioteca com o patch de gamepad já validado')
    parser.add_argument('--output', type=Path, help='Nova biblioteca (nunca sobrescreve arquivos)')
    parser.add_argument('--llvm-bin', type=Path, default=DEFAULT_LLVM)
    parser.add_argument('--check-only', action='store_true', help='Compila e valida sem gravar')
    args = parser.parse_args()
    source = args.input.resolve()
    if not source.is_file():
        parser.error('Biblioteca de entrada não encontrada')
    if not args.check_only and args.output is None:
        parser.error('--output é obrigatório sem --check-only')
    if args.output is not None:
        output_path = args.output.resolve()
        if output_path == source or output_path.is_relative_to(ROOT / 'build') or output_path.is_relative_to(ROOT / 'original'):
            parser.error('Saída deve ser separada, fora de build/ e original/')
        if not args.check_only and (output_path.exists() or Path(str(output_path) + '.patch.json').exists()):
            raise FileExistsError('Saída ou manifesto existente; preservado')
    manifest_path = Path(str(source) + '.patch.json')
    prior_manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    result, manifest = build_patch(source.read_bytes(), prior_manifest, args.llvm_bin)
    if args.check_only:
        print(f'Patch condicional validado; {manifest["caveBytes"]} bytes de stub; SHA de saída {manifest["outputSha256"]}')
        return 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open('xb') as stream:
        stream.write(result)
    Path(str(output_path) + '.patch.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    if sha(output_path.read_bytes()) != manifest['outputSha256']:
        raise RuntimeError('Hash da saída difere do manifesto')
    print(f'Biblioteca criada: {output_path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
