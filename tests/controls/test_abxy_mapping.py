"""Valida a conversao de mascaras para sprites ABXY usados pelo patch nativo."""
import ctypes
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'patches/controls-diag/abxy-mapping.c'


class AbxyMappingTests(unittest.TestCase):
    def test_active_controller_maps_all_four_faces_and_rejects_ambiguous_input(self):
        self.assertTrue(SOURCE.is_file(), 'O mapeamento nativo ABXY ainda nao foi implementado')
        compiler = shutil.which('gcc')
        if compiler is None:
            self.skipTest('Compilador C de host indisponivel')
        with tempfile.TemporaryDirectory(prefix='storm-abxy-test-') as folder:
            library_path = Path(folder) / 'abxy.dll'
            subprocess.run([compiler, '-shared', '-O2', '-Wl,--export-all-symbols',
                            '-o', str(library_path), str(SOURCE)], check=True, capture_output=True)
            library = ctypes.CDLL(str(library_path))
            try:
                resolve = library.abxy_icon_for_mask
                resolve.argtypes = [ctypes.c_uint32, ctypes.c_uint32]
                resolve.restype = ctypes.c_uint32
                expected = {0x4000: 0x10, 0x2000: 0x12, 0x8000: 0x11, 0x1000: 0x0f}
                for mask in range(0x10000):
                    self.assertEqual(resolve(mask, 1), expected.get(mask, 0), hex(mask))
                for mask in (*expected, 0x10000, 0xffffffff):
                    self.assertEqual(resolve(mask, 0), 0)
                    self.assertEqual(resolve(mask, 2), 0)
            finally:
                # Windows does not permit deleting a loaded DLL; unload explicitly.
                import _ctypes
                _ctypes.FreeLibrary(library._handle)
                library._handle = 0

    def test_arm64_payload_links_without_external_relocations(self):
        bin_dir = (Path(os.environ.get('LOCALAPPDATA', '')) / 'Android/Sdk/ndk/27.2.12479018'
                   / 'toolchains/llvm/prebuilt/windows-x86_64/bin')
        clang, linker = bin_dir / 'clang.exe', bin_dir / 'ld.lld.exe'
        readelf, objcopy = bin_dir / 'llvm-readelf.exe', bin_dir / 'llvm-objcopy.exe'
        if not all(tool.is_file() for tool in (clang, linker, readelf, objcopy)):
            self.skipTest('NDK 27.2 indisponivel')
        with tempfile.TemporaryDirectory(prefix='storm-abxy-arm64-') as folder:
            obj, elf, raw = (Path(folder) / name for name in ('abxy.o', 'abxy.elf', 'abxy.bin'))
            subprocess.run([str(clang), '--target=aarch64-linux-android28', '-ffreestanding',
                            '-fno-stack-protector', '-fno-jump-tables', '-Os', '-c', str(SOURCE),
                            '-o', str(obj)], check=True, capture_output=True)
            subprocess.run([str(linker), '-Ttext=0x13188c0', '--entry=abxy_icon_for_mask',
                            '--no-undefined', str(obj), '-o', str(elf)], check=True, capture_output=True)
            result = subprocess.run([str(readelf), '-r', str(elf)], check=True,
                                    capture_output=True, text=True)
            self.assertIn('There are no relocations', result.stdout)
            subprocess.run([str(objcopy), '-O', 'binary', '--only-section=.text', str(elf), str(raw)],
                           check=True, capture_output=True)
            self.assertGreater(raw.stat().st_size, 0)
            self.assertLessEqual(raw.stat().st_size, 0x3740)


if __name__ == '__main__':
    unittest.main()
