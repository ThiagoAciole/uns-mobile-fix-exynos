"""Lossless editor for STORM 1 Android message binaries; standard library only.

Container reference: https://github.com/mosamadeeb/xfbin_lib/blob/main/xfbin/structure/br/br_xfbin.py
Message layout is verified against the supplied 1.2.10 files, not inferred IDs.
"""
import argparse
import copy
import hashlib
import json
import re
import struct
from pathlib import Path

LITERAL_HEADINGS = {
    "<Prohibited Actions>": "<Ações Proibidas>",
    "<Delivery Destinations>": "<Destinos de Entrega>",
    "<Destination>": "<Destino>",
    "<Flashback Mission Icons>": "<Ícones de Missões de Memórias>",
    "<Icon Types>": "<Tipos de Ícone>",
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def uints(data, offset, count):
    require(0 <= offset <= len(data) - count * 4, "Integer table outside file")
    return struct.unpack_from(f">{count}I", data, offset)


def chunks(data):
    require(data[:4] == b"NUCC" and len(data) >= 68, "Not a NUCC container")
    values = uints(data, 28, 10)
    position, strings = 68, []
    for count, size in zip(values[:6:2], values[1:6:2]):
        section = data[position:position + size]
        require(len(section) == size and section.endswith(b"\0"), "Invalid string table")
        table = section[:-1].split(b"\0")
        require(len(table) == count, "String table count mismatch")
        strings.append(table)
        position += size
    position = (position + 3) & ~3
    require(values[7] == values[6] * 12, "Unexpected map size")
    maps = [uints(data, position + i * 12, 3) for i in range(values[6])]
    position += values[7] + values[9] * 8
    indices = uints(data, position, values[8])
    position += values[8] * 4
    require(position == 28 + uints(data, 16, 1)[0] + values[9] * 8,
            "Container table size mismatch")
    page = 0
    while position < len(data):
        size, index = uints(data, position, 2)
        require(position + 12 + size <= len(data), "Chunk outside container")
        require(page + index < len(indices), "Chunk map index outside table")
        map_index = indices[page + index]
        require(map_index < len(maps), "Invalid chunk map")
        names = []
        for table, index in zip(strings, maps[map_index]):
            require(index < len(table), "String index outside table")
            names.append(table[index].decode("utf-8"))
        kind, _, name = names
        yield position, size, kind, name
        if kind == "nuccChunkPage":
            require(size == 8, "Unexpected page chunk")
            page += uints(data, position + 12, 1)[0]
        position += 12 + size
    require(position == len(data) and page == len(indices), "Incomplete container pages")


def message_body(payload):
    require(len(payload) >= 68 and uints(payload, 0, 1)[0] == len(payload) - 4,
            "Binary wrapper size mismatch")
    body = payload[4:]
    require(body[:4] == bytes.fromhex("12fc5e4e"), "Unknown message magic")
    count = uints(body, 0x30, 1)[0]
    require(count <= (len(body) - 64) // 48, "Message count outside payload")
    positions = [0x20, 0x28] + list(range(0x40, 0x40 + count * 48, 8))
    cursor, fields = 0x40 + count * 48, []
    for position in positions:
        offset, size = uints(body, position, 2)
        require(offset == cursor and offset + size <= len(body), "Noncontiguous message strings")
        fields.append(body[offset:offset + size].decode("utf-8"))
        cursor += size
    require(cursor == len(body), "Unparsed message bytes")
    return body, positions, fields, count


def catalog(data):
    entries, names = [], set()
    for position, size, kind, name in chunks(data):
        if kind != "nuccChunkBinary":
            continue
        require(name not in names, "Duplicate message chunk name")
        names.add(name)
        _, _, fields, count = message_body(data[position + 12:position + 12 + size])
        for index in range(count):
            offset = 2 + index * 6
            for field in (1, 2):
                if field == 1 and not fields[offset + field]:
                    continue
                entries.append({"chunk": name, "index": index, "field": field, "id": fields[offset],
                                "source": fields[offset + field], "translation": fields[offset + field]})
    return {"format": "storm-android-messages-v1", "source_sha256": hashlib.sha256(data).hexdigest(),
            "entries": entries}


def controls(text):
    # Engine formatting and printf arguments must survive translation in order.
    # These catalogs also contain literal phrases such as "100% chakra remaining".
    text = re.sub(r"(?<=\d)%(\s+)(?=[A-Za-z])", r"\1", text)
    # Five tutorial headings use literal brackets rather than engine control names.
    for source, translated in LITERAL_HEADINGS.items():
        text = text.replace(translated, source)
    return re.findall(r"<[^>]*>|%(?:\d+\$)?[-+ #0]*(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|ll|[hljztL])?[diuoxXfFeEgGaAcspn%]", text)


def rebuild(data, document):
    original = catalog(data)
    require(document.get("format") == original["format"] and
            document.get("source_sha256") == original["source_sha256"], "Catalog belongs to another source")
    require(len(document["entries"]) == len(original["entries"]), "Catalog entry count changed")
    edits = {}
    for old, new in zip(original["entries"], document["entries"]):
        require(all(old[key] == new.get(key) for key in ("chunk", "index", "field", "id", "source")),
                "Catalog identity/source changed")
        text = new.get("translation")
        require(isinstance(text, str) and "\0" not in text, "Invalid translation")
        require(controls(old["source"]) == controls(text), f"Formatting changed: {old['id']}")
        if text != old["source"]:
            edits[(old["chunk"], old["index"], old["field"])] = text
    output, cursor = bytearray(), 0
    for position, size, kind, name in chunks(data):
        if kind != "nuccChunkBinary":
            continue
        body, positions, fields, count = message_body(data[position + 12:position + 12 + size])
        changed = False
        for index in range(count):
            for field in (1, 2):
                key = (name, index, field)
                if key in edits:
                    fields[2 + index * 6 + field], changed = edits[key], True
        if not changed:
            continue
        new_body = bytearray(body[:0x40 + count * 48])
        for field_position, text in zip(positions, fields):
            encoded = text.encode("utf-8")
            struct.pack_into(">II", new_body, field_position, len(new_body), len(encoded))
            new_body.extend(encoded)
        payload = struct.pack(">I", len(new_body)) + new_body
        output.extend(data[cursor:position])
        output.extend(struct.pack(">I", len(payload)) + data[position + 4:position + 12] + payload)
        cursor = position + 12 + size
    output.extend(data[cursor:])
    result = bytes(output)
    reparsed = catalog(result)
    require([entry["source"] for entry in reparsed["entries"]] ==
            [entry["translation"] for entry in document["entries"]], "Reparse differs from translations")
    return result


def self_test(data):
    require(controls("100% chakra; %d%%; %s; <icon>") == ["%d", "%%", "%s", "<icon>"],
            "Literal percentage confused with printf")
    require(controls("<Destination><iconF1>%s") == controls("<Destino><iconF1>%s"),
            "Literal heading translation changed control identity")
    document = catalog(data)
    require(rebuild(data, document) == data, "Lossless round trip failed")
    edited = copy.deepcopy(document)
    entry = next(entry for entry in edited["entries"] if entry["source"])
    entry["translation"] = "Tradução: ação, coração, você. " + entry["source"]
    result = rebuild(data, edited)
    require(result != data, "Edited payload unchanged")
    before = list(chunks(data))
    after = list(chunks(result))
    require(len(before) == len(after), "Chunk count changed")
    for old, new in zip(before, after):
        op, os, ok, on = old
        np, ns, nk, nn = new
        require((ok, on) == (nk, nn), "Chunk identity changed")
        require(data[op + 4:op + 12] == result[np + 4:np + 12], "Chunk flags changed")
        if ok == "nuccChunkBinary":
            ob, _, of, oc = message_body(data[op + 12:op + 12 + os])
            nb, _, nf, nc = message_body(result[np + 12:np + 12 + ns])
            require(oc == nc and ob[:0x20] == nb[:0x20] and ob[0x30:0x40] == nb[0x30:0x40],
                    "Message metadata changed")
            require(of[:2] == nf[:2], "Message titles changed")
            for i in range(oc):
                for field in (0, 3, 4, 5):
                    require(of[2 + i * 6 + field] == nf[2 + i * 6 + field], "Voice/ID metadata changed")
        else:
            require(data[op + 12:op + 12 + os] == result[np + 12:np + 12 + ns], "Non-message chunk changed")
    corrupt = copy.deepcopy(document)
    corrupt["source_sha256"] = "0" * 64
    try:
        rebuild(data, corrupt)
    except ValueError:
        pass
    else:
        raise AssertionError("Wrong source accepted")
    protected = copy.deepcopy(document)
    tagged = next((entry for entry in protected["entries"] if controls(entry["source"])), None)
    if tagged:
        tagged["translation"] = "Removed formatting"
        try:
            rebuild(data, protected)
        except ValueError:
            pass
        else:
            raise AssertionError("Formatting removal accepted")
    try:
        catalog(data[:-1])
    except ValueError:
        pass
    else:
        raise AssertionError("Truncated input accepted")
    print(json.dumps({"records": len(document["entries"]), "nonempty": sum(bool(e["source"]) for e in document["entries"]),
                      "roundtrip_identical": True, "utf8_edit_reparsed": True, "source_guard": True,
                      "metadata_preserved": True, "truncated_rejected": True, "formatting_guard": bool(tagged)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("export", "rebuild", "self-test"))
    parser.add_argument("input", type=Path)
    parser.add_argument("--catalog", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    data = args.input.read_bytes()
    if args.operation == "self-test":
        self_test(data)
        return
    require(args.output is not None and not args.output.exists(), "A fresh --output is required")
    if args.operation == "export":
        result = (json.dumps(catalog(data), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    else:
        require(args.catalog is not None, "--catalog is required")
        result = rebuild(data, json.loads(args.catalog.read_text(encoding="utf-8-sig")))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("xb") as stream:
        stream.write(result)


if __name__ == "__main__":
    main()
