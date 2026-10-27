"""Gera a biblioteca nativa de diagnóstico do controle externo (uso pessoal, não jogável).

Base: biblioteca 1.2.10 com correção Exynos. Hooks só registram no logcat (tag CTRLDIAG).
A função DrawLetterBox é desativada para abrir espaço de código; as barras decorativas somem.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = 'ccea158f39368ed13254a2f29e608e1fd7e5dcb4a1427ed4461b6a05f3c194ca'
BUILD_ID = 'c3e506f9be350dfb4a00c79228754028'
CAVE = 0x9B12C0  # Após o RET que desativa DrawLetterBox.
CAVE_END = 0x9B145C
GOT_LOG = 0x13BC798  # R_AARCH64_JUMP_SLOT de __android_log_print.
PI_PLT = 0x1314550  # PLT chamado por NotifyInputEvent para Paddleboat_processInputEvent.
ENTRY_CONT = 0xF75198  # Instrução seguinte a 'ldr w8, [x0, #0x74]' em IsControllerConnected.
ISCONN_ENTRY = 0xF75194
NIE_CALL = 0x9E7D40  # bl PI_PLT dentro de NotifyInputEvent.
LETTERBOX_ENTRY = 0x9B12BC
RET = 0xD65F03C0


def sha(data):
    return hashlib.sha256(data).hexdigest()


def branch(source, target, link=False):
    delta = target - source
    if delta % 4 or not -(1 << 27) <= delta < (1 << 27):
        raise ValueError('AArch64 branch target out of range or unaligned')
    opcode = 0x94000000 if link else 0x14000000
    return struct.pack('<I', opcode | ((delta // 4) & 0x3FFFFFF))


def run(*args):
    return subprocess.check_output([str(arg) for arg in args], text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'work/external-single-1.2.10/patched/libultimateninjastorm.so')
    parser.add_argument('--output', type=Path, default=ROOT / 'work/controls-diag/patched/libultimateninjastorm.so')
    parser.add_argument('--llvm-bin', type=Path, default=Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/windows-x86_64/bin')
    parser.add_argument('--check-only', action='store_true', help='Monta e valida sem gravar a biblioteca')
    args = parser.parse_args()
    source, output = args.input.resolve(), args.output.resolve()
    manifest_path = Path(str(output) + '.patch.json')
    if source == output or output.is_relative_to(ROOT / 'original'):
        raise ValueError('Saída deve ser separada e fora de original/')
    if not args.check_only and (output.exists() or manifest_path.exists()):
        raise FileExistsError('Saída ou manifesto já existe; preservado')
    data = source.read_bytes()
    if sha(data) != SOURCE_SHA:
        raise ValueError('Entrada diferente da biblioteca 1.2.10 com correção Exynos')
    if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', data, 18)[0] != 183:
        raise ValueError('Esperado ELF64 little-endian AArch64')
    if data[0x318:0x328].hex() != BUILD_ID:
        raise ValueError('Build ID diferente')

    with tempfile.TemporaryDirectory(prefix='storm-ctrldiag-') as temp:
        temp = Path(temp)
        obj, elf, binary = temp / 'stubs.o', temp / 'stubs.elf', temp / 'stubs.bin'
        run(args.llvm_bin / 'clang.exe', '--target=aarch64-linux-android28', '-c', ROOT / 'patches/controls-diag/stubs.S', '-o', obj)
        run(args.llvm_bin / 'ld.lld.exe', '-Ttext=' + hex(CAVE), '--entry=ctrl_fields_hook',
            '--defsym=GOT_LOG=' + hex(GOT_LOG), '--defsym=PI_PLT=' + hex(PI_PLT),
            '--defsym=ENTRY_CONT=' + hex(ENTRY_CONT), obj, '-o', elf)
        run(args.llvm_bin / 'llvm-objcopy.exe', '-O', 'binary', '--only-section=.text', elf, binary)
        payload = binary.read_bytes()
        symbols = {}
        for line in run(args.llvm_bin / 'llvm-nm.exe', '--defined-only', elf).splitlines():
            fields = line.split()
            if len(fields) == 3 and fields[2] in {'ctrl_fields_hook', 'nie_hook'}:
                symbols[fields[2]] = int(fields[0], 16)
        if len(symbols) != 2 or CAVE + len(payload) > CAVE_END:
            raise ValueError('Símbolos inválidos ou cave estourada')

    patches = []
    result = bytearray(data)

    def put(va, expected, replacement, purpose):
        offset = va - 0x4000
        if data[offset:offset + len(replacement)] != expected:
            raise ValueError(f'Bytes inesperados em ELF {va:#x}: {purpose}')
        result[offset:offset + len(replacement)] = replacement
        patches.append({'elfVa': hex(va), 'offset': offset, 'fileOffset': hex(offset),
                        'before': expected.hex(), 'after': replacement.hex(), 'purpose': purpose})

    # Bytes esperados foram conferidos com llvm-objdump na biblioteca de entrada.
    put(LETTERBOX_ENTRY, struct.pack('<I', 0xD103C3FF), struct.pack('<I', RET), 'Desativa DrawLetterBox (abre cave)')
    put(ISCONN_ENTRY, struct.pack('<I', 0xB9407408), branch(ISCONN_ENTRY, symbols['ctrl_fields_hook']), 'Registra campos de IsControllerConnected')
    put(NIE_CALL, struct.pack('<I', 0x9424B204), branch(NIE_CALL, symbols['nie_hook'], link=True), 'Registra eventos de entrada antes de Paddleboat_processInputEvent')
    if result[CAVE - 0x4000 - 4:CAVE - 0x4000] != struct.pack('<I', RET):
        raise ValueError('Cave precisa começar logo após o RET de DrawLetterBox')
    result[CAVE - 0x4000:CAVE - 0x4000 + len(payload)] = payload
    patches.append({'elfVa': hex(CAVE), 'offset': CAVE - 0x4000, 'fileOffset': hex(CAVE - 0x4000),
                    'before': None, 'after': payload.hex(), 'purpose': 'Stubs de diagnóstico (CTRLDIAG)'})

    if len(result) != len(data) or result[0x6BF964:0x6BF968] != data[0x6BF964:0x6BF968]:
        raise AssertionError('Tamanho do ELF ou correção Exynos mudou')
    parent_path = Path(str(source) + '.patch.json')
    parent_bytes = parent_path.read_bytes()
    parent_patch = json.loads(parent_bytes.decode('utf-8-sig'))
    if parent_patch['outputSha256'].lower() != sha(data):
        raise ValueError('Manifesto Exynos não corresponde à entrada')
    manifest = {'status': 'diagnostic-only-not-game-validated', 'buildId': BUILD_ID,
                'source': parent_patch['source'], 'sourceSha256': parent_patch['sourceSha256'],
                'exynosInputSha256': SOURCE_SHA, 'outputSha256': sha(result), 'caveVa': hex(CAVE),
                'caveBytes': len(payload), 'symbols': {key: hex(value) for key, value in symbols.items()},
                'parentPatch': {'path': str(parent_path), 'sha256': sha(parent_bytes)},
                'patches': patches,
                'limit': 'Somente diagnóstico. DrawLetterBox desativada. Não usar como build de jogo.'}
    if not args.check_only:
        if source.read_bytes() != data:
            raise RuntimeError('Entrada mudou durante a geração')
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(result)
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        if sha(output.read_bytes()) != manifest['outputSha256']:
            raise RuntimeError('Hash da saída diferente do esperado')
    print(json.dumps({key: manifest[key] for key in ['status', 'sourceSha256', 'outputSha256', 'caveBytes', 'symbols']}, indent=2))
    print('Verificações passaram; nenhuma biblioteca gravada.' if args.check_only else str(output))


if __name__ == '__main__':
    main()
