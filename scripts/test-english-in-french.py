import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from english_in_french import rename_language_choices, adapt_resource_paths, module, read_entry
from xfbin_messages import catalog


class LanguageChoiceTests(unittest.TestCase):
    @staticmethod
    def original():
        return (Path(__file__).resolve().parents[1] / 'work/inventory/localization-eng/data/event/eng/message.bin.xfbin').read_bytes()

    def test_original_messages_relabel_both_slots_without_changing_other_texts(self):
        source = self.original()
        before = catalog(source)['entries']
        after = catalog(rename_language_choices(source))['entries']
        self.assertEqual(len(before), len(after))
        expected = {'NS1_Mobile_Option_Language_Setting_01': 'Português (Brasil)',
                    'NS1_Mobile_Option_Language_Setting_02': 'English'}
        found = set()
        for old, new in zip(before, after):
            self.assertEqual((old['chunk'], old['index'], old['field'], old['id']),
                             (new['chunk'], new['index'], new['field'], new['id']))
            if old['id'] in expected and old['chunk'] == 'Mobile' and old['field'] == 2:
                self.assertEqual(new['source'], expected[old['id']])
                found.add(old['id'])
            else:
                self.assertEqual(new['source'], old['source'])
        self.assertEqual(found, set(expected))

    def test_unknown_language_id_is_rejected(self):
        source = self.original()
        original_id = b'NS1_Mobile_Option_Language_Setting_02'
        self.assertEqual(source.count(original_id), 1)
        altered = source.replace(original_id, b'NS1_Mobile_Option_Language_Setting_XX')
        with self.assertRaisesRegex(ValueError, 'Language choices not found'):
            rename_language_choices(altered)

    def test_mission_title_uses_french_resource_path_with_english_texture(self):
        apk = Path(__file__).resolve().parents[1] / 'origin/Ultimate-Ninja-Storm-1.2.10.apk'
        inventory, unpack = module('inventory-cpk'), module('extract-cpk-files')
        path = 'data/adv_title/main/eng/pm01subt.xfbin'
        bank = next(b for b in inventory.inventory(apk) if any(r['path'] == path for r in b['files']))
        rows = {r['path']: r for r in bank['files']}
        english = read_entry(apk, bank['member'], rows[path], unpack)
        french = read_entry(apk, bank['member'], rows[path.replace('/eng/', '/fre/')], unpack)
        result = adapt_resource_paths(english, french)
        old = b'x/adv_title/main/eng/pm01subt_b.nut'
        new = b'x/adv_title/main/fre/pm01subt_b.nut'
        self.assertEqual(english.count(old), 1)
        self.assertEqual(result, english.replace(old, new))
        self.assertIn(new, french)

    def test_unmatched_mission_title_path_is_rejected(self):
        apk = Path(__file__).resolve().parents[1] / 'origin/Ultimate-Ninja-Storm-1.2.10.apk'
        inventory, unpack = module('inventory-cpk'), module('extract-cpk-files')
        path = 'data/adv_title/main/eng/pm01subt.xfbin'
        bank = next(b for b in inventory.inventory(apk) if any(r['path'] == path for r in b['files']))
        rows = {r['path']: r for r in bank['files']}
        english = read_entry(apk, bank['member'], rows[path], unpack)
        with self.assertRaisesRegex(ValueError, 'French resource path'):
            adapt_resource_paths(english, english)


if __name__ == '__main__':
    unittest.main()
