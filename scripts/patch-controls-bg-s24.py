"""Import a 2340/2342x1080 background with an opaque S24 sampling area."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
from xfbin_messages import chunks, require
from xfbin_textures import decode, png_read, png_write, textures

SOURCE_SHA = 'a1c0461e95a70e57e7f3994e81e0c8827cfdd01c0a9cd1a6ed3b71f69400f6cf'
NAME = 'xoption_battlebg01'
VERTICES = ((-140, 0), (1420, 0), (-140, 720), (1420, 720))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch(data, png):
    require(digest(data) == SOURCE_SHA, 'Unknown moption asset or patch already applied')
    width, height, rgba = png_read(png)
    require(width in (2340, 2342) and height == 1080, 'Expected 2340/2342x1080 RGB/RGBA PNG')
    uv_left = (width - 2340) // 2
    require(all(a == 255 for y in range(height)
                for a in rgba[(y*width+uv_left)*4+3:(y*width+uv_left+2340)*4:4]),
            'Sampled background must be fully opaque')
    before = list(chunks(data))
    selected = [(o, s) for o, s, k, n in before if k == 'nuccChunkSprite' and n == NAME]
    require(len(selected) == 1, 'Expected exactly one background sprite')
    sprite_at, sprite_size = selected[0]
    require(sprite_size == 62, 'Unknown sprite layout')
    start = sprite_at + 12
    sprite = data[start:start + sprite_size]
    require(digest(sprite) == 'b13839f831c7f6dfda7db0a4235456832de9746bc634ca4d4b99e3bc3d7abedf',
            'Unknown background sprite bytes')
    require(struct.unpack_from('>8h', sprite, 0x2a) == (0, 0, 1280, 0, 0, 720, 1280, 720),
            'Unknown source geometry')
    result = bytearray(data)
    # shortcut: S24 samples 2340 pixels; a 2342px source keeps one unused pixel per side.
    struct.pack_into('>H', result, start + 0x12, 2340)
    struct.pack_into('>H', result, start + 0x26, uv_left)
    struct.pack_into('>8h', result, start + 0x2a, *(v for point in VERTICES for v in point))
    row = next(t for t in textures(data) if t['name'] == NAME)
    require((row['width'], row['height'], row['format']) == (1920, 1080, 2), 'Unknown texture')
    offset = row['offset']
    payload = bytearray(data[offset + 12:offset + 120])
    argb = bytearray(len(rgba))
    argb[0::4], argb[1::4], argb[2::4], argb[3::4] = rgba[3::4], rgba[0::4], rgba[1::4], rgba[2::4]
    struct.pack_into('>HH', payload, 2, width, height)
    struct.pack_into('>HH', payload, 48, width, height)
    payload[47] = 14
    struct.pack_into('>I', payload, 8, len(argb) + 96)
    struct.pack_into('>I', payload, 28, len(argb) + 80)
    struct.pack_into('>I', payload, 36, len(argb))
    payload.extend(argb)
    result[offset:offset + row['size'] + 12] = struct.pack('>I', len(payload)) + data[offset + 4:offset + 12] + payload
    output = bytes(result)
    after = list(chunks(output))
    require(len(before) == len(after), 'Chunk count changed')
    for old, new in zip(before, after):
        o, s, k, n = old
        p, z, q, m = new
        require((k, n) == (q, m), 'Chunk identities changed')
        if (k, n) not in (('nuccChunkTexture', NAME), ('nuccChunkSprite', NAME)):
            require(data[o:o+s+12] == output[p:p+z+12], 'Unselected chunk changed')
    actual = next(t for t in textures(output) if t['name'] == NAME)
    require(decode(output, actual) == rgba, 'Imported pixels differ')
    new_sprite = next(o + 12 for o, s, k, n in after if k == 'nuccChunkSprite' and n == NAME)
    require(struct.unpack_from('>8h', output, new_sprite + 0x2a) == tuple(v for p in VERTICES for v in p),
            'Geometry readback differs')
    require(struct.unpack_from('>HH', output, new_sprite + 0x12) == (2340, 1080), 'UV extent differs')
    require(struct.unpack_from('>HH', output, new_sprite + 0x26) == (uv_left, 0), 'UV origin differs')
    return output


def self_test(source):
    for width in (2340, 2342):
        # Distinct edge columns prove that the full texture survives, including unused pixels.
        alpha = 25 if width == 2342 else 255
        row = bytes((255, 0, 0, alpha)) + b'\x12\x34\x56\xff' * (width-2) + bytes((0, 255, 0, alpha))
        png = png_write(width, 1080, row * 1080)
        output = patch(source, png)
    for bad_source, bad_png in ((output, png), (source[:-1], png),
                                (source, png[:-1]), (source, png_write(1, 1, b'\0\0\0\xff')),
                                (source, png_write(2340, 1080, b'\0\0\0\x19' * (2340*1080)))):
        try:
            patch(bad_source, bad_png)
        except ValueError:
            pass
        else:
            raise AssertionError('Invalid input accepted')
    # The added 210 sampled pixels on each side map to 140 logical UI units.
    assert 210 / 1.5 == 140 and 2340 / 1560 == 1080 / 720 == 1.5
    print('PASS: 2340/2342 exact pixels including borders, UV extent/origin, untouched chunks, geometry and input guards')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('--png', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    source = args.source.read_bytes()
    if args.self_test:
        self_test(source)
        return
    require(args.png is not None and args.output is not None, '--png and --output required')
    manifest = Path(str(args.output) + '.patch.json')
    require(not args.output.exists() and not manifest.exists(), 'Fresh outputs required')
    png = args.png.read_bytes()
    width, height, _ = png_read(png)
    result = patch(source, png)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open('xb') as stream:
        stream.write(result)
    require(args.output.read_bytes() == result, 'Output readback differs')
    manifest.write_text(json.dumps(dict(sourceSha256=digest(source), outputSha256=digest(result),
                        pngSha256=digest(png), vertices=VERTICES, textureFormat='ARGB8',
                        textureDimensions=[width, height], uvOrigin=[(width-2340)//2, 0],
                        uvExtent=[2340, 1080],
                        status='candidate-not-device-tested'), indent=2) + '\n', encoding='utf-8')
    print(str(args.output))


if __name__ == '__main__':
    main()
