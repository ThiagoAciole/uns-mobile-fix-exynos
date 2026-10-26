"""Build the diagnostic 1.2.10 Exynos widescreen candidate on a separate ELF copy."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = 'ccea158f39368ed13254a2f29e608e1fd7e5dcb4a1427ed4461b6a05f3c194ca'
CAVE = 0x9B12C0  # DrawLetterBox body, after the replacement RET.
CAVE_END = 0x9B145C  # Exact symbol size 0x1a0.


def sha(data):
    return hashlib.sha256(data).hexdigest()


def branch(source, target):
    delta = target - source
    if delta % 4 or not -(1 << 27) <= delta < (1 << 27):
        raise ValueError('AArch64 B target out of range or unaligned')
    return struct.pack('<I', 0x14000000 | ((delta // 4) & 0x3FFFFFF))


def run(*args):
    return subprocess.check_output([str(arg) for arg in args], text=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT / 'work/external-single-1.2.10/patched/libultimateninjastorm.so')
    parser.add_argument('--output', type=Path, default=ROOT / 'work/widescreen/patched/libultimateninjastorm.so')
    parser.add_argument('--llvm-bin', type=Path, default=Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/windows-x86_64/bin')
    parser.add_argument('--check-only', action='store_true', help='Assemble and validate guards without writing an ELF')
    args = parser.parse_args()
    source, output = args.input.resolve(), args.output.resolve()
    manifest_path = Path(str(output) + '.patch.json')
    if source == output or output.is_relative_to(ROOT / 'original'):
        raise ValueError('Output must be separate and outside original/')
    if not args.check_only and (output.exists() or manifest_path.exists()):
        raise FileExistsError('Output or manifest exists; preserved')
    data = source.read_bytes()
    if sha(data) != SOURCE_SHA:
        raise ValueError('Expected the exact primary single 1.2.10 Exynos-patched native library')
    if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', data, 18)[0] != 183:
        raise ValueError('Expected ELF64 little-endian AArch64')
    if data[0x318:0x328].hex() != 'c3e506f9be350dfb4a00c79228754028':
        raise ValueError('BuildID mismatch')

    # No external entry into this exported function body was found by Ghidra;
    # its sole code caller targets the entry, which becomes RET before cave use.
    with tempfile.TemporaryDirectory(prefix='storm-wide-') as temp:
        temp = Path(temp)
        obj, elf, binary = temp / 'stubs.o', temp / 'stubs.elf', temp / 'stubs.bin'
        run(args.llvm_bin / 'clang.exe', '--target=aarch64-linux-android28', '-c', ROOT / 'patches/widescreen/stubs.S', '-o', obj)
        run(args.llvm_bin / 'ld.lld.exe', '-Ttext=' + hex(CAVE), '--entry=camera_hor_plus',
            '--defsym=resume_camera=0x941ff4', '--defsym=resume_ui=0xc96a30',
            '--defsym=nucc_sys_got=0x13b3e10', obj, '-o', elf)
        run(args.llvm_bin / 'llvm-objcopy.exe', '-O', 'binary', '--only-section=.text', elf, binary)
        payload = binary.read_bytes()
        disassembly = run(args.llvm_bin / 'llvm-objdump.exe', '-d', elf)
        symbols = {}
        for line in run(args.llvm_bin / 'llvm-nm.exe', '--defined-only', elf).splitlines():
            fields = line.split()
            if len(fields) == 3 and fields[2] in {'camera_hor_plus', 'ui_uniform', 'input_inverse'}:
                symbols[fields[2]] = int(fields[0], 16)
        if len(symbols) != 3 or CAVE + len(payload) > CAVE_END:
            raise ValueError('Invalid stub symbols or cave overflow')
        if 'fneg\ts6, s0' not in disassembly:
            raise ValueError('UI camera origin must use negative half of actual display width')

    patches = []
    result = bytearray(data)

    def put(va, expected, replacement, purpose):
        offset = va - 0x4000
        if expected is not None and data[offset:offset + len(expected)] != expected:
            raise ValueError(f'Unexpected bytes at ELF {va:#x}: {purpose}')
        for patch in patches:
            lo, hi = patch['offset'], patch['offset'] + len(bytes.fromhex(patch['after']))
            if offset < hi and lo < offset + len(replacement):
                raise ValueError('Overlapping patches')
        before = data[offset:offset + len(replacement)]
        result[offset:offset + len(replacement)] = replacement
        patches.append({'elfVa': hex(va), 'offset': offset, 'fileOffset': hex(offset),
                        'before': before.hex(), 'after': replacement.hex(), 'purpose': purpose})

    put(0xCDBCF4, bytes.fromhex('48004079'), bytes.fromhex('c0035fd6'), 'Preserve native display dimensions')
    put(0xCDBDA4, bytes.fromhex('01028052'), bytes.fromhex('e103142a'), 'Compose with actual display width')
    put(0xCDBDA8, bytes.fromhex('22018052'), bytes.fromhex('e203042a'), 'Compose with actual display height')
    # ChangeRender rebuilds composition independently of SetResolution.
    put(0x1079910, bytes.fromhex('01028052'), bytes.fromhex('e103142a'), 'Keep actual display width when render settings change')
    put(0x1079914, bytes.fromhex('22018052'), bytes.fromhex('e203042a'), 'Keep actual display height when render settings change')
    put(0x9B12BC, bytes.fromhex('ffc303d1'), bytes.fromhex('c0035fd6'), 'Disable decorative letterbox and protect cave')
    put(CAVE, None, payload, 'Position-linked ARM64 stubs inside inactive DrawLetterBox body')
    put(0x941FF0, bytes.fromhex('4bd8217e'), branch(0x941FF0, symbols['camera_hor_plus']), 'Preserve vertical field of view')
    put(0xC969F8, bytes.fromhex('0894a852'), struct.pack('<I', 0x52A88688), 'UI X scale denominator: 720')
    put(0xC96A0C, bytes.fromhex('0318221e'), struct.pack('<I', 0x1E221823), 'UI X scale: height / 720')
    put(0xC96A2C, bytes.fromhex('0640211e'), branch(0xC96A2C, symbols['ui_uniform']), 'Center uniformly scaled UI')
    put(0xA89F58, bytes.fromhex('c0035fd6'), branch(0xA89F58, symbols['input_inverse']), 'Map touches into uniformly scaled UI coordinates with the viewport origin')
    if len(result) != len(data) or result[0x6BF964:0x6BF968] != data[0x6BF964:0x6BF968]:
        raise AssertionError('ELF size or Exynos patch changed')
    assert branch(0x1000, 0x1004) == bytes.fromhex('01000014')
    assert branch(0x1004, 0x1000) == bytes.fromhex('ffffff17')
    # Match the -viewportHalfWidth origin used by ui_uniform.
    for width, height in [(1920, 1080), (2340, 1080)]:
        scale = height / 720
        k = width * 9 / (height * 16)
        old_origin = width / 2 - 640 * scale
        centered_origin = width / 2 - width / 2
        assert centered_origin == 0 and abs(old_origin - (0 if width == 1920 else 210)) < 1e-6
        for ui_x in (0, 640, 1280):
            display_x = centered_origin + ui_x * scale
            converted = display_x * 1280 / width
            restored = converted * k
            assert abs(restored - ui_x) < 1e-6
    parent_path = Path(str(source) + '.patch.json')
    parent_bytes = parent_path.read_bytes()
    parent_patch = json.loads(parent_bytes.decode('utf-8-sig'))
    if parent_patch['outputSha256'].lower() != sha(data) or parent_patch['sourceSha256'].lower() != 'c631e7127e73ecde32da7c8b8054ac6810a375875cd00749d3f4df5db29db79e':
        raise ValueError('Exynos parent manifest does not match the original APK and current input')
    manifest = {'status': 'diagnostic-only-not-game-validated', 'buildId': data[0x318:0x328].hex(),
                'source': parent_patch['source'], 'destination': str(output),
                'sourceSha256': parent_patch['sourceSha256'], 'appliedOnSha256': sha(data),
                'parentPatch': {'path': str(parent_path), 'sha256': sha(parent_bytes), 'metadata': parent_patch},
                'outputSha256': sha(result), 'caveVa': hex(CAVE), 'caveBytes': len(payload),
                'symbols': {key: hex(value) for key, value in symbols.items()}, 'patches': patches,
                'limit': 'Landscape >=16:9 candidate; boot/video/background cover and gameplay require device acceptance.'}
    if not args.check_only:
        if source.read_bytes() != data:
            raise RuntimeError('Source changed during patch preparation')
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(result)
        manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
        if sha(output.read_bytes()) != manifest['outputSha256']:
            raise RuntimeError('Written output hash mismatch')
    print(json.dumps({key: manifest[key] for key in ['status', 'sourceSha256', 'outputSha256', 'caveBytes', 'symbols']}, indent=2))
    print('Checks passed; no ELF written.' if args.check_only else str(output))


if __name__ == '__main__':
    main()
