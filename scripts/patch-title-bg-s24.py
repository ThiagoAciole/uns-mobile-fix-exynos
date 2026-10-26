"""Widen only the verified title gold quad for the S24 2340x1080 preview.

NUCC/NUD reference: https://github.com/mosamadeeb/xfbin_lib
This is an asset candidate, not a runtime-validated fix or an APK builder.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
from xfbin_messages import chunks, require

TARGET = ("nuccChunkModel", "xtitle_parts00_bg")
VERTEX_X = (0x124, 0x140, 0x15C, 0x178)
POSITIONS = ((-640.0, 360.0, 0.0), (-640.0, -360.0, 0.0),
             (640.0, 360.0, 0.0), (640.0, -360.0, 0.0))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def patch(data):
    layout = list(chunks(data))
    targets = [(o, s) for o, s, k, n in layout if (k, n) == TARGET]
    require(len(targets) == 1, "Expected exactly one gold-background model")
    offset, size = targets[0]
    require(size == 428, "Unknown model layout")
    start = offset + 12
    model = data[start:start + size]
    require(digest(model) == "d7cd99b7c16a3df5f18d18affdb5b3d1ae69eb2d21b8659c53fc70ac5fbf28fa",
            "Unknown gold-background model hash or asset already patched")
    require(model[0x34:0x38] == b"NDP3", "Missing NUD header")
    require(struct.unpack_from(">I", model, 0x38)[0] == 0x172, "Unknown NUD size")
    require(struct.unpack_from(">6f", model, 0x1C) ==
            (-640.0, -360.0, 0.0, 640.0, 360.0, 0.0), "Unknown model bounds")
    for at, expected in zip(VERTEX_X, POSITIONS):
        require(struct.unpack_from(">3f", model, at) == expected,
                "Unknown vertices or asset already patched")
    require(model[0x1A6:] == bytes.fromhex("000100000007"), "Unknown material binding")
    for at in (0x54, 0x64):
        require(struct.unpack_from(">3f", model, at) == (0.0, 0.0, 0.0),
                "Unknown bounding-sphere center")
        radius = struct.unpack_from(">f", model, at + 12)[0]
        require(math.isclose(radius, math.hypot(640, 360), rel_tol=1e-6),
                "Unknown bounding radius")

    output = bytearray(data)
    edits = []
    # shortcut: fixed 19.5:9 gold-only width; use runtime ratio for other displays.
    for at in (0x1C, 0x28) + VERTEX_X:
        old = struct.unpack_from(">f", model, at)[0]
        value = old * 39 / 32
        struct.pack_into(">f", output, start + at, value)
        edits.append(dict(offset=start + at, before=old, after=value))
    for at in (0x60, 0x70):
        value = math.hypot(780, 360)
        old = struct.unpack_from(">f", model, at)[0]
        struct.pack_into(">f", output, start + at, value)
        edits.append(dict(offset=start + at, before=old, after=value))

    result = bytes(output)
    require(list(chunks(result)) == layout, "Container structure changed")
    allowed = {e["offset"] + i for e in edits for i in range(4)}
    changed = {i for i, (a, b) in enumerate(zip(data, result)) if a != b}
    require(changed and changed <= allowed, "Changed bytes outside approved floats")
    require(result[:start] == data[:start] and result[start + size:] == data[start + size:],
            "Changed another chunk, animation, texture or logo")
    for at, expected in zip(VERTEX_X, POSITIONS):
        actual = struct.unpack_from(">3f", result, start + at)
        require(actual == (expected[0] * 39 / 32, expected[1], expected[2]),
                "Patched geometry failed readback")
    return result, dict(model=TARGET[1], model_chunk_offset=offset, edits=edits,
                        changed_bytes=len(changed), source_sha256=digest(data),
                        output_sha256=digest(result), aspect="19.5:9", factor=39 / 32)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path, help="New output file; overwrite is refused")
    args = parser.parse_args()
    require(not args.output.exists(), "Output already exists; preserved")
    manifest = args.output.with_suffix(args.output.suffix + ".patch.json")
    require(not manifest.exists(), "Manifest already exists; preserved")
    source = args.source.read_bytes()
    result, info = patch(source)
    # Reapplying must fail rather than silently widening a second time.
    try:
        patch(result)
    except ValueError:
        pass
    else:
        raise AssertionError("Already-patched input was accepted")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(result)
    require(args.output.read_bytes() == result, "Output readback differs")
    manifest.write_text(json.dumps(info, indent=2) + "\n", encoding="utf-8")
    require(args.source.read_bytes() == source, "Source changed")
    print(json.dumps(info, indent=2))


if __name__ == "__main__":
    main()
