"""Extend S24 fullscreen coverage and the RPG start-menu layer on the current APK."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = '5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071'
CAVE, CAVE_END = 0x9b134c, 0x9b145c
LLVM = Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/windows-x86_64/bin'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def branch(source, target):
    delta = target - source
    if delta % 4 or not -(1 << 27) <= delta < (1 << 27):
        raise ValueError('Unaligned or out-of-range branch')
    return struct.pack('<I', 0x14000000 | ((delta // 4) & 0x3ffffff))


def patch(data, llvm=LLVM):
    if digest(data) != SOURCE_SHA:
        raise ValueError('Expected exact current 1.2.10 pt-BR/Exynos/widescreen library; unknown or already patched')
    if data[0x318:0x328].hex() != 'c3e506f9be350dfb4a00c79228754028':
        raise ValueError('Build ID mismatch')
    if data[0x9b12bc-0x4000:0x9b12c0-0x4000] != bytes.fromhex('c0035fd6'):
        raise ValueError('Cave is not protected by DrawLetterBox RET')

    def run(name, *args):
        return subprocess.check_output([str(llvm / name), *map(str, args)], text=True)

    with tempfile.TemporaryDirectory(prefix='storm-s24-') as tmp:
        tmp = Path(tmp)
        obj, elf, raw = tmp / 'stubs.o', tmp / 'stubs.elf', tmp / 'stubs.bin'
        run('clang.exe', '--target=aarch64-linux-android28', '-c', ROOT / 'patches/widescreen/coverage-s24.S', '-o', obj)
        run('ld.lld.exe', '-Ttext=' + hex(CAVE), '--entry=filter_coverage',
            '--defsym=nucc_sys_got=0x13b3e10', '--defsym=resume_filter=0xa58868',
            '--defsym=resume_fade_done=0xbda400', '--defsym=original_ui_width=0x12c7a20',
            '--defsym=resume_fade_original=0xbda3e8', '--defsym=resume_startmenu=0xa7d744',
            obj, '-o', elf)
        run('llvm-objcopy.exe', '-O', 'binary', '--only-section=.text', elf, raw)
        payload = raw.read_bytes()
        symbols = {}
        for line in run('llvm-nm.exe', '--defined-only', elf).splitlines():
            row = line.split()
            if len(row) == 3 and row[2] in ('filter_coverage', 'fade_coverage', 'startmenu_layer'):
                symbols[row[2]] = int(row[0], 16)
        disassembly = run('llvm-objdump.exe', '-d', elf)
    if len(symbols) != 3 or CAVE + len(payload) > CAVE_END:
        raise ValueError('Invalid stubs or cave overflow')

    output, edits = bytearray(data), []

    def put(va, expected, replacement, purpose):
        offset = va - 0x4000
        if data[offset:offset + len(expected)] != expected:
            raise ValueError('Unexpected bytes: ' + purpose)
        if len(expected) != len(replacement):
            raise ValueError('Patch must preserve size')
        for edit in edits:
            lo, hi = edit['offset'], edit['offset'] + len(bytes.fromhex(edit['after']))
            if offset < hi and lo < offset + len(replacement):
                raise ValueError('Overlapping patches')
        output[offset:offset + len(replacement)] = replacement
        edits.append(dict(elfVa=hex(va), offset=offset, before=expected.hex(), after=replacement.hex(), purpose=purpose))

    put(CAVE, data[CAVE-0x4000:CAVE-0x4000+len(payload)], payload, 'S24 coverage stubs after the existing 140-byte cave payload')
    put(0xa58864, bytes.fromhex('0148803d'), branch(0xa58864, symbols['filter_coverage']), 'Expand only full-screen filter X coordinates')
    put(0xbda3e4, bytes.fromhex('8fb51b94'), branch(0xbda3e4, symbols['fade_coverage']), 'Replace default 1280x720 fade size only at 2340x1080')
    ui_branch = data[0xc96a2c-0x4000:0xc96a30-0x4000]
    if ui_branch != bytes.fromhex('2c6af417'):
        raise ValueError('Existing 16:9-uniform UI/touch branch is missing or changed')
    if data[0xa7d73c-0x4000:0xa7d740-0x4000] != bytes.fromhex('01e4002f'):
        raise ValueError('RPG start-menu fullscreen layer callsite changed')
    if data[0xa7d740-0x4000:0xa7d744-0x4000] != bytes.fromhex('0241201e'):
        raise ValueError('RPG start-menu layer arguments changed')
    put(0xa7d73c, bytes.fromhex('01e4002f'), branch(0xa7d73c, symbols['startmenu_layer']),
        'Expand only the S24 RPG start-menu layer from 1280 to logical 1560 and shift X to -140')
    result = bytes(output)
    assert len(result) == len(data)
    assert result[0x9b12bc-0x4000:CAVE-0x4000] == data[0x9b12bc-0x4000:CAVE-0x4000]
    assert result[0x6bf964:0x6bf968] == data[0x6bf964:0x6bf968]
    return result, dict(sourceSha256=digest(data), outputSha256=digest(result),
                        status='static-verified-not-device-tested', target='S24 2340x1080 landscape',
                        caveBytes=len(payload), symbols={k: hex(v) for k, v in symbols.items()},
                        preservedUiBranch=dict(elfVa='0xc96a2c', bytes=ui_branch.hex(), target='0x9b12dc'),
                        patches=edits, disassembly=disassembly,
                        fallback='Original filter coordinates and fade getter path outside 2340x1080')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    manifest_path = Path(str(args.output) + '.patch.json')
    if args.source.resolve() == args.output.resolve() or args.output.exists() or manifest_path.exists():
        raise ValueError('Fresh separate outputs required')
    data = args.source.read_bytes()
    result, info = patch(data)
    if not args.check_only:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open('xb') as stream:
            stream.write(result)
        with manifest_path.open('x', encoding='utf-8') as stream:
            json.dump(info, stream, indent=2)
            stream.write('\n')
        if args.output.read_bytes() != result or args.source.read_bytes() != data:
            raise RuntimeError('Written bytes or source changed')
    print(json.dumps({k: info[k] for k in ('status', 'sourceSha256', 'outputSha256', 'caveBytes', 'symbols')}, indent=2))


if __name__ == '__main__':
    main()
