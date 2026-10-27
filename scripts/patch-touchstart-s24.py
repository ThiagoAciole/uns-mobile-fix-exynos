"""Shrink the pt-BR 'TOQUE PARA INICIAR' quad on the S24 title screen.

Changes only the four vertex positions and the NUD bounds of xtitle_fd01_a, scaled
about the centre. The texture, UVs, coord transform, materials and animation are kept.
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from xfbin_messages import chunks, require

SOURCE_SHA = None  # set by main() from the expected xtitle.xfbin
MODEL = 'xtitle_fd01_a'
VERTEX_AT = (0x124, 0x140, 0x15C, 0x178)
VERTICES = ((-496.0, -56.0), (496.0, -56.0), (496.0, 56.0), (-496.0, 56.0))
BOUNDS = (-496.0, -56.0, 0.0, 496.0, 56.0, 0.0)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch(data, factor):
    require(0 < factor < 1, 'Factor must reduce the quad')
    model_at, model_size = next((o, s) for o, s, k, n in chunks(data) if (k, n) == ('nuccChunkModel', MODEL))
    require(model_size == 424, 'Unknown xtitle_fd01_a layout')
    start = model_at + 12
    model = bytearray(data[start:start + model_size])
    require(model[0x34:0x38] == b'NDP3', 'Missing NUD header')
    require(struct.unpack_from('>6f', model, 0x1C) == BOUNDS, 'Unknown bounds')
    for at, (x, y) in zip(VERTEX_AT, VERTICES):
        require(struct.unpack_from('>3f', model, at) == (x, y, 0.0), 'Unexpected vertex at 0x%x' % at)
        struct.pack_into('>3f', model, at, x * factor, y * factor, 0.0)
    struct.pack_into('>6f', model, 0x1C, *(v * factor for v in BOUNDS))
    result = bytearray(data)
    result[start:start + model_size] = model
    output = bytes(result)

    before, after = list(chunks(data)), list(chunks(output))
    require(len(before) == len(after), 'Chunk count changed')
    for old, new in zip(before, after):
        require(old[:2] == new[:2] and (old[2], old[3]) == (new[2], new[3]), 'Chunk layout changed')
        if (old[2], old[3]) != ('nuccChunkModel', MODEL):
            require(data[old[0]:old[0] + old[1] + 12] == output[new[0]:new[0] + new[1] + 12],
                    'Unselected chunk changed')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='xtitle.xfbin extracted from the installed APK')
    parser.add_argument('output', type=Path, help='fresh output path')
    parser.add_argument('--factor', type=float, default=0.6)
    args = parser.parse_args()
    manifest_path = Path(str(args.output) + '.patch.json')
    require(not args.output.exists() and not manifest_path.exists(), 'Fresh outputs required')
    data = args.source.read_bytes()
    result = patch(data, args.factor)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(result)
    with manifest_path.open('x', encoding='utf-8') as stream:
        json.dump(dict(sourceSha256=digest(data), outputSha256=digest(result), model=MODEL,
                       factor=args.factor), stream, indent=2)
        stream.write('\n')
    print(json.dumps({'outputSha256': digest(result), 'bytes': len(result), 'factor': args.factor}, indent=2))


if __name__ == '__main__':
    main()
