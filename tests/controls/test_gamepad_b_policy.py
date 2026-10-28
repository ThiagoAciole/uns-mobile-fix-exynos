import sys
import importlib.util
import json
import struct
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]

class GamepadBPolicyTests(unittest.TestCase):
    def test_only_gamepad_button_b_is_consumed(self):
        with tempfile.TemporaryDirectory(prefix='storm-b-policy-') as folder:
            output = Path(folder) / 'policy.dll'
            compiler = Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/windows-x86_64/bin/clang.exe'
            subprocess.run([str(compiler), '-shared', '-o', str(output), str(ROOT / 'patches/controls-diag/gamepad-b-policy.c')], check=True, capture_output=True)
            program = """import ctypes, sys
f = ctypes.CDLL(sys.argv[1]).controller_b_handled
f.argtypes = [ctypes.c_int] * 4
f.restype = ctypes.c_int
for values, expected in [((1,0x401,97,0),1), ((1,0x501,97,0),1), ((1,0x101,97,0),0), ((1,0x401,96,0),0), ((2,0x401,97,0),0), ((1,0x101,4,1),1)]:
    assert f(*values) == expected, values
"""
            subprocess.run([sys.executable, '-c', program, str(output)], check=True, capture_output=True)


    def test_two_finish_calls_are_patched_and_input_guarded(self):
        spec = importlib.util.spec_from_file_location('b_patch', ROOT / 'scripts/patch-controls-gamepad-b.py')
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        source = ROOT / 'work/controls-console-ui-20261027/libultimateninjastorm-console-hud-candidate-v2.so'
        data = source.read_bytes()
        manifest = json.loads(Path(str(source) + '.patch.json').read_text(encoding='utf-8-sig'))
        patched, report = mod.compose(data, manifest, mod.select.DEFAULT_LLVM)
        target = int(report['hookVa'], 16)
        for item in report['patches']:
            va = int(item['elfVa'], 16)
            word = struct.unpack('<I', bytes.fromhex(item['after']))[0]
            self.assertEqual(word >> 26, 0b100101)
            self.assertEqual(mod.select.extender.direct_branch_target(word, va), target)
            self.assertEqual(patched[va - 0x4000:va - 0x4000 + 4].hex(), item['after'])
        self.assertEqual(len(report['patches']), 2)
        damaged = bytearray(data)
        damaged[0x1000] ^= 1
        with self.assertRaises(ValueError):
            mod.compose(bytes(damaged), manifest, mod.select.DEFAULT_LLVM)

    def test_existing_output_is_preserved(self):
        source = ROOT / 'work/controls-console-ui-20261027/libultimateninjastorm-console-hud-candidate-v2.so'
        with tempfile.TemporaryDirectory(prefix='storm-b-output-') as folder:
            output = Path(folder) / 'existing.so'
            output.write_bytes(b'preserve')
            result = subprocess.run([sys.executable, str(ROOT / 'scripts/patch-controls-gamepad-b.py'), '--input', str(source), '--output', str(output)], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_bytes(), b'preserve')
            self.assertFalse(Path(str(output) + '.patch.json').exists())

if __name__ == '__main__':
    unittest.main()
