"""Regression checks for the last24 incremental composition patch."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


patcher = load('composition_patch', ROOT / 'scripts/patch-widescreen-composition.py')


class CompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = (ROOT / 'work/restore-20261024/transform-audit/installed.so').read_bytes()
        cls.output, cls.manifest = patcher.patch(cls.source)

    def test_only_two_instructions_change(self):
        start = 0x1079910 - 0x4000
        self.assertEqual(len(self.source), len(self.output))
        self.assertEqual(self.output[:start], self.source[:start])
        self.assertEqual(self.output[start + 8:], self.source[start + 8:])
        self.assertEqual(self.output[start:start + 8], bytes.fromhex('e103142ae203042a'))
        self.assertEqual(self.output[0x9b12c0 - 0x4000:0x9b134c - 0x4000],
                         self.source[0x9b12c0 - 0x4000:0x9b134c - 0x4000])
        self.assertEqual(self.output[0xa89f58 - 0x4000:0xa89f5c - 0x4000],
                         self.source[0xa89f58 - 0x4000:0xa89f5c - 0x4000])

    def test_wrong_source_and_reapply_rejected(self):
        for data in (b'bad ELF', self.source[:-1], self.output):
            with self.assertRaises(ValueError):
                patcher.patch(data)

    def test_actual_patched_tail_composes_at_zero(self):
        emulator = load('composition_replay', ROOT / 'work/widescreen-composition-analysis/emulate_composition.py')
        emulator.DATA = self.output
        result = emulator.run_case('generated ELF composition', (0, 0), change_tail='installed')
        self.assertEqual(result['setRenderModeW1ThroughW7'], [2340, 1080, 2340, 1080, 1, 0, 0])
        self.assertEqual(result['resolution']['destination'], [0, 0, 2340, 1080])
        self.assertEqual(result['observed']['spriteFloats'][0], 0)
        self.assertEqual(result['observed']['spriteFloats'][6:8], [2340, 1080])


if __name__ == '__main__':
    unittest.main()
