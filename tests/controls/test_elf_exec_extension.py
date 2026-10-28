"""Verifica a reserva de espaco executavel na biblioteca F1.1, sem gravar APK."""
import importlib.util
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts' / 'extend-controls-elf.py'
SOURCE = ROOT / 'work/controls-console-ui-20261027/libultimateninjastorm-console-hud-candidate-v2.so'


def segments(data):
    offset = struct.unpack_from('<Q', data, 32)[0]
    size, count = struct.unpack_from('<HH', data, 54)
    return [struct.unpack_from('<IIQQQQQQ', data, offset + index * size)
            for index in range(count)]


def sections(data):
    offset = struct.unpack_from('<Q', data, 40)[0]
    size, count = struct.unpack_from('<HH', data, 58)
    return [struct.unpack_from('<IIQQQQIIQQ', data, offset + index * size)
            for index in range(count)]


class ExecutableExtensionTests(unittest.TestCase):
    def test_direct_branch_decoding_covers_conditional_and_unconditional_forms(self):
        self.assertTrue(SCRIPT.is_file())
        spec = importlib.util.spec_from_file_location('extend_controls_elf', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, 'direct_branch_target'), 'Decodificador de branches ausente')
        for word in (0x14000001, 0x94000001, 0x54000020, 0x34000020, 0x36000020):
            self.assertEqual(module.direct_branch_target(word, 0x1000), 0x1004, hex(word))
        self.assertEqual(module.direct_branch_target(0x17ffffff, 0x1000), 0xffc)
        self.assertIsNone(module.direct_branch_target(0xd65f03c0, 0x1000))

    def test_extension_preserves_load_segments_and_rejects_untrusted_inputs(self):
        self.assertTrue(SCRIPT.is_file(), 'O extensor ELF ainda nao foi implementado')
        if not SOURCE.is_file():
            self.skipTest('Biblioteca F1.1 local ausente')
        spec = importlib.util.spec_from_file_location('extend_controls_elf', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        source = SOURCE.read_bytes()
        output, layout = module.reserve_executable_space(source)
        self.assertEqual(layout['code_va'], 0x13188c0)
        self.assertEqual(layout['code_capacity'], 0x3740)
        self.assertIn('scratch_va', layout, 'Reserva gravavel ainda nao implementada')
        self.assertEqual(layout['scratch_va'], 0x1566390)
        self.assertEqual(layout['scratch_capacity'], 0x400)
        self.assertEqual(len(output), len(source) + 0x4000)
        self.assertEqual(output[0x318:0x328], source[0x318:0x328])
        before, after = segments(source), segments(output)
        self.assertEqual(len(before), len(after))
        for old, new in zip(before, after):
            self.assertEqual(old[0:2], new[0:2])
            self.assertEqual(old[3:5], new[3:5])
            self.assertEqual(old[7], new[7])
            self.assertEqual(new[2], old[2] + (0x4000 if old[2] >= 0x13148c0 else 0))
            if old[0] != 1:
                self.assertEqual(old[5:7], new[5:7])
                continue
            self.assertEqual(new[2] % new[7], new[3] % new[7])
            # ELF header and program headers must change to describe the new layout.
            skip = 0x270 if old[2] == 0 else 0
            self.assertEqual(source[old[2] + skip:old[2] + old[5]],
                             output[new[2] + skip:new[2] + old[5]])
        self.assertEqual(after[2][3] + after[2][6], after[3][3] & ~0x3fff)
        self.assertGreaterEqual(after[4][3] + after[4][6], layout['scratch_va'] + layout['scratch_capacity'])
        for old, new in zip(sections(source), sections(output)):
            self.assertEqual(old[:4], new[:4])
            self.assertEqual(old[5:], new[5:])
            self.assertEqual(new[4], old[4] + (0x4000 if old[4] >= 0x13148c0 else 0))
        self.assertEqual(output[layout['code_offset']:layout['code_offset'] + layout['code_capacity']],
                         bytes(layout['code_capacity']))
        changed = bytearray(source)
        changed[0x1000] ^= 1
        with self.assertRaises(ValueError):
            module.reserve_executable_space(bytes(changed))
        with self.assertRaises(ValueError):
            module.reserve_executable_space(source[:-1])


if __name__ == '__main__':
    unittest.main()
