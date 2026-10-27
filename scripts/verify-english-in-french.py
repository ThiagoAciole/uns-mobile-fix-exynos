"""Verify the language candidate against the exact original and accepted base APKs."""
import argparse
import zipfile
from pathlib import Path

from english_in_french import (BASE_SHA, ORIGINAL_SHA, DISC, LANGUAGES, MESSAGE,
                               adapt_resource_paths, digest_file, member_start, module, read_entry,
                               rename_language_choices)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--original', type=Path, required=True)
    parser.add_argument('--base', type=Path, required=True)
    parser.add_argument('--candidate', type=Path, required=True)
    args = parser.parse_args()
    original, base, candidate = args.original.resolve(), args.base.resolve(), args.candidate.resolve()
    if digest_file(original) != ORIGINAL_SHA or digest_file(base) != BASE_SHA:
        raise ValueError('Unexpected original or base APK')
    inv, unpack = module('inventory-cpk'), module('extract-cpk-files')
    originals = {b['member']: b for b in inv.inventory(original)}
    bases = {b['member']: b for b in inv.inventory(base)}
    results = {b['member']: b for b in inv.inventory(candidate)}
    pair_count = 0
    for name, old_bank in originals.items():
        old = {r['path']: r for r in old_bank['files']}
        src = {r['path']: r for r in bases[name]['files']}
        dst = {r['path']: r for r in results[name]['files']}
        english = [p for p in old if '/eng/' in p]
        if not english:
            continue
        targets = {p.replace('/eng/', '/fre/'): old[p] for p in english}
        edits = {MESSAGE.format(lang) for lang in LANGUAGES} if name == DISC else set()
        title_paths = {p.replace('/eng/', '/fre/'): p for p in english
                       if p.startswith(('data/adv_title/main/eng/', 'data/adv_title/sub/eng/'))}
        edits.update(title_paths)
        if set(src) != set(dst):
            raise ValueError('CPK entry list changed: ' + name)
        for path, row in src.items():
            if path not in targets and path not in edits and row != dst[path]:
                raise ValueError('Unrelated CPK entry changed: ' + path)
        orig_start = member_start(original, name)
        candidate_start = member_start(candidate, name)
        with original.open('rb') as orig_file, candidate.open('rb') as out_file:
            for path, source in targets.items():
                if path in edits:
                    continue
                result = dst[path]
                if any(result[k] != source[k] for k in ('offset', 'size', 'extractSize')):
                    raise ValueError('Alias metadata differs: ' + path)
                orig_file.seek(orig_start + source['offset'])
                out_file.seek(candidate_start + result['offset'])
                a, b = orig_file.read(source['size']), out_file.read(result['size'])
                if len(a) != source['size'] or a != b:
                    raise ValueError('Alias payload differs: ' + path)
            pair_count += len(targets)
        if name == DISC:
            for language in LANGUAGES:
                path = MESSAGE.format(language)
                source_apk = original if language == 'fre' else base
                source_bank = old_bank if language == 'fre' else bases[name]
                source_row = old[MESSAGE.format('eng')] if language == 'fre' else src[path]
                expected = rename_language_choices(read_entry(source_apk, name, source_row, unpack))
                actual = read_entry(candidate, name, dst[path], unpack)
                if actual != expected:
                    raise ValueError('Message content differs: ' + path)
        for path, english_path in title_paths.items():
            eng = read_entry(original, name, old[english_path], unpack)
            fre = read_entry(original, name, old[path], unpack)
            expected = adapt_resource_paths(eng, fre)
            actual = read_entry(candidate, name, dst[path], unpack)
            if actual != expected:
                raise ValueError('Mission title content differs: ' + path)
    if pair_count != 259:
        raise ValueError('Unexpected pair count')
    changed_banks = {name for name, b in originals.items() if any('/eng/' in r['path'] for r in b['files'])}
    with zipfile.ZipFile(base) as before, zipfile.ZipFile(candidate) as after:
        b = {x.filename: (x.CRC, x.file_size) for x in before.infolist() if not x.filename.startswith('META-INF/') and x.filename != 'stamp-cert-sha256'}
        a = {x.filename: (x.CRC, x.file_size) for x in after.infolist() if not x.filename.startswith('META-INF/') and x.filename != 'stamp-cert-sha256'}
        if b.keys() != a.keys():
            raise ValueError('APK payload member list changed')
        for name in b.keys() - changed_banks:
            if b[name] != a[name]:
                raise ValueError('Unrelated APK payload changed: ' + name)
    print('Verified 259 pairs, six message catalogs and all unrelated APK members (CRC and size).')
    print('Candidate SHA-256:', digest_file(candidate))


if __name__ == '__main__':
    main()
