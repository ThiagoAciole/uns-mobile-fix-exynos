"""Ciclo de vida da apresentacao ABXY na selecao, com adaptador de host."""
import ctypes
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'patches/controls-diag/abxy-select.c'


class AbxySelectTests(unittest.TestCase):
    def test_connection_binding_visibility_and_owner_lifecycle(self):
        self.assertTrue(SOURCE.is_file(), 'A atualizacao nativa da selecao ainda nao foi implementada')
        compiler = shutil.which('gcc')
        if compiler is None:
            self.skipTest('Compilador C de host indisponivel')
        with tempfile.TemporaryDirectory(prefix='storm-abxy-select-') as folder:
            dll = Path(folder) / 'select.dll'
            subprocess.run([compiler, '-shared', '-O2', '-Wl,--export-all-symbols', '-o', str(dll),
                            str(SOURCE), str(ROOT / 'patches/controls-diag/abxy-mapping.c'),
                            str(ROOT / 'tests/controls/abxy_select_test_shim.c')],
                           check=True, capture_output=True)
            library = ctypes.CDLL(str(dll))
            try:
                for name in ('mock_set_pad', 'mock_release'):
                    getattr(library, name).argtypes = [ctypes.c_size_t]
                library.mock_show.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
                library.mock_fail_create.argtypes = [ctypes.c_uint32]
                library.mock_update.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
                for name in ('mock_drawn_id', 'mock_drawn_slot'):
                    getattr(library, name).argtypes = [ctypes.c_uint32]
                    getattr(library, name).restype = ctypes.c_uint32
                library.mock_reset()
                library.mock_set_pad(0x900000)
                library.mock_show(0, 1)
                library.mock_show(1, 1)
                library.mock_stage_update.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
                library.mock_stage_update(0, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                library.mock_stage_update(1, 0x4000)
                self.assertEqual([(library.mock_drawn_slot(i), library.mock_drawn_id(i)) for i in range(2)], [(0, 0x10), (1, 0x0f)])
                library.mock_stage_update(0, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                library.mock_release(0x900000)
                self.assertEqual(library.mock_releases(), 2)
                library.mock_reset()
                library.mock_set_pad(0x100000)
                library.mock_show(0, 1)
                library.mock_show(2, 1)
                library.mock_update(0, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                self.assertEqual(library.mock_creates(), 0)
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_draws(), 2)
                self.assertEqual([(library.mock_drawn_slot(i), library.mock_drawn_id(i)) for i in range(2)],
                                 [(0, 0x0f), (2, 0x10)])
                self.assertEqual(library.mock_creates(), 2)
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_creates(), 2)
                library.mock_update(1, 0x8000)
                self.assertEqual(library.mock_drawn_id(1), 0x11)
                self.assertEqual(library.mock_releases(), 1)
                library.mock_update(0, 0x8000)
                self.assertEqual(library.mock_draws(), 0)
                library.mock_update(1, 0)
                self.assertEqual(library.mock_draws(), 1)
                library.mock_set_pad(0x200000)
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_draws(), 2)
                self.assertGreaterEqual(library.mock_releases(), 2)
                library.mock_release(0x200000)
                self.assertGreaterEqual(library.mock_releases(), 4)
                library.mock_reset()
                library.mock_set_pad(0x300000)
                library.mock_show(0, 1)
                library.mock_show(3, 1)
                library.mock_fail_create(1)
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                self.assertEqual(library.mock_creates(), 2)
                library.mock_fail_create(0)
                library.mock_update(1, 0x4000)
                self.assertEqual([(library.mock_drawn_slot(i), library.mock_drawn_id(i)) for i in range(2)],
                                 [(0, 0x0f), (3, 0x10)])
                library.mock_release(0x400000)
                self.assertEqual(library.mock_releases(), 0)
                library.mock_update(2, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                library.mock_release(0x300000)
                self.assertEqual(library.mock_releases(), 2)
                library.mock_reset()
                library.mock_set_pad(0x500000)
                for slot in (0, 2, 3):
                    library.mock_show(slot, 1)
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_draws(), 3)
                self.assertEqual(library.mock_creates(), 3, 'Cada botao visivel precisa de sprite proprio')
                library.mock_update(1, 0x8000)
                self.assertEqual(library.mock_releases(), 2)
                library.mock_release(0x500000)
                library.mock_reset()
                library.mock_set_pad(0x600000)
                library.mock_show(1, 1)
                library.mock_update(0, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                self.assertEqual(library.mock_font_creates(), 0)
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_draws(), 1, 'Start deve acompanhar o botao de configuracoes')
                self.assertEqual((library.mock_drawn_slot(0), library.mock_drawn_id(0)), (1, 0x100))
                library.mock_update(1, 0x4000)
                self.assertEqual(library.mock_font_creates(), 1)
                library.mock_update(0, 0x4000)
                self.assertEqual(library.mock_draws(), 0)
                library.mock_release(0x600000)
                self.assertEqual(library.mock_font_releases(), 1)
            finally:
                import _ctypes
                _ctypes.FreeLibrary(library._handle)
                library._handle = 0


if __name__ == '__main__':
    unittest.main()
