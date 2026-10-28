"""Compoe um candidato experimental de prompts na selecao Android.

Nao produz APK nem instala. A interface e o carregamento ELF ainda exigem teste no S24.
"""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = '557b842e7f3372b1498843fce78df8b32bab43e26030d4092ef6c66ce290cb9e'
PRIOR_INPUT_SHA256 = '2923db436931bb2f3a0b7178a7b1c007434e28d269e5ec5a81c5be4a73e96db7'
VA_DELTA = 0x4000
DRAW = 0x9F28FC
DESTROY = 0xADEF78
STAGE_DRAW, STAGE_DESTROY = 0x9F1AD0, 0xD04890
EXPECTED = {DRAW: bytes.fromhex('fd7bbea9'), DESTROY: bytes.fromhex('ff8301d1'), STAGE_DRAW: bytes.fromhex('fd7bbea9'), STAGE_DESTROY: bytes.fromhex('ff4301d1')}
DEFAULT_LLVM = (Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018'
                / 'toolchains/llvm/prebuilt/windows-x86_64/bin')

spec = importlib.util.spec_from_file_location('extend_controls_elf', ROOT / 'scripts/extend-controls-elf.py')
extender = importlib.util.module_from_spec(spec)
spec.loader.exec_module(extender)


def branch(source, target):
    delta = target - source
    if delta % 4 or not -(1 << 27) <= delta < (1 << 27):
        raise ValueError('Branch ARM64 fora do alcance ou desalinhado')
    return struct.pack('<I', 0x14000000 | ((delta // 4) & 0x3ffffff))


def build_patch(data, prior_manifest, llvm_bin):
    if hashlib.sha256(data).hexdigest() != SOURCE_SHA256:
        raise ValueError('Biblioteca diferente da F1.1 aceita')
    if (prior_manifest.get('outputSha256', '').lower() != SOURCE_SHA256 or
            prior_manifest.get('inputLibrarySha256', '').lower() != PRIOR_INPUT_SHA256):
        raise ValueError('Manifesto anterior nao identifica a F1.1 esperada')
    for va, expected in EXPECTED.items():
        offset = va - VA_DELTA
        if data[offset:offset + len(expected)] != expected:
            raise ValueError(f'Prologo inesperado em {va:#x}')
    expanded, layout = extender.reserve_executable_space(data)
    symbols = {
        'game_controller_status': 0x1188360,
        'game_nucc_global_got': 0x13B3E10,
        'game_select_draw_resume': DRAW + 4,
        'game_select_destroy_resume': DESTROY + 4,
        'game_stage_draw_resume': STAGE_DRAW + 4,
        'game_stage_destroy_resume': STAGE_DESTROY + 4,
        'game_button_is_shown': 0x99B5AC,
        'game_sprite_create': 0x9B5BD8,
        'game_sprite_assign': 0xAB8D04,
        'game_sprite_release': 0xB4C374,
        'game_sprite_set_pos': 0x96A8C4,
        'game_sprite_set_scale': 0x96A164,
        'game_sprite_draw': 0x926EC0,
        'game_font_create': 0x9BB770,
        'game_font_print': 0x91D3D0,
        'game_font_assign': 0x9F1184,
        'game_font_release': 0xADDFC8,
        'abxy_state_address': layout['scratch_va'],
    }
    sources = ['abxy-select-hook.S', 'abxy-mapping.c', 'abxy-select.c', 'abxy-select-engine.c']
    with tempfile.TemporaryDirectory(prefix='storm-select-prompts-') as folder:
        folder = Path(folder)
        objects = []
        for index, name in enumerate(sources):
            obj = folder / f'{index}.o'
            command = [str(llvm_bin / 'clang.exe'), '--target=aarch64-linux-android28',
                       '-ffreestanding', '-fno-stack-protector', '-fno-jump-tables',
                       '-fno-asynchronous-unwind-tables', '-fno-unwind-tables', '-fno-pic',
                       '-Os', '-c', str(ROOT / 'patches/controls-diag' / name), '-o', str(obj)]
            subprocess.run(command, check=True, capture_output=True)
            objects.append(obj)
        elf, raw = folder / 'payload.elf', folder / 'payload.bin'
        command = [str(llvm_bin / 'ld.lld.exe'), '-Ttext=' + hex(layout['code_va']),
                   '--entry=abxy_select_draw_hook', '--no-undefined']
        command += ['--defsym=' + name + '=' + hex(value) for name, value in symbols.items()]
        command += [*map(str, objects), '-o', str(elf)]
        subprocess.run(command, check=True, capture_output=True)
        relocations = subprocess.check_output([str(llvm_bin / 'llvm-readelf.exe'), '-r', str(elf)], text=True)
        if 'There are no relocations' not in relocations:
            raise ValueError('Payload contem relocacoes nao resolvidas')
        sections = subprocess.check_output([str(llvm_bin / 'llvm-readelf.exe'), '-S', '-W', str(elf)], text=True)
        if '.rodata' in sections or '.data ' in sections or '.bss ' in sections:
            raise ValueError('Payload exige secoes alem de .text')
        names = subprocess.check_output([str(llvm_bin / 'llvm-nm.exe'), '-n', str(elf)], text=True)
        addresses = {}
        for line in names.splitlines():
            parts = line.split()
            if len(parts) == 3 and parts[2] in ('abxy_select_draw_hook', 'abxy_select_destroy_hook', 'abxy_stage_draw_hook', 'abxy_stage_destroy_hook'):
                addresses[parts[2]] = int(parts[0], 16)
        if len(addresses) != 4:
            raise ValueError('Entradas do payload nao encontradas')
        subprocess.run([str(llvm_bin / 'llvm-objcopy.exe'), '-O', 'binary', '--only-section=.text',
                        str(elf), str(raw)], check=True, capture_output=True)
        payload = raw.read_bytes()
    if not payload or len(payload) > layout['code_capacity']:
        raise ValueError('Payload fora da reserva executavel')
    if any(not layout['code_va'] <= address < layout['code_va'] + len(payload) for address in addresses.values()):
        raise ValueError('Entradas fora do payload')
    result = bytearray(expanded)
    start = layout['code_offset']
    if any(result[start:start + len(payload)]):
        raise ValueError('Reserva executavel nao esta vazia')
    result[start:start + len(payload)] = payload
    patches = []
    for va, name in ((DRAW, 'abxy_select_draw_hook'), (DESTROY, 'abxy_select_destroy_hook'), (STAGE_DRAW, 'abxy_stage_draw_hook'), (STAGE_DESTROY, 'abxy_stage_destroy_hook')):
        offset = va - VA_DELTA
        after = branch(va, addresses[name])
        result[offset:offset + 4] = after
        patches.append({'elfVa': hex(va), 'before': EXPECTED[va].hex(), 'after': after.hex(),
                        'targetVa': hex(addresses[name]), 'purpose': name})
    output = bytes(result)
    restored = bytearray(output)
    restored[start:start + len(payload)] = bytes(len(payload))
    for item in patches:
        offset = int(item['elfVa'], 16) - VA_DELTA
        if restored[offset:offset + 4].hex() != item['after']:
            raise AssertionError('Releitura do branch falhou')
        restored[offset:offset + 4] = bytes.fromhex(item['before'])
    if bytes(restored) != expanded:
        raise AssertionError('Alteracoes fora do payload e hooks esperados')
    report = {'status': 'host-only-experimental-select-prompts-not-device-tested',
              'inputLibrarySha256': SOURCE_SHA256, 'sourceSha256': SOURCE_SHA256,
              'outputSha256': hashlib.sha256(output).hexdigest(), 'buildId': extender.BUILD_ID,
              'payloadVa': hex(layout['code_va']), 'payloadBytes': len(payload),
              'scratchVa': hex(layout['scratch_va']), 'patches': patches,
              'limitations': ['selecao de personagem e arena: sprites A/Y e texto START',
                              'posicao dos sprites e carregamento ELF nao validados no aparelho',
                              'outros menus, tutoriais e bindings personalizados nao validados']}
    return output, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-only', action='store_true')
    mode.add_argument('--output', type=Path, help='Biblioteca nova fora de build/ e original/')
    parser.add_argument('--llvm-bin', type=Path, default=DEFAULT_LLVM)
    args = parser.parse_args()
    if args.output:
        output = args.output.resolve()
        if output == args.input.resolve() or output.is_relative_to(ROOT / 'build') or output.is_relative_to(ROOT / 'original'):
            parser.error('Saida deve ser separada e fora de build e original')
        if output.exists() or Path(str(output) + '.patch.json').exists():
            parser.error('Saida ou manifesto existente; preservado')
    prior = json.loads(Path(str(args.input) + '.patch.json').read_text(encoding='utf-8-sig'))
    result, report = build_patch(args.input.read_bytes(), prior, args.llvm_bin)
    if args.output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(result)
        if hashlib.sha256(output.read_bytes()).hexdigest() != report['outputSha256']:
            raise RuntimeError('Hash da biblioteca gravada difere do manifesto')
        with Path(str(output) + '.patch.json').open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
