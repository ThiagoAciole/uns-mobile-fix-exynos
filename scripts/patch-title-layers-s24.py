"""Extend verified title overlay meshes to S24 width; keep logo, UVs and animation.

Input is the existing 1.2.10 title asset with only the gold quad widened.
NUCC/NUD layout reference: https://github.com/mosamadeeb/xfbin_lib
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from xfbin_messages import chunks, require

SOURCE_SHA = "e1bf958a9e4eef7668dbe4fb61b694294c83963845d064fe54f133dfda446220"
# name: (payload size, payload SHA-256, first vertex, count, bounding half-height)
TARGETS = {
    "xtitle_parts00_b": (427, "3b62ddb4eeef96c5c95765334d9273935fe63885a6257fda3325b1f94966268b", 0x124, 4, 360),
    "xtitle_parts00_w": (427, "743bba9f8bc5b4fca6633eceff1df8ec83b7b6909593d4396624b58a7a49c7aa", 0x124, 4, 360),
    "xtitle_parts00_flt_a": (431, "999b19ac881be36367d8266134af50b6810e54d7404186630d4d40044602e01c", 0x124, 4, 56),
    "xtitle_parts00_flt_c": (4159, "1610e2e46665ae52a9d3388f9f9ec51a3ae913cf4be1f9ecacf31fc81de476b4", 0x2E4, 121, 360),
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch(data):
    require(digest(data) == SOURCE_SHA, "Expected the exact gold-widened title asset; unknown or already patched input")
    layout = list(chunks(data))
    result, edits, found = bytearray(data), [], set()
    for offset, size, kind, name in layout:
        if kind != "nuccChunkModel" or name not in TARGETS:
            continue
        require(name not in found, "Duplicate overlay model")
        found.add(name)
        expected_size, expected_sha, vertex_at, count, half_height = TARGETS[name]
        start = offset + 12
        model = data[start:start + size]
        require(size == expected_size and digest(model) == expected_sha, "Unknown overlay model: " + name)
        require(model[0x34:0x38] == b"NDP3", "Missing NUD header")
        require(struct.unpack_from(">HH", model, 0x3C) == (0x200, 1), "Unknown NUD version/group count")
        require(struct.unpack_from(">HBB", model, 0xA0) == (count, 6, 0x12), "Unknown vertex count or format")
        xs = [struct.unpack_from(">f", model, vertex_at + i * 28)[0] for i in range(count)]
        require(min(xs) == -640 and max(xs) == 640, "Unknown overlay horizontal extent")
        require(struct.unpack_from(">6f", model, 0x1C) ==
                (-640.0, -float(half_height), 0.0, 640.0, float(half_height), 0.0),
                "Unknown overlay bounds")

        def put(at, value):
            before = struct.unpack_from(">f", model, at)[0]
            struct.pack_into(">f", result, start + at, value)
            edits.append(dict(model=name, offset=start + at, before=before, after=value))

        # shortcut: S24 19.5:9 geometry; use runtime coverage before supporting other ratios.
        for at in (0x1C, 0x28) + tuple(vertex_at + i * 28 for i in range(count)):
            put(at, struct.unpack_from(">f", model, at)[0] * 39 / 32)
        for at in (0x60, 0x70):
            require(math.isclose(struct.unpack_from(">f", model, at)[0],
                                 math.hypot(640, half_height), rel_tol=1e-6), "Unknown culling radius")
            put(at, math.hypot(780, half_height))

    require(found == set(TARGETS), "Missing overlay models")
    output = bytes(result)
    require(list(chunks(output)) == layout, "Container layout changed")
    allowed = {edit["offset"] + j for edit in edits for j in range(4)}
    changed = {i for i, (a, b) in enumerate(zip(data, output)) if a != b}
    require(changed and changed <= allowed, "Changed data outside declared geometry floats")
    for edit in edits:
        require(math.isclose(struct.unpack_from(">f", output, edit["offset"])[0],
                             edit["after"], rel_tol=1e-6, abs_tol=1e-6), "Geometry readback mismatch")
    return output, dict(status="static-verified-not-device-tested", source_sha256=digest(data),
                        output_sha256=digest(output), aspect="19.5:9", models=sorted(found),
                        edits=edits, changed_bytes=len(changed),
                        preserved="Gold quad, logo, textures, UVs, vertex colors, animation and other chunks")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    manifest_path = Path(str(args.output) + ".patch.json")
    require(args.source.resolve() != args.output.resolve(), "Separate output required")
    require(not args.output.exists() and not manifest_path.exists(), "Output or manifest exists; preserved")
    source = args.source.read_bytes()
    output, manifest = patch(source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(output)
    require(args.output.read_bytes() == output, "Written asset differs")
    with manifest_path.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(manifest, indent=2) + "\n")
    require(args.source.read_bytes() == source, "Source changed")
    print(json.dumps({key: manifest[key] for key in
                      ("status", "source_sha256", "output_sha256", "models", "changed_bytes")}, indent=2))


if __name__ == "__main__":
    main()
