"""Fix ChangeRender composition on the exact last24 widescreen library."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = '04b046b7cd13a7be949cc1914bf14e53490804e11b58d964fc09607335cd604e'


def patch(data):
    source_hash = hashlib.sha256(data).hexdigest()
    if source_hash != SOURCE_SHA:
        raise ValueError('Expected exact last24 library; unknown or already patched input')
    start = 0x1079910 - 0x4000
    before, after = bytes.fromhex('0102805222018052'), bytes.fromhex('e103142ae203042a')
    if data[start:start + 8] != before:
        raise ValueError('Unexpected ChangeRender ratio instructions')
    result = data[:start] + after + data[start + 8:]
    assert len(result) == len(data)
    return result, dict(
        sourceSha256=source_hash,
        outputSha256=hashlib.sha256(result).hexdigest(),
        status='composition-emulated-not-device-tested',
        scope='ChangeRender uses device width/height; last24 UI, input and assets retained',
        patches=[dict(elfVa='0x1079910', offset=start, before=before.hex(), after=after.hex(),
                      purpose='Keep composition widescreen when render settings change')],
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    manifest = Path(str(output) + '.patch.json')
    if output == args.source.resolve() or output.exists() or manifest.exists():
        raise ValueError('Fresh separate output and manifest required')
    if any(output.is_relative_to(ROOT / folder) for folder in ('original', 'origin')):
        raise ValueError('Output cannot be inside original/ or origin/')
    data = args.source.read_bytes()
    result, info = patch(data)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('xb') as stream:
        stream.write(result)
    with manifest.open('x', encoding='utf-8') as stream:
        json.dump(info, stream, indent=2)
        stream.write('\n')
    if output.read_bytes() != result or args.source.read_bytes() != data:
        raise RuntimeError('Written bytes or source changed')
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
