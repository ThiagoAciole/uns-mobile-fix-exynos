"""Append replacement files to one CPK bank, preserving original payloads and TOC order."""
import argparse
import hashlib
import importlib.util
import json
import shutil
import struct
import zipfile
from pathlib import Path

spec = importlib.util.spec_from_file_location("inventory_cpk", Path(__file__).with_name("inventory-cpk.py"))
inventory_cpk = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory_cpk)


def packet(stream, offset, marker):
    stream.seek(offset)
    prefix = stream.read(16)
    if len(prefix) != 16 or prefix[:4] != marker:
        raise ValueError("Invalid CPK metadata packet")
    size = struct.unpack_from("<Q", prefix, 8)[0]
    if size > 32 * 1024 * 1024:
        raise ValueError("Metadata exceeds limit")
    data = bytearray(stream.read(size))
    if len(data) != size:
        raise ValueError("Truncated metadata")
    _, rows, locations = inventory_cpk.utf_table(data, with_locations=True)
    return data, rows, locations


def set_integer(data, location, value):
    kind, offset = location
    if offset is None or kind not in (2, 4, 6):
        raise ValueError("Field is not a writable unsigned integer")
    struct.pack_into({2: ">H", 4: ">I", 6: ">Q"}[kind], data, offset, value)


def patch(apk, member, replacements, output):
    if output.exists() or not replacements:
        raise ValueError("Fresh output and nonempty replacements required")
    replacements = {name: Path(path) for name, path in replacements.items()}
    for path in replacements.values():
        if not path.is_file() or not 0 < path.stat().st_size <= 64 * 1024 * 1024:
            raise ValueError(f"Invalid replacement: {path}")
    with zipfile.ZipFile(apk) as archive:
        info = archive.getinfo(member)
        if info.compress_type != zipfile.ZIP_STORED:
            raise ValueError("Expected stored CPK bank")
        output.parent.mkdir(parents=True, exist_ok=True)
        with archive.open(info) as source, output.open("xb") as target:
            shutil.copyfileobj(source, target, 4 * 1024 * 1024)
    changes = []
    with output.open("r+b") as bank:
        header_data, headers, header_locations = packet(bank, 0, b"CPK ")
        if len(headers) != 1:
            raise ValueError("Expected single CPK header")
        header = headers[0]
        toc_at = header["TocOffset"]
        toc_data, rows, locations = packet(bank, toc_at, b"TOC ")
        if len(rows) != header["Files"]:
            raise ValueError("CPK file count mismatch")
        base = min(toc_at, header["ContentOffset"])
        paths = [f"{row.get('DirName') or ''}/{row['FileName']}".lstrip("/") for row in rows]
        if len(set(paths)) != len(paths) or not replacements.keys() <= set(paths):
            raise ValueError("Missing or ambiguous replacement path")
        for index, name in enumerate(paths):
            if name not in replacements:
                continue
            data = replacements[name].read_bytes()
            bank.seek(0, 2)
            alignment = header["Align"]
            if not 1 <= alignment <= 65536:
                raise ValueError("Invalid CPK alignment")
            bank.write(bytes((-bank.tell()) % alignment))
            start = bank.tell()
            bank.write(data)
            for field, value in (("FileOffset", start - base), ("FileSize", len(data)), ("ExtractSize", len(data))):
                set_integer(toc_data, locations[index][field], value)
            changes.append({"path": name, "offset": start, "size": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        bank.seek(0, 2)
        bank.write(bytes((-bank.tell()) % header["Align"]))
        size = bank.tell()
        set_integer(header_data, header_locations[0]["ContentSize"], size - header["ContentOffset"])
        bank.seek(16)
        bank.write(header_data)
        bank.seek(toc_at + 16)
        bank.write(toc_data)
        # Parse bytes written, then prove all other entries retain their metadata.
        _, new_rows, _ = packet(bank, toc_at, b"TOC ")
        for index, name in enumerate(paths):
            if name not in replacements and rows[index] != new_rows[index]:
                raise ValueError("Untouched CPK entry changed")
        for change in changes:
            row = new_rows[paths.index(change["path"])]
            if row["FileOffset"] + base != change["offset"] or row["FileSize"] != change["size"] or row["ExtractSize"] != change["size"]:
                raise ValueError("Replacement TOC mismatch")
            bank.seek(change["offset"])
            if hashlib.sha256(bank.read(change["size"])).hexdigest() != change["sha256"]:
                raise ValueError("Replacement hash mismatch")
    # Compare every original byte outside the two metadata packets, not just TOC sizes.
    with zipfile.ZipFile(apk) as archive, archive.open(member) as source, output.open("rb") as target:
        ranges = [(16, 16 + len(header_data)), (toc_at + 16, toc_at + 16 + len(toc_data))]
        position = 0
        while position < info.file_size:
            count = min(4 * 1024 * 1024, info.file_size - position)
            original, actual = bytearray(source.read(count)), bytearray(target.read(count))
            if len(original) != count or len(actual) != count:
                raise ValueError("Truncated original CPK comparison")
            for start, stop in ranges:
                left, right = max(start, position), min(stop, position + count)
                if left < right:
                    original[left-position:right-position] = actual[left-position:right-position]
            if original != actual:
                raise ValueError("Original CPK payload changed")
            position += count
    with output.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    manifest = {"sourceApk": str(apk.resolve()), "member": member, "changes": changes,
                "sha256": digest, "size": size, "originalPayloads": "byte-identical outside header and TOC"}
    Path(str(output) + ".patch.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("member")
    parser.add_argument("replacements", type=Path, help="JSON object: CPK path to local replacement file")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = patch(args.apk, args.member, json.loads(args.replacements.read_text(encoding="utf-8-sig")), args.output)
    print(f"Verified {len(result['changes'])} replacements; {result['size']} bytes")
