"""Focused checks against the extracted, exact current native input."""
import importlib.util
from pathlib import Path
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('coverage_patch', HERE / 'patch-s24-coverage.py')
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)


class CoverageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (HERE.parent / 'work/s24-composition/patched/libultimateninjastorm.so').read_bytes()
        cls.output, cls.info = patcher.patch(cls.source)

    def test_only_declared_ranges_change(self):
        allowed = set()
        for entry in self.info['patches']:
            allowed.update(range(entry['offset'], entry['offset'] + len(bytes.fromhex(entry['after']))))
        changed = {i for i, (a, b) in enumerate(zip(self.source, self.output)) if a != b}
        self.assertTrue(changed)
        self.assertLessEqual(changed, allowed)
        self.assertEqual(len(self.output), len(self.source))
        self.assertEqual(self.source[0x9b12bc-0x4000:0x9b134c-0x4000],
                         self.output[0x9b12bc-0x4000:0x9b134c-0x4000])
        self.assertEqual(self.source[0x6bf964:0x6bf968], self.output[0x6bf964:0x6bf968])

    def test_wrong_source_and_reapply_rejected(self):
        for data in (self.output, self.source[:-1], b'bad ELF'):
            with self.assertRaises(ValueError):
                patcher.patch(data)

    def test_s24_edges_and_existing_16_9_mapping(self):
        for width, height, left, right in (
                (1920, 1080, 0, 1280),
                (2340, 1080, -140, 1420),
                (2560, 1080, -213.3333333333, 1493.3333333333)):
            scale = height / 720
            self.assertAlmostEqual(width / 2 + (left - 640) * scale, 0, places=6)
            self.assertAlmostEqual(width / 2 + (right - 640) * scale, width, places=6)
        self.assertEqual(self.source[0xc96a2c-0x4000:0xc96a30-0x4000], bytes.fromhex('2c6af417'))
        self.assertEqual(self.output[0xc96a2c-0x4000:0xc96a30-0x4000], bytes.fromhex('2c6af417'))
        branch_word = int.from_bytes(bytes.fromhex('2c6af417'), 'little')
        branch_delta = branch_word & 0x03ffffff
        if branch_delta & (1 << 25):
            branch_delta -= 1 << 26
        self.assertEqual(0xc96a2c + (branch_delta << 2), 0x9b12dc)
        self.assertNotIn('ui_center', self.info['symbols'])
        self.assertLessEqual(self.info['caveBytes'], 0x9b145c - 0x9b134c)

    def test_start_menu_layer_expands_to_full_logical_width(self):
        self.assertEqual(self.source[0xa7d73c-0x4000:0xa7d740-0x4000], bytes.fromhex('01e4002f'))
        patched = self.output[0xa7d73c-0x4000:0xa7d740-0x4000]
        branch_word = int.from_bytes(patched, 'little')
        branch_delta = branch_word & 0x03ffffff
        if branch_delta & (1 << 25):
            branch_delta -= 1 << 26
        self.assertEqual(0xa7d73c + (branch_delta << 2),
                         int(self.info['symbols']['startmenu_layer'], 16))
        self.assertEqual(self.output[0xa7d740-0x4000:0xa7d744-0x4000],
                         self.source[0xa7d740-0x4000:0xa7d744-0x4000])
        self.assertAlmostEqual(2340 / (1080 / 720), 1560)
        self.assertAlmostEqual(640 - 1560 / 2, -140)


if __name__ == '__main__':
    unittest.main()
