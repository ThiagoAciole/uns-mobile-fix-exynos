"""Valida a composicao do candidato nativo de selecao, sem gerar APK."""
import importlib.util
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'scripts/patch-controls-select-prompts.py'
SOURCE = ROOT / 'work/controls-console-ui-20261027/libultimateninjastorm-console-hud-candidate-v2.so'


class AbxySelectPatchTests(unittest.TestCase):
    def test_cli_preserves_existing_output_and_rejects_build_destination(self):
        self.assertTrue(SCRIPT.is_file())
        if not SOURCE.is_file():
            self.skipTest('Biblioteca F1.1 local ausente')
        with tempfile.TemporaryDirectory(prefix='storm-select-output-test-') as folder:
            output = Path(folder) / 'existing.so'
            output.write_bytes(b'preserve')
            command = [sys.executable, '-B', str(SCRIPT), '--input', str(SOURCE)]
            process = subprocess.run(command + ['--output', str(output)], capture_output=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn(b'existente', process.stderr)
            self.assertEqual(output.read_bytes(), b'preserve')
            self.assertFalse(Path(str(output) + '.patch.json').exists())
            process = subprocess.run(command + ['--output', str(ROOT / 'build/forbidden-f12.so')],
                                     capture_output=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn(b'fora de build', process.stderr)
            self.assertFalse((ROOT / 'build/forbidden-f12.so').exists())
            fresh = Path(folder) / 'fresh.so'
            process = subprocess.run(command + ['--output', str(fresh)], capture_output=True)
            self.assertEqual(process.returncode, 0, process.stderr.decode(errors='replace'))
            report = json.loads(Path(str(fresh) + '.patch.json').read_text(encoding='utf-8'))
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), report['outputSha256'])
            self.assertEqual(report['status'], 'host-only-experimental-select-prompts-not-device-tested')

    def test_build_is_guarded_reversible_and_keeps_f11_patches(self):
        self.assertTrue(SCRIPT.is_file(), 'O patch nativo de selecao ainda nao foi implementado')
        if not SOURCE.is_file():
            self.skipTest('Biblioteca F1.1 local ausente')
        spec = importlib.util.spec_from_file_location('select_patch', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if not (module.DEFAULT_LLVM / 'clang.exe').is_file():
            self.skipTest('NDK 27.2 indisponivel')
        data = SOURCE.read_bytes()
        manifest = json.loads(Path(str(SOURCE) + '.patch.json').read_text(encoding='utf-8'))
        result, report = module.build_patch(data, manifest, module.DEFAULT_LLVM)
        self.assertEqual(len(result), len(data) + 0x4000)
        self.assertEqual(report['inputLibrarySha256'], module.SOURCE_SHA256)
        self.assertEqual(report['status'], 'host-only-experimental-select-prompts-not-device-tested')
        self.assertEqual(len(report['patches']), 4)
        expanded, layout = module.extender.reserve_executable_space(data)
        restored = bytearray(result)
        for item in report['patches']:
            offset = int(item['elfVa'], 16) - 0x4000
            before, after = bytes.fromhex(item['before']), bytes.fromhex(item['after'])
            self.assertEqual(restored[offset:offset + len(after)], after)
            target = module.extender.direct_branch_target(struct.unpack('<I', after)[0], int(item['elfVa'], 16))
            self.assertEqual(target, int(item['targetVa'], 16))
            restored[offset:offset + len(before)] = before
        start = layout['code_offset']
        restored[start:start + report['payloadBytes']] = bytes(report['payloadBytes'])
        self.assertEqual(bytes(restored), expanded)
        # Existing gamepad and HUD caves and hook are untouched.
        for va, size in ((0x9b134c, 84), (0x9f26a4, 4)):
            offset = va - 0x4000
            self.assertEqual(result[offset:offset + size], data[offset:offset + size])
        invalid = bytearray(data)
        invalid[0x1000] ^= 1
        with self.assertRaises(ValueError):
            module.build_patch(bytes(invalid), manifest, module.DEFAULT_LLVM)
        with self.assertRaises(ValueError):
            module.build_patch(data, {}, module.DEFAULT_LLVM)
        with self.assertRaises(ValueError):
            module.build_patch(result, manifest, module.DEFAULT_LLVM)


if __name__ == '__main__':
    unittest.main()
