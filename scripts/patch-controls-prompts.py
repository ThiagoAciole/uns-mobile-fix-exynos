"""Replace the Android character-select triangle/circle prompts with GameSir Y/B glyphs."""
import argparse
import hashlib
import importlib.util
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APK_MEMBER = "assets/data/disc/installTimeDisc.awb"
XFBIN_PATH = "data/interface/mode/eng/ANDROID/xmode.xfbin"
NATIVE_MEMBER = "lib/arm64-v8a/libultimateninjastorm.so"
EXPECTED_NATIVE_SHA256 = "8797e4446449b505bd20d704c4123f4bdbedeec8b9e1e71a87414a876572cfd0"
EXPECTED_XFBIN_SHA256 = "887bfc1f0bc56961acbf57a914e2bee5b046e5055043b98a97fcc3e26bbe52fb"
TEXTURES = {
    "xmode00": "5ee4c7074e2953a92f96af24f63ccdd265c6254be88c2077962b81ecbba547e1",
    "xmode00_1": "0fa0595fcf7871348f790d5ab2ac2d810ae97c40257b7e30f32828e8b00fec53",
}
Y_GLYPH = ("1000001", "0100010", "0010100", "0001000", "0001000", "0001000", "0001000")
B_GLYPH = ("11110", "10001", "10001", "11110", "10001", "10001", "11110")
SCALE = 5
INK = bytes((244, 248, 255, 255))
OUTLINE = bytes((26, 31, 112, 255))


def load_script_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load project helper: {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


texture_codec = load_script_module("xfbin_textures", "xfbin_textures.py")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def glyph_pixels(pattern, x: int, y: int):
    points = set()
    for row, line in enumerate(pattern):
        for column, bit in enumerate(line):
            if bit == "1":
                for dy in range(SCALE):
                    for dx in range(SCALE):
                        points.add((x + column * SCALE + dx, y + row * SCALE + dy))
    return points


def paint_prompt(rgba: bytearray, width: int, height: int, clear_box, pattern, x: int, y: int):
    left, top, right, bottom = clear_box
    if not (0 <= left < right <= width and 0 <= top < bottom <= height):
        raise ValueError("Prompt bounds outside texture")
    for py in range(top, bottom):
        start = (py * width + left) * 4
        end = (py * width + right) * 4
        rgba[start:end] = bytes((right - left) * 4)

    points = glyph_pixels(pattern, x, y)
    outline = {(px + dx, py + dy) for px, py in points
               for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))}
    for px, py in outline - points:
        if 0 <= px < width and 0 <= py < height:
            at = (py * width + px) * 4
            rgba[at:at + 4] = OUTLINE
    for px, py in points:
        if 0 <= px < width and 0 <= py < height:
            at = (py * width + px) * 4
            rgba[at:at + 4] = INK


def make_texture_png(data: bytes, row) -> bytes:
    rgba = bytearray(texture_codec.decode(data, row))
    width, height = row["width"], row["height"]
    # The existing atlas has only these two PlayStation face-button glyphs.
    # Clear each original silhouette and paint a position-matched GameSir label.
    paint_prompt(rgba, width, height, (0, 310, 72, 374), Y_GLYPH, 18, 321)
    paint_prompt(rgba, width, height, (72, 310, 128, 374), B_GLYPH, 86, 326)
    return texture_codec.png_write(width, height, bytes(rgba))


def patch_xfbin(data: bytes):
    if digest(data) != EXPECTED_XFBIN_SHA256:
        raise ValueError("Unexpected xmode.xfbin SHA-256; accepted S24 base required")
    texture_rows = list(texture_codec.textures(data))
    rows = {row["name"]: row for row in texture_rows}
    if len(rows) != len(texture_rows):
        raise ValueError("Duplicate XFBIN texture names are unsupported")
    changes = {}
    for name, expected_hash in TEXTURES.items():
        row = rows.get(name)
        if row is None:
            raise ValueError(f"Missing expected prompt atlas: {name}")
        if (row["width"], row["height"], row["format"], row["mipmaps"]) != (1536, 1536, 2, 1):
            raise ValueError(f"Unexpected dimensions or format for {name}")
        if row["sha256"] != expected_hash:
            raise ValueError(f"Unexpected source texture hash for {name}")
        changes[name] = make_texture_png(data, row)
    output, report = texture_codec.replace(data, changes)
    if digest(output) == digest(data) or {item["name"] for item in report} != set(TEXTURES):
        raise ValueError("Both GameSir prompt atlases must be replaced")
    output_rows = {row["name"]: row for row in texture_codec.textures(output)}
    for name, png in changes.items():
        if texture_codec.decode(output, output_rows[name]) != texture_codec.png_read(png)[2]:
            raise ValueError(f"Texture readback mismatch: {name}")
    return output, report


def extract_xfbin(apk_path: Path):
    inventory = load_script_module("inventory_cpk", "inventory-cpk.py")
    extractor = load_script_module("extract_cpk_files", "extract-cpk-files.py")
    with zipfile.ZipFile(apk_path) as archive, apk_path.open("rb") as raw:
        native = archive.read(NATIVE_MEMBER)
        if digest(native) != EXPECTED_NATIVE_SHA256:
            raise ValueError("Unexpected native library; accepted S24 controller base required")
        banks = inventory.inventory(apk_path)
        matches = [(bank, row) for bank in banks for row in bank["files"]
                   if bank["member"] == APK_MEMBER and row["path"] == XFBIN_PATH]
        if len(matches) != 1:
            raise ValueError("Expected exactly one Android xmode.xfbin in installTimeDisc.awb")
        bank, row = matches[0]
        info = archive.getinfo(APK_MEMBER)
        if info.compress_type != zipfile.ZIP_STORED or info.file_size != bank["size"]:
            raise ValueError("APK CPK member differs from its inventory")
        raw.seek(info.header_offset)
        header = raw.read(30)
        if header[:4] != b"PK\x03\x04":
            raise ValueError("Invalid APK local header for installTimeDisc.awb")
        name_length, extra_length = struct.unpack_from("<HH", header, 26)
        data_start = info.header_offset + 30 + name_length + extra_length
        if row["offset"] < 0 or row["offset"] + row["size"] > info.file_size:
            raise ValueError("xmode.xfbin lies outside the indexed AWB member")
        raw.seek(data_start + row["offset"])
        packed = raw.read(row["size"])
        if len(packed) != row["size"]:
            raise ValueError("Truncated xmode.xfbin payload")
        decoded = extractor.decompress(packed, row["extractSize"])
    if digest(decoded) != EXPECTED_XFBIN_SHA256:
        raise ValueError("xmode.xfbin differs from the accepted S24 asset")
    return decoded


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apk", type=Path, required=True, help="Accepted S24 APK with GameSir support")
    parser.add_argument("--output-dir", type=Path, help="Fresh folder for patched XFBIN and AWB replacement")
    parser.add_argument("--check-only", action="store_true", help="Validate patch in memory without writing")
    args = parser.parse_args()
    if args.check_only == bool(args.output_dir):
        parser.error("Use --check-only or --output-dir, not both")
    apk = args.apk.resolve()
    if not apk.is_file():
        parser.error(f"APK not found: {apk}")
    source = extract_xfbin(apk)
    patched, report = patch_xfbin(source)
    result = {
        "status": "static-controller-prompt-candidate",
        "sourceXfbinSha256": digest(source),
        "outputXfbinSha256": digest(patched),
        "mappingBasis": "face-button position: PlayStation triangle to GameSir Y (top), circle to GameSir B (right)",
        "scope": "Android mode-selection prompts only; no A/X glyphs or semantic action mapping inferred",
        "textures": report,
        "deviceValidated": False,
    }
    if not args.check_only:
        output_dir = args.output_dir.resolve()
        if output_dir.exists():
            parser.error(f"Output directory exists; preserved: {output_dir}")
        output_dir.mkdir(parents=True)
        xfb_path = output_dir / "xmode.xfbin"
        xfb_path.write_bytes(patched)
        patch_cpk = load_script_module("patch_cpk", "patch-cpk.py")
        awb_path = output_dir / "installTimeDisc.awb"
        patch_cpk.patch(apk, APK_MEMBER, {XFBIN_PATH: str(xfb_path)}, awb_path)
        replacement_plan = {APK_MEMBER: str(awb_path)}
        (output_dir / "apk-plan.json").write_text(json.dumps(replacement_plan, indent=2) + "\n", encoding="utf-8")
        (output_dir / "manifest.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, zipfile.BadZipFile) as error:
        print(f"patch-controls-prompts: {error}", file=sys.stderr)
        sys.exit(1)
