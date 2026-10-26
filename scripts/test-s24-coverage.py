"""Focused checks for edge-to-edge responsive widescreen HUDs/menus + 3D Hor+ FOV."""
import importlib.util
from pathlib import Path
import struct
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('coverage_patch', HERE / 'patch-s24-coverage.py')
patcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(patcher)


def f32(val: float) -> float:
    return struct.unpack('<f', struct.pack('<f', val))[0]


def sim_disp_camera_and_touch(width: int, height: int, ui_x: float, ui_y: float):
    w = f32(float(width))
    h = f32(float(height))
    scale_x = f32(w / f32(1280.0))
    scale_y = f32(h / f32(720.0))
    trans_x = f32(f32(-0.5) * w)
    trans_y = f32(f32(0.5) * h)
    # View X in [-w/2 .. +w/2] -> physical screen X in [0 .. w]
    view_x = f32(f32(ui_x) * scale_x + trans_x)
    phys_x = f32(view_x + f32(0.5) * w)
    view_y = f32(f32(-ui_y) * scale_y + trans_y)
    phys_y = f32(f32(0.5) * h - view_y)
    # ConvertScreenPosToRenderPos maps physical touch back to [0..1280] x [0..720]
    touch_ui_x = f32(phys_x * f32(f32(1280.0) / w))
    touch_ui_y = f32(phys_y * f32(f32(720.0) / h))
    return phys_x, phys_y, touch_ui_x, touch_ui_y


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
        self.assertEqual(self.source[0x6bf964:0x6bf968], self.output[0x6bf964:0x6bf968])

    def test_wrong_source_and_reapply_rejected(self):
        for data in (self.output, self.source[:-1], b'bad ELF'):
            with self.assertRaises(ValueError):
                patcher.patch(data)

    def test_3d_hor_plus_and_native_resolution_preserved(self):
        # AdjustScreenSize RET, SetResolution/ChangeRender native dims, DrawLetterBox RET, 3D Hor+ camera branch
        self.assertEqual(self.output[0xcdbcf4 - 0x4000:0xcdbcf8 - 0x4000], bytes.fromhex('c0035fd6'))
        self.assertEqual(self.output[0xcdbda4 - 0x4000:0xcdbdac - 0x4000], bytes.fromhex('e103142ae203042a'))
        self.assertEqual(self.output[0x1079910 - 0x4000:0x1079918 - 0x4000], bytes.fromhex('e103142ae203042a'))
        self.assertEqual(self.output[0x9b12bc - 0x4000:0x9b12c0 - 0x4000], bytes.fromhex('c0035fd6'))
        self.assertEqual(self.output[0x941ff0 - 0x4000:0x941ff4 - 0x4000], bytes.fromhex('b4bc0114'))

    def test_2d_disp_camera_and_touch_are_edge_to_edge_responsive(self):
        self.assertEqual(self.output[0xc969f8 - 0x4000:0xc969fc - 0x4000], bytes.fromhex('0894a852'))
        self.assertEqual(self.output[0xc96a0c - 0x4000:0xc96a10 - 0x4000], bytes.fromhex('0318221e'))
        self.assertEqual(self.output[0xc96a2c - 0x4000:0xc96a30 - 0x4000], bytes.fromhex('0640211e'))
        self.assertEqual(self.output[0xa89f58 - 0x4000:0xa89f5c - 0x4000], bytes.fromhex('c0035fd6'))
        self.assertEqual(self.output[0x955710 - 0x4000:0x955714 - 0x4000], bytes.fromhex('0018221e'))
        self.assertEqual(self.output[0x955728 - 0x4000:0x95572c - 0x4000], bytes.fromhex('02082b1e'))

        for width, height in ((1920, 1080), (2340, 1080), (2400, 1080), (2560, 1080), (3088, 1440)):
            px_left, py_top, tx_left, ty_top = sim_disp_camera_and_touch(width, height, 0.0, 0.0)
            px_mid, py_mid, tx_mid, ty_mid = sim_disp_camera_and_touch(width, height, 640.0, 360.0)
            px_right, py_bot, tx_right, ty_bot = sim_disp_camera_and_touch(width, height, 1280.0, 720.0)
            self.assertAlmostEqual(px_left, 0.0, places=3)
            self.assertAlmostEqual(px_mid, width * 0.5, places=3)
            self.assertAlmostEqual(px_right, float(width), places=3)
            self.assertAlmostEqual(py_top, 0.0, places=3)
            self.assertAlmostEqual(py_bot, float(height), places=3)
            self.assertAlmostEqual(tx_left, 0.0, places=3)
            self.assertAlmostEqual(tx_mid, 640.0, places=2)
            self.assertAlmostEqual(tx_right, 1280.0, places=2)
            self.assertAlmostEqual(ty_top, 0.0, places=3)
            self.assertAlmostEqual(ty_bot, 720.0, places=2)


if __name__ == '__main__':
    unittest.main()

