"""Read CPK/@UTF metadata inside stored APK members without extracting payloads.

Format reference: https://github.com/kamikat/cpktools/blob/master/cpkunpack.py
"""
import argparse
import json
import struct
import zipfile
from pathlib import Path


def utf_table(data, with_locations=False):
    if len(data) < 32 or data[:4] != b"@UTF":
        raise ValueError("Expected a plain @UTF table")
    size, rows_at, strings_at, blobs_at, name, columns, width, count = struct.unpack_from(
        ">IIIIIHHI", data, 4
    )
    end = size + 8
    rows_at, strings_at, blobs_at = rows_at + 8, strings_at + 8, blobs_at + 8
    if not 32 <= rows_at <= strings_at <= blobs_at <= end <= len(data):
        raise ValueError("Invalid @UTF section bounds")
    if rows_at + width * count > strings_at:
        raise ValueError("@UTF rows overlap strings")

    def string(offset):
        start = strings_at + offset
        if not strings_at <= start < blobs_at:
            raise ValueError("Invalid @UTF string offset")
        stop = data.find(b"\0", start, blobs_at)
        if stop < 0:
            raise ValueError("Unterminated @UTF string")
        return data[start:stop].decode("utf-8")

    formats = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i",
               6: "Q", 7: "q", 8: "f", 9: "d", 10: "I", 11: "II"}

    def value(kind, position, limit):
        if kind not in formats:
            raise ValueError(f"Unsupported @UTF type {kind}")
        fmt = ">" + formats[kind]
        length = struct.calcsize(fmt)
        if position + length > limit:
            raise ValueError("@UTF value outside its section")
        fields = struct.unpack_from(fmt, data, position)
        result = fields[0]
        if kind == 10:
            result = string(result)
        elif kind == 11:
            offset, length_data = fields
            if blobs_at + offset + length_data > end:
                raise ValueError("@UTF blob outside table")
            result = {"offset": blobs_at + offset, "size": length_data}
        return result, position + length

    schema = []
    position = 32
    for _ in range(columns):
        if position + 5 > rows_at:
            raise ValueError("@UTF column outside schema")
        flags, key = struct.unpack_from(">BI", data, position)
        position += 5
        storage, kind = flags & 0xF0, flags & 0x0F
        constant = 0
        constant_at = position if storage == 0x30 else None
        if storage == 0x30:
            constant, position = value(kind, position, rows_at)
        elif storage not in (0x10, 0x50):
            raise ValueError(f"Unsupported @UTF storage {storage:#x}")
        schema.append((string(key), storage, kind, constant, constant_at))
    rows = []
    locations = []
    for index in range(count):
        position = rows_at + index * width
        row_end = position + width
        row = {}
        row_locations = {}
        for key, storage, kind, constant, constant_at in schema:
            row_locations[key] = (kind, position if storage == 0x50 else constant_at)
            if storage == 0x50:
                row[key], position = value(kind, position, row_end)
            else:
                row[key] = constant
        if position != row_end:
            raise ValueError("@UTF row width does not match schema")
        rows.append(row)
        locations.append(row_locations)
    return (string(name), rows, locations) if with_locations else (string(name), rows)


def inventory(apk):
    banks = []
    with zipfile.ZipFile(apk) as archive, apk.open("rb") as raw:
        for member in archive.infolist():
            if not member.filename.endswith(".awb"):
                continue
            if member.compress_type != zipfile.ZIP_STORED:
                raise ValueError("Metadata-only reader requires stored APK members")
            raw.seek(member.header_offset)
            local = raw.read(30)
            if local[:4] != b"PK\x03\x04":
                raise ValueError("Invalid ZIP local header")
            name_length, extra_length = struct.unpack_from("<HH", local, 26)
            base = member.header_offset + 30 + name_length + extra_length

            def read_at(offset, length):
                if offset < 0 or length < 0 or offset + length > member.file_size:
                    raise ValueError("Read outside CPK member")
                raw.seek(base + offset)
                data = raw.read(length)
                if len(data) != length:
                    raise ValueError("Truncated APK member")
                return data

            def packet(offset, marker):
                header = read_at(offset, 16)
                if header[:4] != marker:
                    raise ValueError(f"Expected {marker!r} at {offset:#x}")
                length = struct.unpack_from("<Q", header, 8)[0]
                if length > 32 * 1024 * 1024:
                    raise ValueError("CPK metadata packet exceeds 32 MiB")
                return utf_table(read_at(offset + 16, length))

            _, header_rows = packet(0, b"CPK ")
            if len(header_rows) != 1:
                raise ValueError("Expected one CPK header row")
            header = header_rows[0]
            toc_offset = header["TocOffset"]
            _, files = packet(toc_offset, b"TOC ")
            if len(files) != header["Files"]:
                raise ValueError("CPK file count differs from TOC")
            offset_base = min(toc_offset, header["ContentOffset"])
            entries = []
            for row in files:
                offset = offset_base + row["FileOffset"]
                size = row["FileSize"]
                if offset < 0 or offset + size > member.file_size:
                    raise ValueError("TOC payload outside CPK")
                directory = row.get("DirName") or ""
                filename = row["FileName"]
                entries.append({"path": f"{directory}/{filename}".lstrip("/"),
                                "offset": offset, "size": size,
                                "extractSize": row.get("ExtractSize", size)})
            banks.append({"member": member.filename, "size": member.file_size,
                          "tocOffset": toc_offset, "contentOffset": header["ContentOffset"],
                          "files": entries})
    return banks


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = inventory(args.apk)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("x", encoding="utf-8") as output:
        json.dump(result, output, ensure_ascii=False, indent=2)
    for bank in result:
        print(f"{bank['member']}: {len(bank['files'])} files; metadata validated")
