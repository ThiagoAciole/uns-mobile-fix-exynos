"""Extract explicitly named CPK files from the metadata inventory, never a full bank.

CRILAYLA format reference: https://github.com/esperknight/CriPakTools/blob/master/CriPakTools/CPK.cs
"""
import argparse
import hashlib
import json
import struct
import zipfile
from pathlib import Path, PurePosixPath


def decompress(data, expected):
    if data[:8] != b"CRILAYLA":
        if len(data) != expected:
            raise ValueError("Unknown compression or incorrect raw size")
        return data
    if len(data) < 272:
        raise ValueError("Truncated CRILAYLA header")
    size, header_at = struct.unpack_from("<II", data, 8)
    if size + 256 != expected or header_at + 272 != len(data):
        raise ValueError("CRILAYLA sizes differ from TOC")
    output = bytearray(expected)
    output[:256] = data[header_at + 16:]
    source, pool, remaining = header_at + 15, 0, 0

    def bits(count):
        nonlocal source, pool, remaining
        result = 0
        while count:
            if not remaining:
                if source < 16:
                    raise ValueError("CRILAYLA bitstream exhausted")
                pool, remaining = data[source], 8
                source -= 1
            take = min(remaining, count)
            result = (result << take) | ((pool >> (remaining - take)) & ((1 << take) - 1))
            remaining -= take
            count -= take
        return result

    destination = expected - 1
    while destination >= 256:
        if not bits(1):
            output[destination] = bits(8)
            destination -= 1
            continue
        reference = destination + bits(13) + 3
        length = 3
        for width in (2, 3, 5, 8):
            value = bits(width)
            length += value
            if value != (1 << width) - 1:
                break
        else:
            value = 255
            while value == 255:
                value = bits(8)
                length += value
        if reference >= expected or length > destination - 255:
            raise ValueError("CRILAYLA back-reference outside output")
        for _ in range(length):
            output[destination] = output[reference]
            destination -= 1
            reference -= 1
    return bytes(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("inventory", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--file", action="append", required=True, dest="files")
    args = parser.parse_args()
    if args.output.exists():
        raise ValueError("Output directory already exists; preserved")
    banks = json.loads(args.inventory.read_text(encoding="utf-8"))
    selected = [(bank, row) for bank in banks for row in bank["files"] if row["path"] in args.files]
    if len(selected) != len(set(args.files)):
        raise ValueError("Missing or ambiguous requested CPK path")
    pending = []
    with zipfile.ZipFile(args.apk) as archive, args.apk.open("rb") as raw:
        for bank, row in selected:
            path = PurePosixPath(row["path"])
            if path.is_absolute() or ".." in path.parts or "\\" in str(path) or ":" in str(path):
                raise ValueError("Unsafe output path")
            if not 0 < row["extractSize"] <= 64 * 1024 * 1024:
                raise ValueError("Selected file exceeds 64 MiB limit")
            member = archive.getinfo(bank["member"])
            if member.compress_type != zipfile.ZIP_STORED or member.file_size != bank["size"]:
                raise ValueError("APK member differs from inventory")
            raw.seek(member.header_offset)
            local = raw.read(30)
            if local[:4] != b"PK\x03\x04":
                raise ValueError("Invalid ZIP local header")
            name_length, extra_length = struct.unpack_from("<HH", local, 26)
            if row["offset"] < 0 or row["offset"] + row["size"] > member.file_size:
                raise ValueError("Selected payload outside CPK")
            raw.seek(member.header_offset + 30 + name_length + extra_length + row["offset"])
            packed = raw.read(row["size"])
            if len(packed) != row["size"]:
                raise ValueError("Truncated selected payload")
            decoded = decompress(packed, row["extractSize"])
            pending.append((path, decoded, {"member": bank["member"], "path": str(path),
                            "packedSha256": hashlib.sha256(packed).hexdigest(),
                            "sha256": hashlib.sha256(decoded).hexdigest(), "size": len(decoded)}))
    args.output.mkdir(parents=True)
    for path, decoded, metadata in pending:
        destination = args.output.joinpath(*path.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as output:
            output.write(decoded)
        print(f"{path}: {len(decoded)} bytes; size and bounds validated")
    (args.output / "manifest.json").write_text(
        json.dumps([item[2] for item in pending], indent=2), encoding="utf-8")
