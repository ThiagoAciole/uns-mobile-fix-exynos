"""Prepare English in the French slot while preserving the current pt-BR APK."""

import argparse
import hashlib
import importlib.util
import json
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from xfbin_messages import catalog, chunks, rebuild

ROOT = Path(__file__).resolve().parents[1]
BASE_SHA = '291e1e5f59a7d18c9bc945b38b035333cfd48ac58eac4099c5d79a4f3428b3fd'
ORIGINAL_SHA = 'e0386533659f517e54cea333605319d33160d862bf6540ec3e57c730100b707f'
DISC = 'assets/data/disc/installTimeDisc.awb'
MESSAGE = 'data/event/{}/message.bin.xfbin'
LANGUAGES = ('eng', 'fre', 'ger', 'ita', 'jpn', 'spa')


def module(filename):
    spec = importlib.util.spec_from_file_location(filename.replace('-', '_'), ROOT / 'scripts' / (filename + '.py'))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def digest_file(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def rename_language_choices(data):
    document = catalog(data)
    expected = {'NS1_Mobile_Option_Language_Setting_01': 'Português (Brasil)',
                'NS1_Mobile_Option_Language_Setting_02': 'English'}
    found = set()
    for entry in document['entries']:
        if entry['chunk'] == 'Mobile' and entry['field'] == 2 and entry['id'] in expected:
            if entry['id'] in found:
                raise ValueError('Duplicate language choice')
            found.add(entry['id'])
            entry['translation'] = expected[entry['id']]
    if found != set(expected):
        raise ValueError('Language choices not found')
    return rebuild(data, document)


def adapt_resource_paths(english, french):
    def path_table(data):
        list(chunks(data))
        counts = struct.unpack_from('>6I', data, 28)
        first_size, path_count, path_size = counts[1:4]
        start = 68 + first_size
        table = data[start:start + path_size]
        paths = table[:-1].split(b'\0')
        if not table.endswith(b'\0') or len(paths) != path_count:
            raise ValueError('Invalid XFBIN resource paths')
        return start, table, paths

    start, table, paths = path_table(english)
    _, _, french_paths = path_table(french)
    replacements = {}
    for path in paths:
        new = path.replace(b'/eng/', b'/fre/').replace(b'\\eng\\', b'\\fre\\')
        if new != path:
            if new not in french_paths:
                raise ValueError('French resource path missing')
            replacements[path] = new
    if not replacements:
        raise ValueError('English resource path missing')
    modified = b'\0'.join(replacements.get(path, path) for path in paths) + b'\0'
    if len(modified) != len(table):
        raise ValueError('Resource path table size changed')
    result = english[:start] + modified + english[start + len(table):]
    list(chunks(result))
    return result


def member_start(apk, member):
    with zipfile.ZipFile(apk) as archive, apk.open('rb') as stream:
        info = archive.getinfo(member)
        if info.compress_type != zipfile.ZIP_STORED:
            raise ValueError('Expected stored CPK')
        stream.seek(info.header_offset)
        header = stream.read(30)
        if header[:4] != b'PK\x03\x04':
            raise ValueError('Bad ZIP local header')
        name, extra = struct.unpack_from('<HH', header, 26)
        return info.header_offset + 30 + name + extra


def read_entry(apk, bank, row, unpack):
    with apk.open('rb') as stream:
        stream.seek(member_start(apk, bank) + row['offset'])
        packed = stream.read(row['size'])
    if len(packed) != row['size']:
        raise ValueError('Truncated CPK entry')
    return unpack.decompress(packed, row['extractSize'])


def prepare_bank(original, base, old_bank, base_bank, output, replacements, cpk):
    """Redirect French TOC rows to verified original English bytes; append edits."""
    old_rows = {r['path']: r for r in old_bank['files']}
    current_rows = {r['path']: r for r in base_bank['files']}
    english = sorted(p for p in old_rows if '/eng/' in p)
    aliases = {p.replace('/eng/', '/fre/'): old_rows[p] for p in english}
    if len(aliases) != len(english) or not aliases.keys() <= old_rows.keys() or not aliases.keys() <= current_rows.keys():
        raise ValueError('Missing or ambiguous English/French pair')
    # Original bytes must still exist at the exact original offsets in the base CPK.
    orig_start = member_start(original, old_bank['member'])
    base_start = member_start(base, base_bank['member'])
    with original.open('rb') as src, base.open('rb') as dst:
        for path, row in aliases.items():
            src.seek(orig_start + row['offset'])
            dst.seek(base_start + row['offset'])
            a, b = src.read(row['size']), dst.read(row['size'])
            if len(a) != row['size'] or a != b:
                raise ValueError('Original packed bytes changed: ' + path)
    with zipfile.ZipFile(base) as archive, archive.open(base_bank['member']) as source, output.open('xb') as target:
        shutil.copyfileobj(source, target, 4 * 1024 * 1024)
    with output.open('r+b') as bank:
        header_data, headers, header_locs = cpk.packet(bank, 0, b'CPK ')
        header = headers[0]
        toc_at = header['TocOffset']
        toc_data, rows, locs = cpk.packet(bank, toc_at, b'TOC ')
        paths = [f"{r.get('DirName') or ''}/{r['FileName']}".lstrip('/') for r in rows]
        if len(set(paths)) != len(paths) or not (aliases.keys() | replacements.keys()) <= set(paths):
            raise ValueError('CPK targets missing or ambiguous')
        offset_base = min(toc_at, header['ContentOffset'])
        changed = {}
        for index, path in enumerate(paths):
            if path in replacements:
                data = replacements[path]
                bank.seek(0, 2)
                bank.write(bytes((-bank.tell()) % header['Align']))
                offset = bank.tell()
                bank.write(data)
                fields = (offset - offset_base, len(data), len(data))
                changed[path] = hashlib.sha256(data).hexdigest()
            elif path in aliases:
                row = aliases[path]
                fields = (row['offset'] - offset_base, row['size'], row['extractSize'])
            else:
                continue
            for field, value in zip(('FileOffset', 'FileSize', 'ExtractSize'), fields):
                cpk.set_integer(toc_data, locs[index][field], value)
        bank.seek(0, 2)
        bank.write(bytes((-bank.tell()) % header['Align']))
        cpk.set_integer(header_data, header_locs[0]['ContentSize'], bank.tell() - header['ContentOffset'])
        bank.seek(16)
        bank.write(header_data)
        bank.seek(toc_at + 16)
        bank.write(toc_data)
        _, new_rows, _ = cpk.packet(bank, toc_at, b'TOC ')
        for i, path in enumerate(paths):
            if path not in aliases and path not in replacements and rows[i] != new_rows[i]:
                raise ValueError('Unexpected TOC change: ' + path)
            if path in aliases and path not in replacements:
                expected = aliases[path]
                row = new_rows[i]
                if (row['FileOffset'] + offset_base, row['FileSize'], row['ExtractSize']) != (expected['offset'], expected['size'], expected['extractSize']):
                    raise ValueError('Alias verification failed: ' + path)
            if path in changed:
                row = new_rows[i]
                bank.seek(row['FileOffset'] + offset_base)
                if hashlib.sha256(bank.read(row['FileSize'])).hexdigest() != changed[path]:
                    raise ValueError('Replacement hash failed: ' + path)
    # All original payload bytes must remain unchanged, except CPK metadata packets.
    with zipfile.ZipFile(base) as archive, archive.open(base_bank['member']) as source, output.open('rb') as target:
        ranges = [(16, 16 + len(header_data)), (toc_at + 16, toc_at + 16 + len(toc_data))]
        position = 0
        while position < base_bank['size']:
            count = min(4 * 1024 * 1024, base_bank['size'] - position)
            before, after = bytearray(source.read(count)), bytearray(target.read(count))
            if len(before) != count or len(after) != count:
                raise ValueError('Truncated CPK validation')
            for left, right in ranges:
                start, end = max(left, position), min(right, position + count)
                if start < end:
                    before[start-position:end-position] = after[start-position:end-position]
            if before != after:
                raise ValueError('Existing CPK payload changed')
            position += count
    return {'aliases': len(aliases), 'replacements': changed}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', required=True, type=Path)
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    original, base, output = args.original.resolve(), args.base.resolve(), args.output.resolve()
    if output.exists() or output == base or output == original or output.is_relative_to(ROOT / 'origin') or output.is_relative_to(ROOT / 'original'):
        raise ValueError('Output must be a fresh path outside protected directories')
    if digest_file(original) != ORIGINAL_SHA or digest_file(base) != BASE_SHA:
        raise ValueError('Unexpected APK SHA-256; no candidate generated')
    inv, unpack, cpk = module('inventory-cpk'), module('extract-cpk-files'), module('patch-cpk')
    original_banks = {b['member']: b for b in inv.inventory(original)}
    base_banks = {b['member']: b for b in inv.inventory(base)}
    disc_old, disc_base = original_banks[DISC], base_banks[DISC]
    old_rows = {r['path']: r for r in disc_old['files']}
    base_rows = {r['path']: r for r in disc_base['files']}
    disc_replacements = {}
    for language in LANGUAGES:
        path = MESSAGE.format(language)
        source_apk, bank, row = ((original, disc_old, old_rows[MESSAGE.format('eng')]) if language == 'fre'
                                 else (base, disc_base, base_rows[path]))
        disc_replacements[path] = rename_language_choices(read_entry(source_apk, bank['member'], row, unpack))
    with tempfile.TemporaryDirectory(prefix='naruto-language-assets-') as temp:
        tmp = Path(temp)
        plans, reports = {}, {}
        for i, (name, old_bank) in enumerate(original_banks.items()):
            if not any('/eng/' in r['path'] for r in old_bank['files']):
                continue
            replacements = dict(disc_replacements) if name == DISC else {}
            rows = {r['path']: r for r in old_bank['files']}
            titles = [p for p in rows if p.startswith(('data/adv_title/main/eng/', 'data/adv_title/sub/eng/'))]
            for path in titles:
                translated_path = path.replace('/eng/', '/fre/')
                original_title = read_entry(original, name, rows[path], unpack)
                french_title = read_entry(original, name, rows[translated_path], unpack)
                replacements[translated_path] = adapt_resource_paths(original_title, french_title)
            if titles and len(titles) != 110:
                raise ValueError('Unexpected mission title count')
            file = tmp / f'bank-{i}.awb'
            reports[name] = prepare_bank(original, base, old_bank, base_banks[name], file,
                                         replacements, cpk)
            plans[name] = str(file)
        if sum(x['aliases'] for x in reports.values()) != 259:
            raise ValueError('Unexpected number of language pairs')
        plan = tmp / 'apk-plan.json'
        plan.write_text(json.dumps(plans), encoding='utf-8')
        native_name = 'lib/arm64-v8a/libultimateninjastorm.so'
        library = tmp / 'libultimateninjastorm.so'
        with zipfile.ZipFile(base) as apk:
            library.write_bytes(apk.read(native_name))
        lib_hash = digest_file(library)
        Path(str(library) + '.patch.json').write_text(json.dumps({'sourceSha256': lib_hash, 'outputSha256': lib_hash}), encoding='utf-8')
        subprocess.run([sys.executable, str(ROOT / 'scripts/repack-native-apk.py'), str(base), str(library), str(output), '--replacements', str(plan)], check=True)
        report = output.with_name(output.name + '.language.json')
        report.write_text(json.dumps({'originalSha256': ORIGINAL_SHA, 'baseSha256': BASE_SHA, 'banks': reports,
                                      'unsignedSha256': digest_file(output), 'status': 'unsigned-not-device-tested'}, indent=2), encoding='utf-8')
        print('Candidate created; sign and verify before installation:', output)


if __name__ == '__main__':
    main()
