"""Enable edge-to-edge responsive widescreen HUDs/menus while preserving 3D Hor+ FOV."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = '5e2797280a0d9eae2cf2d14f0089d6a9585699673a7c872e0d21d61be6f78071'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch(data):
    if digest(data) != SOURCE_SHA:
        raise ValueError('Expected exact current 1.2.10 pt-BR/Exynos/widescreen library; unknown or already patched')
    if data[0x318:0x328].hex() != 'c3e506f9be350dfb4a00c79228754028':
        raise ValueError('Build ID mismatch')
    if data[0x9b12bc - 0x4000:0x9b12c0 - 0x4000] != bytes.fromhex('c0035fd6'):
        raise ValueError('DrawLetterBox RET guard missing')
    if data[0x941ff0 - 0x4000:0x941ff4 - 0x4000] != bytes.fromhex('b4bc0114'):
        raise ValueError('3D Hor+ camera branch missing')

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

    put(0xc969f8, bytes.fromhex('8886a852'), bytes.fromhex('0894a852'),
        'Restore 1280.0f X denominator in ccGameDrawEnv::SetupDispCamera')
    put(0xc96a0c, bytes.fromhex('2318221e'), bytes.fromhex('0318221e'),
        'Scale 2D DispCamera X by displayWidth / 1280.0f for full-width responsive HUDs')
    put(0xc96a2c, bytes.fromhex('2c6af417'), bytes.fromhex('0640211e'),
        'Set 2D DispCamera X origin to -0.5f * displayWidth (edge-to-edge)')
    put(0xa89f58, bytes.fromhex('e69cfc17'), bytes.fromhex('c0035fd6'),
        'Restore full-width touch X mapping in nuccResolution::ConvertScreenPosToRenderPos')

    result = bytes(output)
    assert len(result) == len(data)
    assert result[0x6bf964:0x6bf968] == data[0x6bf964:0x6bf968]
    return result, dict(
        sourceSha256=digest(data),
        outputSha256=digest(result),
        status='static-verified-edge-to-edge-responsive-widescreen',
        target='Responsive >=16:9 landscape (3D Hor+, 2D edge-to-edge)',
        preserved3dHorPlus=dict(elfVa='0x941ff0', bytes='b4bc0114', target='0x9b12c0'),
        patches=edits,
    )


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
    print(json.dumps({k: info[k] for k in ('status', 'sourceSha256', 'outputSha256')}, indent=2))


if __name__ == '__main__':
    main()

