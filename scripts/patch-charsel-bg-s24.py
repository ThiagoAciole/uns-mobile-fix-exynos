"""Widen the S24 character-select gold background (msel1_bg00) to 2340px.

Changes only: the 20 X positions of the bg00 grid (+-640 -> +-734, +-320 -> +-367),
the NUD bounds/radius of that model, and the top 1080 rows of the msel1_bg00 atlas,
which are replaced by the supplied 2340x1080 art downscaled to 1536px. The atlas is
stored as ARGB8 (format 14) because the project encoder does not write BC3.
"""
import argparse
import hashlib
import json
import math
import struct
from pathlib import Path

from xfbin_messages import chunks, require
from xfbin_textures import decode, png_read, textures

SOURCE_SHA = '6daade83d3288ae50c0aed6ba27a6d10c4226f6bfc1a82909fa5a4f37b09f9a1'
MODEL = 'bg00'
TEXTURE = 'msel1_bg00'
SCALE = 752.0 / 640.0
# Verified X positions of the bg00 grid (z=0, |y|<=720); other X values are 0 and stay 0.
VERTEX_AT = (0x174, 0x190, 0x1ac, 0x1c8, 0x21c, 0x238, 0x254, 0x270, 0x28c, 0x2a8,
             0x2e0, 0x2fc, 0x318, 0x334, 0x36c, 0x388, 0x3a4, 0x3c0, 0x3f8, 0x414)
ATLAS_W, BG_ROWS = 1536, 1080


def digest(data):
    return hashlib.sha256(data).hexdigest()


def downscale_rows(rgba, src_w, rows, dst_w):
    """Box-average each row horizontally from src_w to dst_w pixels."""
    out = bytearray(dst_w * rows * 4)
    ratio = src_w / dst_w
    for y in range(rows):
        row = rgba[y * src_w * 4:(y + 1) * src_w * 4]
        for x in range(dst_w):
            a = int(x * ratio)
            b = max(a + 1, int((x + 1) * ratio))
            n = b - a
            sums = [0, 0, 0, 0]
            for sx in range(a, b):
                p = sx * 4
                sums[0] += row[p]
                sums[1] += row[p + 1]
                sums[2] += row[p + 2]
                sums[3] += row[p + 3]
            o = (y * dst_w + x) * 4
            out[o:o + 4] = bytes(s // n for s in sums)
    return bytes(out)


def patch(data, art_png):
    require(digest(data) == SOURCE_SHA, 'Unknown msel1_bg.xfbin or patch already applied')
    width, height, art = png_read(art_png)
    require((width, height) == (2340, 1080), 'Expected 2340x1080 PNG')
    require(all(art[i] == 255 for i in range(3, len(art), 4)), 'Art must be fully opaque')

    model_at, model_size = next((o, s) for o, s, k, n in chunks(data) if (k, n) == ('nuccChunkModel', MODEL))
    require(model_size == 1087, 'Unknown bg00 model layout')
    result = bytearray(data)
    start = model_at + 12
    model = bytearray(data[start:start + model_size])
    for at in VERTEX_AT:
        x, y, z = struct.unpack_from('>3f', model, at)
        require(abs(x) in (320.0, 640.0) and z == 0.0 and abs(y) <= 720.0, 'Unexpected vertex at 0x%x' % at)
        struct.pack_into('>f', model, at, math.copysign(abs(x) * SCALE, x))
    require(struct.unpack_from('>6f', model, 0x1C) == (-640.0, -360.0, 0.0, 640.0, 360.0, 0.0),
            'Unknown bg00 bounds')
    struct.pack_into('>6f', model, 0x1C, -752.0, -360.0, 0.0, 752.0, 360.0, 0.0)
    radius = math.hypot(752.0, 360.0)
    for at in (0x60, 0x70):
        require(abs(struct.unpack_from('>f', model, at)[0] - 734.3023681640625) < 1e-3, 'Unknown radius')
        struct.pack_into('>f', model, at, radius)
    result[start:start + model_size] = model

    row = next(t for t in textures(data) if t['name'] == TEXTURE)
    require((row['width'], row['height'], row['format']) == (1536, 1536, 2), 'Unknown atlas texture')
    rgba = decode(data, row)
    top = downscale_rows(art, width, BG_ROWS, ATLAS_W)
    rgba = top + rgba[BG_ROWS * ATLAS_W * 4:]

    argb = bytearray(len(rgba))
    argb[0::4], argb[1::4], argb[2::4], argb[3::4] = rgba[3::4], rgba[0::4], rgba[1::4], rgba[2::4]
    offset = row['offset']
    payload = bytearray(data[offset + 12:offset + 120])
    payload[47] = 14
    struct.pack_into('>I', payload, 8, len(argb) + 96)
    struct.pack_into('>I', payload, 28, len(argb) + 80)
    struct.pack_into('>I', payload, 36, len(argb))
    payload.extend(argb)
    result[offset:offset + row['size'] + 12] = struct.pack('>I', len(payload)) + data[offset + 4:offset + 12] + payload

    output = bytes(result)
    before, after = list(chunks(data)), list(chunks(output))
    require(len(before) == len(after), 'Chunk count changed')
    for old, new in zip(before, after):
        require((old[2], old[3]) == (new[2], new[3]), 'Chunk identities changed')
        if (old[2], old[3]) not in (('nuccChunkTexture', TEXTURE), ('nuccChunkModel', MODEL)):
            require(data[old[0]:old[0] + old[1] + 12] == output[new[0]:new[0] + new[1] + 12],
                    'Unselected chunk changed')
    actual = next(t for t in textures(output) if t['name'] == TEXTURE)
    require((actual['width'], actual['height'], actual['format']) == (1536, 1536, 14), 'Atlas readback differs')
    pixels = decode(output, actual)
    require(pixels[:BG_ROWS * ATLAS_W * 4] == top, 'Background pixels differ')
    require(pixels[BG_ROWS * ATLAS_W * 4:] == rgba[BG_ROWS * ATLAS_W * 4:], 'Lower atlas pixels differ')
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path, help='msel1_bg.xfbin extracted from the installed APK')
    parser.add_argument('art', type=Path, help='2340x1080 opaque PNG')
    parser.add_argument('output', type=Path, help='fresh output path')
    args = parser.parse_args()
    manifest_path = Path(str(args.output) + '.patch.json')
    require(not args.output.exists() and not manifest_path.exists(), 'Fresh outputs required')
    data = args.source.read_bytes()
    result = patch(data, args.art.read_bytes())
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(result)
    with manifest_path.open('x', encoding='utf-8') as stream:
        json.dump(dict(sourceSha256=digest(data), outputSha256=digest(result), model=MODEL,
                       texture=TEXTURE, scale=SCALE, vertices=len(VERTEX_AT)), stream, indent=2)
        stream.write('\n')
    print(json.dumps({'outputSha256': digest(result), 'bytes': len(result)}, indent=2))


if __name__ == '__main__':
    main()
