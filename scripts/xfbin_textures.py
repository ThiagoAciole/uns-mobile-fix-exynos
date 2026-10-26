"""Decode/reimport single-mip NTP3 textures without changing game geometry or UVs.

NTP3 layout: https://github.com/mosamadeeb/xfbin_lib/blob/main/xfbin/structure/br/br_nut.py
Pixel formats/channel rotation: Smash-Forge/Filetypes/Textures/NUT.cs.
Only format conversion is performed here; no image retouching or resizing.
"""
import argparse
import hashlib
import json
import struct
import zlib
from pathlib import Path

from xfbin_messages import chunks, require


def textures(data):
    for offset, size, kind, name in chunks(data):
        if kind != "nuccChunkTexture":
            continue
        start = offset + 12
        payload = data[start:start + size]
        require(len(payload) >= 108 and payload[12:16] == b"NTP3", "Expected wrapped NTP3")
        version, count = struct.unpack_from(">HH", payload, 16)
        require(version == 0x100 and count == 1, "Only single-texture NTP3 v1 supported")
        total, unused, length, header = struct.unpack_from(">IIIH", payload, 28)
        mipmaps, pixel_format = payload[45], payload[47]
        width, height = struct.unpack_from(">HH", payload, 48)
        require(mipmaps == 1 and header == 0x50 and not struct.unpack_from(">I", payload, 56)[0] & 0x200,
                "Only single-mip non-cubemap textures supported")
        require(0 < width <= 8192 and 0 < height <= 8192, "Invalid texture dimensions")
        require(pixel_format in (0, 2, 14), "Only BC1, BC3 and ARGB8 supported")
        expected = width * height * 4 if pixel_format == 14 else ((width+3)//4)*((height+3)//4)*(8 if pixel_format == 0 else 16)
        require(length == expected and total == length + header and len(payload) == 28 + total,
                "NTP3 size mismatch")
        require(struct.unpack_from(">I", payload, 8)[0] == len(payload) - 12, "Texture wrapper size mismatch")
        yield dict(name=name, offset=offset, size=size, width=width, height=height,
                   format=pixel_format, mipmaps=mipmaps, pixels_at=start + 108,
                   pixels_size=length, sha256=hashlib.sha256(payload).hexdigest())


def color565(value):
    r, g, b = (value >> 11) & 31, (value >> 5) & 63, value & 31
    return ((r << 3) | (r >> 2), (g << 2) | (g >> 4), (b << 3) | (b >> 2), 255)


def decode(data, texture):
    w, h, fmt = texture["width"], texture["height"], texture["format"]
    pixels = data[texture["pixels_at"]:texture["pixels_at"] + texture["pixels_size"]]
    if fmt == 14:
        rgba = bytearray(len(pixels))
        rgba[0::4], rgba[1::4], rgba[2::4], rgba[3::4] = pixels[1::4], pixels[2::4], pixels[3::4], pixels[0::4]
        return bytes(rgba)
    output = bytearray(w * h * 4)
    stride, at = (8 if fmt == 0 else 16), 0
    for by in range(0, h, 4):
        for bx in range(0, w, 4):
            block = pixels[at:at + stride]
            at += stride
            colors_at = 0 if fmt == 0 else 8
            c0, c1, indices = struct.unpack_from("<HHI", block, colors_at)
            palette = [color565(c0), color565(c1)]
            if c0 > c1 or fmt == 2:
                palette.append(tuple((2*palette[0][i] + palette[1][i])//3 for i in range(3))+(255,))
                palette.append(tuple((palette[0][i] + 2*palette[1][i])//3 for i in range(3))+(255,))
            else:
                palette.extend([tuple((palette[0][i]+palette[1][i])//2 for i in range(3))+(255,), (0,0,0,0)])
            if fmt == 2:
                a0, a1 = block[:2]
                alpha = [a0, a1]
                if a0 > a1:
                    alpha += [((7-i)*a0+i*a1)//7 for i in range(1,7)]
                else:
                    alpha += [((5-i)*a0+i*a1)//5 for i in range(1,5)] + [0,255]
                alpha_indices = int.from_bytes(block[2:8], "little")
            for i in range(16):
                x, y = bx+i%4, by+i//4
                if x < w and y < h:
                    color = list(palette[(indices >> (2*i)) & 3])
                    if fmt == 2:
                        color[3] = alpha[(alpha_indices >> (3*i)) & 7]
                    dest = (y*w+x)*4
                    output[dest:dest+4] = bytes(color)
    return bytes(output)


def png_write(width, height, rgba):
    require(len(rgba) == width*height*4, "RGBA length differs from dimensions")
    def packet(kind, content):
        return struct.pack(">I",len(content))+kind+content+struct.pack(">I",zlib.crc32(kind+content)&0xffffffff)
    rows = b"".join(b"\0"+rgba[y*width*4:(y+1)*width*4] for y in range(height))
    return b"\x89PNG\r\n\x1a\n"+packet(b"IHDR",struct.pack(">IIBBBBB",width,height,8,6,0,0,0))+packet(b"IDAT",zlib.compress(rows))+packet(b"IEND",b"")


def png_read(data):
    require(len(data) <= 64 * 1024 * 1024, "PNG input exceeds 64 MiB limit")
    require(data[:8] == b"\x89PNG\r\n\x1a\n", "Not PNG")
    position, compressed, dimensions, ended = 8, bytearray(), None, False
    while position < len(data):
        require(position+12 <= len(data), "Truncated PNG")
        size = struct.unpack_from(">I", data, position)[0]
        kind = data[position+4:position+8]
        end = position+8+size
        require(end+4 <= len(data), "PNG chunk outside file")
        value = data[position+8:end]
        require(zlib.crc32(kind+value)&0xffffffff == struct.unpack_from(">I",data,end)[0], "PNG CRC mismatch")
        if kind == b"IHDR":
            require(dimensions is None and position == 8, "PNG must begin with exactly one IHDR")
            width,height,depth,color,compression,filtering,interlace = struct.unpack(">IIBBBBB",value)
            require(0<width<=8192 and 0<height<=8192 and width*height <= 16*1024*1024 and depth == 8 and color in (2,6) and
                    (compression,filtering,interlace)==(0,0,0), "Expected non-interlaced 8-bit RGB/RGBA PNG")
            dimensions = width,height,color
        elif kind == b"IDAT":
            compressed.extend(value)
        elif kind == b"IEND":
            require(size == 0 and end+4 == len(data), "Invalid PNG end or trailing data")
            ended = True
            break
        position = end+4
    require(dimensions is not None and ended, "Missing PNG dimensions or end")
    width,height,color = dimensions
    bpp = 4 if color == 6 else 3
    stride = width*bpp
    inflater=zlib.decompressobj()
    raw=inflater.decompress(bytes(compressed),(stride+1)*height+1)
    require(inflater.eof and not inflater.unused_data and not inflater.unconsumed_tail, "PNG decompression exceeds bounds or is truncated")
    require(len(raw)==(stride+1)*height, "PNG decoded size mismatch")
    output, previous = bytearray(), bytearray(stride)
    for y in range(height):
        at = y*(stride+1)
        filtering, row = raw[at], bytearray(raw[at+1:at+1+stride])
        require(filtering in range(5), "Unknown PNG filter")
        for i in range(stride):
            a = row[i-bpp] if i>=bpp else 0
            b = previous[i]
            c = previous[i-bpp] if i>=bpp else 0
            if filtering == 1: predictor = a
            elif filtering == 2: predictor = b
            elif filtering == 3: predictor = (a+b)//2
            elif filtering == 4:
                p=a+b-c;pa,pb,pc=abs(p-a),abs(p-b),abs(p-c)
                predictor=a if pa<=pb and pa<=pc else b if pb<=pc else c
            else: predictor = 0
            row[i]=(row[i]+predictor)&255
        output.extend(row)
        previous=row
    if bpp == 3:
        rgba=bytearray(width*height*4)
        rgba[0::4],rgba[1::4],rgba[2::4],rgba[3::4]=output[0::3],output[1::3],output[2::3],bytes([255])*(width*height)
        output=rgba
    return width,height,bytes(output)


def replace(data, replacements):
    entries=list(textures(data))
    metadata = {row["name"]:row for row in entries}
    require(len(metadata)==len(entries), "Duplicate texture names unsupported")
    require(replacements.keys() <= metadata.keys(), "Unknown texture name")
    result, cursor, report = bytearray(), 0, []
    for row in metadata.values():
        name = row["name"]
        if name not in replacements:
            continue
        width,height,rgba = png_read(replacements[name])
        require((width,height)==(row["width"],row["height"]), "Texture dimensions must remain identical")
        if decode(data,row)==rgba:
            continue
        argb=bytearray(len(rgba))
        argb[0::4],argb[1::4],argb[2::4],argb[3::4]=rgba[3::4],rgba[0::4],rgba[1::4],rgba[2::4]
        start = row["offset"]
        payload = bytearray(data[start+12:start+120])
        payload[47] = 14
        struct.pack_into(">I",payload,8,len(argb)+96)
        struct.pack_into(">I",payload,28,len(argb)+80)
        struct.pack_into(">I",payload,36,len(argb))
        payload.extend(argb)
        result.extend(data[cursor:start])
        result.extend(struct.pack(">I",len(payload))+data[start+4:start+12]+payload)
        cursor = start+12+row["size"]
        report.append(dict(name=name,fromFormat=row["format"],toFormat=14,width=width,height=height))
    result.extend(data[cursor:])
    output=bytes(result)
    new={row['name']:row for row in textures(output)}
    for name,png in replacements.items():
        require(decode(output,new[name])==png_read(png)[2], "Reimported pixels differ")
    before=list(chunks(data));after=list(chunks(output))
    require(len(before)==len(after), "Chunk count changed")
    for old,current in zip(before,after):
        op,os,ok,on=old;np,ns,nk,nn=current
        require((ok,on)==(nk,nn), "Chunk identities changed")
        if ok!='nuccChunkTexture' or on not in replacements:
            require(data[op:op+os+12]==output[np:np+ns+12], "Unselected chunk changed")
    return output,report


def self_test(data):
    rows=list(textures(data))
    originals={row['name']:png_write(row['width'],row['height'],decode(data,row)) for row in rows}
    result,report=replace(data,originals)
    require(result==data and not report,'No-edit round trip was not byte-identical')
    for fmt in (14,2,0):
        selected=next((row for row in rows if row['format']==fmt),None)
        if selected is None:
            continue
        rgba=bytearray(decode(data,selected))
        rgba[0]^=1
        png=png_write(selected['width'],selected['height'],rgba)
        output,changed=replace(data,{selected['name']:png})
        require(len(changed)==1 and changed[0]['toFormat']==14,'Changed texture not reported')
        actual=next(row for row in textures(output) if row['name']==selected['name'])
        require(decode(output,actual)==rgba,'Changed pixels did not survive reimport')
    try:
        png_read(next(iter(originals.values()))[:-1])
    except ValueError:
        pass
    else:
        raise AssertionError('Truncated PNG accepted')
    corrupt=bytearray(next(iter(originals.values())))
    corrupt[29]^=1
    try:
        png_read(corrupt)
    except ValueError:
        pass
    else:
        raise AssertionError('Corrupt PNG CRC accepted')
    bad_png=png_write(1,1,b'\xff\x00\x00\xff')
    try:
        replace(data,{rows[0]['name']:bad_png})
    except ValueError:
        pass
    else:
        raise AssertionError('Changed dimensions accepted')
    print(f'Self-test passed: {len(rows)} no-edit texture round trips, edit/reparse, untouched chunks, CRC/truncation and dimension guards')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    sub=parser.add_subparsers(dest='command',required=True)
    extract=sub.add_parser('extract');extract.add_argument('source',type=Path);extract.add_argument('output',type=Path)
    rebuild=sub.add_parser('rebuild');rebuild.add_argument('source',type=Path);rebuild.add_argument('plan',type=Path);rebuild.add_argument('output',type=Path)
    check=sub.add_parser('self-test');check.add_argument('source',type=Path)
    args=parser.parse_args();data=args.source.read_bytes()
    if args.command=='self-test':
        self_test(data)
        return
    require(not args.output.exists(),'Fresh output required')
    if args.command=='extract':
        args.output.mkdir(parents=True)
        rows=list(textures(data))
        for row in rows:
            require('/' not in row['name'] and '\\' not in row['name'] and row['name'] not in ('.','..'),'Unsafe texture name')
            png=png_write(row['width'],row['height'],decode(data,row))
            require(png_read(png)==(row['width'],row['height'],decode(data,row)),'PNG round trip failed')
            (args.output/(row['name']+'.png')).write_bytes(png)
        (args.output/'manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
        print(f'Exported {len(rows)} textures')
    else:
        paths=json.loads(args.plan.read_text(encoding='utf-8-sig'))
        output,report=replace(data,{name:Path(path).read_bytes() for name,path in paths.items()})
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_bytes(output)
        args.output.with_suffix(args.output.suffix+'.textures.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
        print(f'Reimported {len(report)} changed textures')


if __name__=='__main__':
    main()
