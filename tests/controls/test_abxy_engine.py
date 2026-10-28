"""Confere o adaptador nativo de sprite e posicao dos botoes Android."""
import ctypes
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'patches/controls-diag/abxy-select-engine.c'


class AbxyEngineTests(unittest.TestCase):
    def test_draw_uses_live_text_anchor_and_skips_missing_coordinates(self):
        self.assertTrue(SOURCE.is_file(), 'O adaptador nativo da selecao ainda nao foi implementado')
        compiler = shutil.which('gcc')
        if compiler is None:
            self.skipTest('Compilador C de host indisponivel')
        with tempfile.TemporaryDirectory(prefix='storm-abxy-engine-') as folder:
            dll = Path(folder) / 'engine.dll'
            subprocess.run([compiler, '-shared', '-O2', '-Wl,--export-all-symbols', '-o', str(dll),
                            str(SOURCE), str(ROOT / 'tests/controls/abxy_engine_test_shim.c')],
                           check=True, capture_output=True)
            lib = ctypes.CDLL(str(dll))
            try:
                lib.mock_engine_button.restype = ctypes.c_void_p
                lib.mock_engine_coordinates.argtypes = [ctypes.c_float, ctypes.c_float]
                lib.abxy_game_draw_at_button.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
                for name in ('mock_engine_x', 'mock_engine_y', 'mock_engine_scale_x', 'mock_engine_scale_y'):
                    getattr(lib, name).restype = ctypes.c_float
                lib.mock_engine_reset()
                button = lib.mock_engine_button()
                lib.abxy_game_draw_at_button(1, button)
                self.assertEqual(lib.mock_engine_draws(), 0)
                lib.mock_engine_coordinates(125.0, 250.0)
                lib.abxy_game_draw_at_button(1, button)
                self.assertEqual(lib.mock_engine_draws(), 1)
                self.assertAlmostEqual(lib.mock_engine_x(), 125.0)
                self.assertAlmostEqual(lib.mock_engine_y(), 222.0)
                self.assertAlmostEqual(lib.mock_engine_scale_x(), 0.5)
                self.assertAlmostEqual(lib.mock_engine_scale_y(), 0.5)
                self.assertTrue(hasattr(lib, 'abxy_game_create_start_font'), 'Adaptador de fonte START ausente')
                lib.abxy_game_create_start_font.restype = ctypes.c_void_p
                lib.abxy_game_draw_start_at_button.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
                lib.mock_font_text.restype = ctypes.c_char_p
                lib.mock_font_x.restype = lib.mock_font_y.restype = ctypes.c_float
                font = lib.abxy_game_create_start_font()
                self.assertEqual(lib.mock_font_text(), b'START')
                lib.abxy_game_draw_start_at_button(font, button)
                self.assertEqual(lib.mock_font_draws(), 1)
                self.assertAlmostEqual(lib.mock_font_x(), 125.0)
                self.assertAlmostEqual(lib.mock_font_y(), 222.0)
            finally:
                import _ctypes
                _ctypes.FreeLibrary(lib._handle)
                lib._handle = 0


if __name__ == '__main__':
    unittest.main()
