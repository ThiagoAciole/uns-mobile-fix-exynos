"""Unit tests for the 1280 -> 1720 widescreen backdrop XFBIN patcher."""
import importlib.util
from pathlib import Path
import struct
import unittest

import sys
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from xfbin_messages import chunks

spec = importlib.util.spec_from_file_location("patch_xfbins", HERE / "patch-widescreen-xfbins.py")
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)

CANONICAL_DIR = HERE.parent / "work/s24-coverage/canonical-xfbins"


class WidescreenXfbinTests(unittest.TestCase):
    def test_sprite_backdrops_widen_to_1720_and_reject_reapply(self):
        for rel_path, (_, target_name, _, _, after_verts) in patcher.SPRITE_TARGETS.items():
            source = (CANONICAL_DIR / rel_path).read_bytes()
            output, info = patcher.patch_sprite_xfbin(rel_path, source)
            self.assertEqual(len(output), len(source))
            self.assertEqual(info["logicalWidth"], 1720)
            self.assertLessEqual(info["changedBytes"], 16)
            for off, sz, kind, name in chunks(output):
                if kind == "nuccChunkSprite" and name == target_name:
                    verts = struct.unpack_from(">8h", output, off + 12 + 0x2A)
                    self.assertEqual(verts, after_verts)
                    self.assertEqual(verts[2] - verts[0], 1720)
            with self.assertRaises(ValueError):
                patcher.patch_sprite_xfbin(rel_path, output)
            with self.assertRaises(ValueError):
                patcher.patch_sprite_xfbin(rel_path, source[:-1])

    def test_model_backdrops_widen_to_1720_and_reject_reapply(self):
        for rel_path, (_, specs) in patcher.MODEL_TARGETS.items():
            source = (CANONICAL_DIR / rel_path).read_bytes()
            output, info = patcher.patch_model_xfbin(rel_path, source)
            self.assertEqual(len(output), len(source))
            self.assertEqual(info["logicalWidth"], 1720)
            for off, sz, kind, name in chunks(output):
                if kind == "nuccChunkModel" and name in specs:
                    _, _, vertex_at, vcount, _, half_h, _ = specs[name]
                    bounds = struct.unpack_from(">6f", output, off + 12 + 0x1C)
                    self.assertEqual(bounds, (-860.0, -half_h, 0.0, 860.0, half_h, 0.0))
                    xs = [struct.unpack_from(">f", output, off + 12 + vertex_at + i * 28)[0] for i in range(vcount)]
                    self.assertAlmostEqual(min(xs), -860.0, places=3)
                    self.assertAlmostEqual(max(xs), 860.0, places=3)
            with self.assertRaises(ValueError):
                patcher.patch_model_xfbin(rel_path, output)
            with self.assertRaises(ValueError):
                patcher.patch_model_xfbin(rel_path, source[:-1])


if __name__ == "__main__":
    unittest.main()

