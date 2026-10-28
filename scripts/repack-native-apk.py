"""Replace the verified game native library; preserve all other APK payloads."""
import argparse
import copy
import hashlib
import json
import shutil
import struct
import zipfile
from pathlib import Path

# Python switches to ZIP64 at 2 GiB; APK signing requires classic ZIP (up to 4 GiB).
zipfile.ZIP64_LIMIT = 0xFFFFFFFF


def clean_extra(extra):
    result = bytearray()
    position = 0
    while position < len(extra):
        # Existing zipalign padding may be bare zero bytes rather than a tagged field.
        if not any(extra[position:]):
            break
        if position + 4 > len(extra):
            raise ValueError("Truncated ZIP extra field")
        kind, size = struct.unpack_from("<HH", extra, position)
        end = position + 4 + size
        if end > len(extra):
            raise ValueError("ZIP extra field outside header")
        if kind not in (0x0001, 0xD935):
            result.extend(extra[position:end])
        position = end
    return bytes(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("library", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--replacements", type=Path, help="JSON object: additional APK member to local file")
    args = parser.parse_args()
    if args.output.exists() or args.output.resolve() == args.apk.resolve():
        raise ValueError("A fresh separate output APK is required")
    if args.output.resolve().is_relative_to(Path(__file__).resolve().parents[1] / "build"):
        raise ValueError("build/ is reserved for build-selective.py output; use work/ for intermediates")
    patch = json.loads(Path(str(args.library) + ".patch.json").read_text(encoding="utf-8-sig"))
    library_hash = hashlib.sha256(args.library.read_bytes()).hexdigest().upper()
    if library_hash != patch["outputSha256"].upper():
        raise ValueError("Patched library differs from patch manifest")
    native_name = "lib/arm64-v8a/libultimateninjastorm.so"
    replacements = json.loads(args.replacements.read_text(encoding="utf-8-sig")) if args.replacements else {}
    if native_name in replacements or any(name.startswith("META-INF/") for name in replacements):
        raise ValueError("Additional replacements cannot override native/signature handling")
    replacements = {name: Path(path) for name, path in replacements.items()}
    for path in replacements.values():
        if not path.is_file():
            raise ValueError(f"Missing replacement: {path}")
    replacement_hashes = {}
    for name, path in replacements.items():
        with path.open("rb") as payload:
            replacement_hashes[name] = hashlib.file_digest(payload, "sha256").hexdigest()
    replacements[native_name] = args.library
    expected = {}
    removed = []
    with zipfile.ZipFile(args.apk) as source:
        names = source.namelist()
        if len(set(names)) != len(names):
            raise ValueError("Duplicate ZIP member names are unsupported")
        if not replacements.keys() <= set(names):
            raise ValueError("Replacement member missing from source APK")
        with source.open(native_name) as original:
            if hashlib.file_digest(original, "sha256").hexdigest().upper() != patch["sourceSha256"].upper():
                raise ValueError("Input APK native library differs from patch source")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.output, "x", allowZip64=False) as target:
            for original_info in source.infolist():
                name = original_info.filename
                upper = name.upper()
                if name == "stamp-cert-sha256" or (upper.startswith("META-INF/") and
                        (upper.endswith((".SF", ".RSA", ".DSA", ".EC")) or upper == "META-INF/MANIFEST.MF")):
                    removed.append(name)
                    continue
                if original_info.flag_bits & 1:
                    raise ValueError("Encrypted ZIP members are unsupported")
                info = copy.copy(original_info)
                info.extra = clean_extra(info.extra)
                if name in replacements:
                    info.compress_type = zipfile.ZIP_STORED
                    info.file_size = replacements[name].stat().st_size
                if info.compress_type == zipfile.ZIP_STORED:
                    alignment = 16384 if name.startswith("lib/") and name.endswith(".so") else 4
                    try:
                        encoded_name = name.encode("ascii")
                    except UnicodeEncodeError:
                        encoded_name = name.encode("utf-8")
                    start = target.fp.tell() + 30 + len(encoded_name) + len(info.extra)
                    # Android's 0xd935 field starts with uint16 alignment, followed by padding.
                    padding = (-start - 6) % alignment
                    info.extra += struct.pack("<HHH", 0xD935, padding + 2, alignment) + bytes(padding)
                    if len(info.extra) > 65535:
                        raise ValueError("Alignment exceeds ZIP extra field limit")
                reader = replacements[name].open("rb") if name in replacements else source.open(original_info)
                with reader, target.open(info, "w") as writer:
                    shutil.copyfileobj(reader, writer, 4 * 1024 * 1024)
                if name not in replacements and (info.CRC != original_info.CRC or info.file_size != original_info.file_size):
                    raise ValueError(f"Unexpected payload change: {name}")
                expected[name] = (info.CRC, info.file_size)
    with zipfile.ZipFile(args.output) as result:
        actual = {info.filename: (info.CRC, info.file_size) for info in result.infolist()}
        if actual != expected:
            raise ValueError("Output central directory differs from written payloads")
        with result.open(native_name) as native:
            if hashlib.file_digest(native, "sha256").hexdigest().upper() != library_hash:
                raise ValueError("Output native library hash mismatch")
        for name, digest in replacement_hashes.items():
            with result.open(name) as payload:
                if hashlib.file_digest(payload, "sha256").hexdigest() != digest:
                    raise ValueError(f"Replacement hash mismatch: {name}")
    Path(str(args.output) + ".repack.json").write_text(json.dumps({
        "source": str(args.apk.resolve()), "nativeSha256": library_hash,
        "members": len(expected), "removedSignatureEntries": removed,
        "replacementsSha256": replacement_hashes,
        "otherPayloads": "CRC32 and uncompressed size preserved for every unchanged member",
        "status": "unsigned-aligned-candidate-not-device-tested",
    }, indent=2), encoding="utf-8")
    print(f"Repacked {len(expected)} members; native SHA-256 verified; other payload CRCs preserved")
