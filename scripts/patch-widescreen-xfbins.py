"""Widen the 7 full-screen backdrop XFBIN pairs (plus title overlays) from 1280 to 1720 logical width.

Covers up to 21.5:9 (1720x720 logical space, X in [-220..1500] or [-860..860]) responsively,
while the GPU viewport clips any excess on narrower displays (16:9, 19.5:9, 20:9, 21:9).
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct

from xfbin_messages import chunks, require

TARGET_HALF_WIDTH = 860.0  # 1720.0 total logical width

# 1-3: Single-quad full-screen backdrop sprites (size 62, vertices at +0x2a)
SPRITE_TARGETS = {
    "data/interface/adv/eng/ANDROID/xadv_map.xfbin": (
        "9245f56045a86fd1ab0522a7fb7f2607dfe66c0144030e894d5a08c7ffe6e17c",
        "xadv_map_bg",
        "090661547b4a6ef482c0cd5133c3c2c441d06b49dfe5c3cab8bbeedd5bba47d9",
        (0, 0, 1280, 0, 0, 720, 1280, 720),
        (-220, 0, 1500, 0, -220, 720, 1500, 720),
    ),
    "data/interface/adv/eng/ANDROID/xadv_mission_menu.xfbin": (
        "5da9ce7c7131e546290516834fd572133903a62efad03b88060b9663451eaa76",
        "xadv_mission_menu12",
        "e34e3700310b4b0515c64089c37c898a73e3bb23517afd9b6c5dd88498ca3c64",
        (1, 0, 1281, 0, 1, 720, 1281, 720),
        (-219, 0, 1501, 0, -219, 720, 1501, 720),
    ),
    "data/interface/index/ANDROID/xcmn_index.xfbin": (
        "e08baa1ca9ffb97ec8a3e5e34e7868e6275dd4ae7694f3c5d60c685922603290",
        "xcmn_index04",
        "357d9cc98e339349781f478198fecba6e47665dfb9b7ac5d0ed7dc6cdc19129d",
        (0, 0, 1280, 0, 0, 720, 1280, 720),
        (-220, 0, 1500, 0, -220, 720, 1500, 720),
    ),
}

# 4-7 (+ title): Full-screen NUD backdrop models (bounds at +0x1C, culling radii at +0x60/+0x70)
MODEL_TARGETS = {
    "data/interface/adv/eng/ANDROID/xadv_shop.xfbin": (
        "b81778005a09a3c37741c97761506ba7612ddfee235a5696cb68aea8c7c9dbd3",
        {
            "shop_back": (756, 8, 0x154, 14, 640.0, 360.0, {
                "a4e34a0c1197578c4b797e2d8268729af390c1567f8df26f3146f96d9f4a6566",
                "7f3f4687101ce820e79b5d9aea68bff06668dd2713c10f5d5355aa37831c3275",
                "73747e2b7efde8824604a00e0851d9cc18b3fb80b61a140f5282c5e1c8816d1e",
                "931b40aa163580d47d9644833da3bf4ec23c41f8b73388c4a6a219229a6fb3fb",
                "0f8dc88886e9cf8789c5363f220dad0aa0e43ac78dffa66e944166d1b3243afc",
                "04b6532c8f6be7e0bbfa9845c7cea041885980dfb4d879bbd7e782044bb39420",
            }),
        },
    ),
    "data/interface/adv/eng/ANDROID/xadv_startmain.xfbin": (
        "96848f7937ff99618a1a5e1757f3a064bfaf94eb49a644afc9764a3081ec59d9",
        {
            "xadv_stmain_bar01": (620, 1, 0x134, 10, 640.0, 26.0, {
                "6cc3f64ff3496c04055c15b1be13edfa60e6b4d9e4ddfaf2ecf4dfca31db4ce7",
            }),
        },
    ),
    "data/interface/mode/eng/ANDROID/xmode.xfbin": (
        "887bfc1f0bc56961acbf57a914e2bee5b046e5055043b98a97fcc3e26bbe52fb",
        {
            "xmode_bg": (483, 2, 0x124, 6, 640.0, 360.0, {
                "c7f61d9f19e299e8218502c1964b1131b9ee0bd61f1849034e817fe92c7651cc",
                "b52be6da2676d3f7581453db25ec0b81591224ef933826b49c40564b76acb555",
            }),
        },
    ),
    "data/interface/option/eng/ANDROID/moption.xfbin": (
        "a1c0461e95a70e57e7f3994e81e0c8827cfdd01c0a9cd1a6ed3b71f69400f6cf",
        {
            "xmode_bg": (483, 1, 0x124, 6, 640.0, 360.0, {
                "c7f61d9f19e299e8218502c1964b1131b9ee0bd61f1849034e817fe92c7651cc",
            }),
        },
    ),
    "data/interface/title/ANDROID/xtitle_bg_e.xfbin": (
        "e1bf958a9e4eef7668dbe4fb61b694294c83963845d064fe54f133dfda446220",
        {
            "xtitle_parts00_bg": (428, 1, 0x124, 4, 780.0, 360.0, {
                "95e3e4bed8cdb283e13c173bd88665f6e49b9ed05c7e92d8ede34b1135ab9318",
            }),
            "xtitle_parts00_b": (427, 1, 0x124, 4, 640.0, 360.0, {
                "3b62ddb4eeef96c5c95765334d9273935fe63885a6257fda3325b1f94966268b",
            }),
            "xtitle_parts00_w": (427, 1, 0x124, 4, 640.0, 360.0, {
                "743bba9f8bc5b4fca6633eceff1df8ec83b7b6909593d4396624b58a7a49c7aa",
            }),
            "xtitle_parts00_flt_a": (431, 1, 0x124, 4, 640.0, 56.0, {
                "999b19ac881be36367d8266134af50b6810e54d7404186630d4d40044602e01c",
            }),
            "xtitle_parts00_flt_c": (4159, 1, 0x2E4, 121, 640.0, 360.0, {
                "1610e2e46665ae52a9d3388f9f9ec51a3ae913cf4be1f9ecacf31fc81de476b4",
            }),
        },
    ),
}


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def patch_sprite_xfbin(rel_path: str, data: bytes):
    expected_file_sha, target_name, expected_chunk_sha, before_verts, after_verts = SPRITE_TARGETS[rel_path]
    require(digest(data) == expected_file_sha, f"Unexpected source SHA-256 for {rel_path}")
    layout = list(chunks(data))
    matches = [(off, sz) for off, sz, kind, name in layout if kind == "nuccChunkSprite" and name == target_name]
    require(len(matches) == 1, f"Expected 1 {target_name} in {rel_path}, found {len(matches)}")
    off, sz = matches[0]
    start = off + 12
    sprite = data[start:start + sz]
    require(sz == 62 and digest(sprite) == expected_chunk_sha, f"Unexpected {target_name} chunk payload")
    require(struct.unpack_from(">8h", sprite, 0x2A) == before_verts, f"Unexpected {target_name} vertices")

    result = bytearray(data)
    struct.pack_into(">8h", result, start + 0x2A, *after_verts)
    output = bytes(result)

    require(list(chunks(output)) == layout, "Container chunk layout changed")
    allowed = set(range(start + 0x2A, start + 0x3A))
    changed = {i for i, (a, b) in enumerate(zip(data, output)) if a != b}
    require(changed and changed <= allowed, "Modified bytes outside sprite vertex quad")
    require(struct.unpack_from(">8h", output, start + 0x2A) == after_verts, "Sprite vertex readback mismatch")
    return output, {
        "path": rel_path,
        "kind": "nuccChunkSprite",
        "target": target_name,
        "sourceSha256": digest(data),
        "outputSha256": digest(output),
        "beforeVertices": list(before_verts),
        "afterVertices": list(after_verts),
        "logicalWidth": after_verts[2] - after_verts[0],
        "changedBytes": len(changed),
    }


def patch_model_xfbin(rel_path: str, data: bytes, check_file_sha: bool = True):
    expected_file_sha, specs = MODEL_TARGETS[rel_path]
    if check_file_sha:
        require(digest(data) == expected_file_sha, f"Unexpected source SHA-256 for {rel_path}")
    layout = list(chunks(data))
    result = bytearray(data)
    edits = []
    counts = {name: 0 for name in specs}

    for off, sz, kind, name in layout:
        if kind != "nuccChunkModel" or name not in specs:
            continue
        expected_sz, _, vertex_at, vcount, half_w, half_h, valid_shas = specs[name]
        start = off + 12
        model = data[start:start + sz]
        require(sz == expected_sz and digest(model) in valid_shas, f"Unexpected model chunk {name} in {rel_path}")
        require(model[0x34:0x38] == b"NDP3", f"Missing NDP3 header in {name}")
        require(struct.unpack_from(">HH", model, 0x3C) == (0x200, 1), f"Unexpected NUD version/group in {name}")
        require(struct.unpack_from(">HBB", model, 0xA0) == (vcount, 6, 0x12), f"Unexpected vertex format in {name}")
        xs = [struct.unpack_from(">f", model, vertex_at + i * 28)[0] for i in range(vcount)]
        require(math.isclose(min(xs), -half_w, rel_tol=1e-5) and math.isclose(max(xs), half_w, rel_tol=1e-5),
                f"Unexpected X extent in {name}")
        bounds = struct.unpack_from(">6f", model, 0x1C)
        require(bounds == (-half_w, -half_h, 0.0, half_w, half_h, 0.0), f"Unexpected bounds in {name}: {bounds}")

        factor = TARGET_HALF_WIDTH / half_w

        def put(at: int, val: float):
            before = struct.unpack_from(">f", model, at)[0]
            struct.pack_into(">f", result, start + at, val)
            edits.append({"model": name, "offset": start + at, "before": before, "after": val})

        for at in (0x1C, 0x28) + tuple(vertex_at + i * 28 for i in range(vcount)):
            old_x = struct.unpack_from(">f", model, at)[0]
            put(at, old_x * factor)
        for at in (0x60, 0x70):
            old_r = struct.unpack_from(">f", model, at)[0]
            require(math.isclose(old_r, math.hypot(half_w, half_h), rel_tol=1e-5), f"Unexpected culling radius in {name}")
            put(at, math.hypot(TARGET_HALF_WIDTH, half_h))
        counts[name] += 1

    for name, (_, expected_count, *_) in specs.items():
        require(counts[name] == expected_count, f"Expected {expected_count} instances of {name}, found {counts[name]}")

    output = bytes(result)
    require(list(chunks(output)) == layout, "Container chunk layout changed")
    allowed = {e["offset"] + j for e in edits for j in range(4)}
    changed = {i for i, (a, b) in enumerate(zip(data, output)) if a != b}
    require(changed and changed <= allowed, "Modified bytes outside declared NUD floats")
    return output, {
        "path": rel_path,
        "kind": "nuccChunkModel",
        "models": counts,
        "sourceSha256": digest(data),
        "outputSha256": digest(output),
        "logicalWidth": int(TARGET_HALF_WIDTH * 2),
        "changedBytes": len(changed),
    }


def patch_all(source_dir: Path, output_dir: Path, controls_png: Path | None = None):
    require(source_dir.resolve() != output_dir.resolve(), "Source and output directories must differ")
    require(not output_dir.exists(), "Output directory already exists; preserved")
    if controls_png is None:
        default_png = Path(__file__).resolve().parents[1] / "background-joystick-widescreen.png"
        if default_png.is_file():
            controls_png = default_png

    controls_patcher = None
    if controls_png is not None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("controls_bg", Path(__file__).with_name("patch-controls-bg-s24.py"))
        controls_patcher = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(controls_patcher)

    reports = []
    pending = []

    for rel_path in sorted(SPRITE_TARGETS):
        raw = (source_dir / rel_path).read_bytes()
        out, info = patch_sprite_xfbin(rel_path, raw)
        pending.append((rel_path, out, info))

    for rel_path in sorted(MODEL_TARGETS):
        raw = (source_dir / rel_path).read_bytes()
        orig_sha = digest(raw)
        if rel_path == "data/interface/option/eng/ANDROID/moption.xfbin" and controls_patcher is not None:
            raw = controls_patcher.patch(raw, controls_png.read_bytes())
            out, info = patch_model_xfbin(rel_path, raw, check_file_sha=False)
            info["sourceSha256"] = orig_sha
            info["controlsBackground"] = "xoption_battlebg01 panoramic PNG + xmode_bg 1720"
        else:
            out, info = patch_model_xfbin(rel_path, raw)
        pending.append((rel_path, out, info))

    output_dir.mkdir(parents=True)
    disc_replacements = {}
    sim_replacements = {}
    for rel_path, out, info in pending:
        dest = output_dir / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        with dest.open("xb") as f:
            f.write(out)
        require(dest.read_bytes() == out, f"Readback mismatch for {rel_path}")
        reports.append(info)
        if rel_path == "data/interface/option/eng/ANDROID/moption.xfbin":
            sim_replacements[rel_path] = str(dest.resolve())
        else:
            disc_replacements[rel_path] = str(dest.resolve())

    (output_dir / "installTimeDisc-replacements.json").write_text(
        json.dumps(disc_replacements, indent=2) + "\n", encoding="utf-8")
    (output_dir / "installTime-replacements.json").write_text(
        json.dumps(sim_replacements, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "status": "static-verified-1720-widescreen-backdrops",
        "logicalWidth": 1720,
        "filesPatched": len(reports),
        "files": reports,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_dir", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    manifest = patch_all(args.source_dir, args.output_dir)
    print(json.dumps({
        "status": manifest["status"],
        "logicalWidth": manifest["logicalWidth"],
        "filesPatched": manifest["filesPatched"],
        "outputs": {row["path"]: row["outputSha256"] for row in manifest["files"]},
    }, indent=2))


if __name__ == "__main__":
    main()
