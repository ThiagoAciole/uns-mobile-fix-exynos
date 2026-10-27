"""Focused host proof for the widescreen-compatible controller diagnostic."""
import importlib.util
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


class FlowDiagnosticTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('flow_diag', ROOT / 'scripts/patch-controls-flow-diag.py')
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)
        with zipfile.ZipFile(ROOT / 'build/UNSM-S24-FIX-PTBR-EN-v2.apk') as apk:
            cls.source = apk.read('lib/arm64-v8a/libultimateninjastorm.so')

    def test_diagnostic_preserves_widescreen_and_only_changes_declared_ranges(self):
        result, manifest = self.module.build_diagnostic(self.source, self.module.DEFAULT_LLVM)
        self.assertEqual(len(result), len(self.source))
        self.assertEqual(result[:0x270], self.source[:0x270])
        self.assertEqual(result[0x9B12BC - 0x4000:0x9B134C - 0x4000],
                         self.source[0x9B12BC - 0x4000:0x9B134C - 0x4000])
        self.assertLessEqual(manifest['caveBytes'], 0x110)
        self.assertEqual(set(manifest['symbols']), {'flow_event', 'flow_data'})
        self.assertIn(b'event ret=%d src=%x dev=%d', result)
        self.assertIn(b'data ret=%d slot=%d buttons=%x', result)
        restored = bytearray(result)
        for patch in manifest['patches']:
            offset = patch['offset']
            before = bytes.fromhex(patch['before'])
            self.assertEqual(restored[offset:offset + len(before)].hex(), patch['after'])
            restored[offset:offset + len(before)] = before
        self.assertEqual(bytes(restored), self.source)
        self.assertEqual(self.module.sha(result), manifest['outputSha256'])

    def test_wrong_binary_and_already_patched_input_are_rejected(self):
        invalid = bytearray(self.source)
        invalid[0x1000] ^= 1
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.module.build_diagnostic(bytes(invalid), self.module.DEFAULT_LLVM)
        result, _ = self.module.build_diagnostic(self.source, self.module.DEFAULT_LLVM)
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            self.module.build_diagnostic(result, self.module.DEFAULT_LLVM)

    def test_gamepad_candidate_keeps_shared_constant_and_has_separate_init_hook(self):
        result, manifest = self.module.build_diagnostic(self.source, self.module.DEFAULT_LLVM,
                                                       enable_gamepad=True)
        self.assertTrue(manifest['enableGamepad'])
        self.assertEqual(manifest['inputMaskChange'], {'before': '0x22', 'after': '0x23'})
        self.assertEqual(result[0x66D2E8:0x66D2F0], self.source[0x66D2E8:0x66D2F0])
        self.assertLessEqual(manifest['caveBytes'], 0x110)
        restored = bytearray(result)
        init = [patch for patch in manifest['patches'] if patch['elfVa'] == '0xceefd4']
        self.assertEqual(len(init), 1)
        self.assertEqual(init[0]['before'], '004101fc')
        # This is a jump, not a call: LR must remain untouched at the inline site.
        word = int.from_bytes(bytes.fromhex(init[0]['after']), 'little')
        self.assertEqual(word >> 26, 0b000101)
        hook = int(manifest['symbols']['gamepad_enable'], 16) - 0x4000
        # The original 64-bit parameter store must execute before setting bit 0.
        self.assertEqual(result[hook:hook + 4], bytes.fromhex('004101fc'))
        for patch in manifest['patches']:
            before = bytes.fromhex(patch['before'])
            restored[patch['offset']:patch['offset'] + len(before)] = before
        self.assertEqual(bytes(restored), self.source)

    def test_existing_output_is_preserved_and_build_destination_is_rejected(self):
        command = [sys.executable, '-B', str(ROOT / 'scripts/patch-controls-flow-diag.py'),
                   '--apk', str(ROOT / 'build/UNSM-S24-FIX-PTBR-EN-v2.apk')]
        with tempfile.TemporaryDirectory(prefix='storm-flow-test-') as folder:
            output = Path(folder) / 'existing.so'
            output.write_bytes(b'preserve this artifact')
            process = subprocess.run(command + ['--output', str(output)], capture_output=True)
            self.assertNotEqual(process.returncode, 0)
            self.assertIn(b'FileExistsError', process.stderr)
            self.assertEqual(output.read_bytes(), b'preserve this artifact')
            self.assertFalse(Path(str(output) + '.patch.json').exists())
        process = subprocess.run(command + ['--output', str(ROOT / 'build/flow-test.so')], capture_output=True)
        self.assertEqual(process.returncode, 2)
        self.assertFalse((ROOT / 'build/flow-test.so').exists())

    def test_usage_candidate_has_no_logging_and_leaves_event_and_data_calls_original(self):
        result, manifest = self.module.build_diagnostic(self.source, self.module.DEFAULT_LLVM,
                                                       enable_gamepad=True, flow_logs=False)
        self.assertEqual(set(manifest['symbols']), {'gamepad_enable'})
        self.assertFalse(manifest['flowLogs'])
        self.assertEqual(manifest['caveBytes'], 28)
        self.assertNotIn(b'CTRLFLOW', result)
        for va in [0x9E7D40, 0x931670]:
            offset = va - 0x4000
            self.assertEqual(result[offset:offset + 4], self.source[offset:offset + 4])
        self.assertEqual(len(manifest['patches']), 2)
        restored = bytearray(result)
        for patch in manifest['patches']:
            before = bytes.fromhex(patch['before'])
            restored[patch['offset']:patch['offset'] + len(before)] = before
        self.assertEqual(bytes(restored), self.source)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]], verbosity=2)
