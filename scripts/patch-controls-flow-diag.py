"""Diagnostico Paddleboat que preserva a biblioteca S24 widescreen de uso.

Le a biblioteca do APK sem extrair o jogo. Nao gera, assina nem instala APK.
Use --check-only para montar e validar inteiramente em memoria.
--enable-gamepad acrescenta a habilitacao experimental do bit local de controle.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LLVM = Path.home() / 'AppData/Local/Android/Sdk/ndk/27.2.12479018/toolchains/llvm/prebuilt/windows-x86_64/bin'
SOURCE_SHA = '8797e4446449b505bd20d704c4123f4bdbedeec8b9e1e71a87414a876572cfd0'
BUILD_ID = 'c3e506f9be350dfb4a00c79228754028'
NATIVE_MEMBER = 'lib/arm64-v8a/libultimateninjastorm.so'
CAVE = 0x9B134C
CAVE_END = 0x9B145C
VA_DELTA = 0x4000
CALLS = {'flow_event': (0x9E7D40, 0x1314550), 'flow_data': (0x931670, 0x13144F0)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def branch(source, target):
    delta = target - source
    if delta % 4 or not -(1 << 27) <= delta < (1 << 27):
        raise ValueError('Destino BL AArch64 fora do alcance ou desalinhado')
    return struct.pack('<I', 0x94000000 | ((delta // 4) & 0x3FFFFFF))


def verify_cave(data):
    # Read the actual ELF executable LOAD and its VA/file mapping.
    phoff = struct.unpack_from('<Q', data, 32)[0]
    phsize, phnum = struct.unpack_from('<HH', data, 54)
    for index in range(phnum):
        kind, flags, offset, va, _, filesz, _, _ = struct.unpack_from('<IIQQQQQQ', data, phoff + index * phsize)
        if kind != 1 or not flags & 1 or not va <= CAVE < CAVE_END <= va + filesz:
            continue
        if va - offset != VA_DELTA:
            raise ValueError('Mapeamento VA/arquivo inesperado')
        # Reject a direct branch from any live executable address into the cave.
        # Branches wholly inside the dormant tail of DrawLetterBox are irrelevant.
        for position in range(offset, offset + filesz - 3, 4):
            at = va + position - offset
            if CAVE <= at < CAVE_END:
                continue
            word = struct.unpack_from('<I', data, position)[0]
            if word & 0x7C000000 != 0x14000000:
                continue
            immediate = word & 0x3FFFFFF
            if immediate & 0x2000000:
                immediate -= 0x4000000
            if CAVE <= at + immediate * 4 < CAVE_END:
                raise ValueError(f'Branch existente entra na cave: {at:#x}')
        return
    raise ValueError('Cave fora do segmento executavel')


def build_diagnostic(data, llvm_bin, *, enable_gamepad=False, flow_logs=True,
                     source_apk_library_sha256=SOURCE_SHA):
    if not flow_logs and not enable_gamepad:
        raise ValueError('Sem logs, habilite explicitamente o candidato de gamepad')
    if sha(data) != SOURCE_SHA:
        raise ValueError('SHA-256 diferente da biblioteca S24 widescreen esperada')
    if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<H', data, 18)[0] != 183:
        raise ValueError('Esperado ELF64 little-endian AArch64')
    if data[0x318:0x328].hex() != BUILD_ID:
        raise ValueError('Build ID diferente')
    if data[0x9B12BC - VA_DELTA:0x9B12C0 - VA_DELTA] != bytes.fromhex('c0035fd6'):
        raise ValueError('DrawLetterBox nao esta desativada; cave insegura')
    verify_cave(data)

    def run(tool, *args):
        return subprocess.check_output([str(llvm_bin / tool), *map(str, args)], text=True)

    with tempfile.TemporaryDirectory(prefix='storm-controls-flow-') as folder:
        folder = Path(folder)
        obj, elf, binary = folder / 'stubs.o', folder / 'stubs.elf', folder / 'stubs.bin'
        defines = ['-DENABLE_GAMEPAD'] if enable_gamepad else []
        if not flow_logs:
            defines.append('-DNO_FLOW_LOGS')
        run('clang.exe', '--target=aarch64-linux-android28', *defines, '-c', ROOT / 'patches/controls-diag/flow-stubs.S', '-o', obj)
        definitions = {'EVENT_TARGET': 0x1314550, 'DATA_TARGET': 0x13144F0,
                       'SOURCE_TARGET': 0x12EC9E0, 'DEVICE_TARGET': 0x12ECB40,
                       'GOT_LOG': 0x13BC798, 'MASK_RESUME': 0xCEEFD8}
        run('ld.lld.exe', '-Ttext=' + hex(CAVE), '--entry=' + ('flow_event' if flow_logs else 'gamepad_enable'),
            *['--defsym=' + key + '=' + hex(value) for key, value in definitions.items()], obj, '-o', elf)
        run('llvm-objcopy.exe', '-O', 'binary', '--only-section=.text', elf, binary)
        payload = binary.read_bytes()
        symbols = {}
        for line in run('llvm-nm.exe', '--defined-only', elf).splitlines():
            fields = line.split()
            if len(fields) == 3 and fields[2] in {*CALLS, 'gamepad_enable'}:
                symbols[fields[2]] = int(fields[0], 16)
        expected_symbols = set(CALLS) if flow_logs else set()
        if enable_gamepad:
            expected_symbols.add('gamepad_enable')
        if set(symbols) != expected_symbols or not payload or CAVE + len(payload) > CAVE_END:
            raise ValueError('Simbolos invalidos ou cave excedida')

    result = bytearray(data)
    patches = []

    def put(va, before, after, purpose):
        offset = va - VA_DELTA
        if data[offset:offset + len(after)] != before:
            raise ValueError(f'Bytes inesperados em {va:#x}')
        result[offset:offset + len(after)] = after
        patches.append({'elfVa': hex(va), 'offset': offset, 'before': before.hex(),
                        'after': after.hex(), 'purpose': purpose})

    if flow_logs:
        for name, (callsite, original_target) in CALLS.items():
            put(callsite, branch(callsite, original_target), branch(callsite, symbols[name]), name)
    if enable_gamepad:
        # Unlike the two call hooks, this inline hook uses B and preserves LR.
        jump = struct.pack('<I', struct.unpack('<I', branch(0xCEEFD4, symbols['gamepad_enable']))[0] & ~0x80000000)
        put(0xCEEFD4, bytes.fromhex('004101fc'), jump, 'Enable gamepad in local init mask; keep keyboard/touch')
    put(CAVE, data[CAVE - VA_DELTA:CAVE - VA_DELTA + len(payload)], payload,
        'CTRLFLOW stubs' if flow_logs else 'Local gamepad mask stub; no logging')
    if len(result) != len(data):
        raise AssertionError('Tamanho da biblioteca alterado')
    if len(source_apk_library_sha256) != 64 or any(ch not in '0123456789abcdefABCDEF' for ch in source_apk_library_sha256):
        raise ValueError('SHA-256 da biblioteca do APK base inválido')
    manifest = {'status': ('device-validated-gamepad-mask' if enable_gamepad
                           else 'diagnostic-only-host-verified-not-device-tested'),
                'sourceSha256': source_apk_library_sha256.lower(), 'inputLibrarySha256': SOURCE_SHA,
                'outputSha256': sha(result), 'buildId': BUILD_ID,
                'caveVa': hex(CAVE), 'caveBytes': len(payload),
                'symbols': {key: hex(value) for key, value in symbols.items()}, 'patches': patches,
                'limit': 'Logging por evento/frame pode afetar latencia; nao e patch de jogabilidade.'}
    manifest['enableGamepad'] = enable_gamepad
    manifest['flowLogs'] = flow_logs
    if enable_gamepad:
        manifest['inputMaskChange'] = {'before': '0x22', 'after': '0x23'}
        manifest['limit'] = ('Diagnostic build with logs' if flow_logs
                             else 'Physical controller was accepted on S24; broader devices remain untested.')
    return bytes(result), manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apk', type=Path, help='APK whose native member is the verified source')
    parser.add_argument('--input-library', type=Path,
                        help='Library after Exynos+widescreen; its hash must match the expected source')
    parser.add_argument('--source-apk-library-sha256', default=SOURCE_SHA,
                        help='Original APK native SHA for repack manifest when using --input-library')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--llvm-bin', type=Path, default=DEFAULT_LLVM)
    parser.add_argument('--check-only', action='store_true')
    parser.add_argument('--enable-gamepad', action='store_true',
                        help='Candidato experimental: habilita gamepad mantendo teclado e toque')
    parser.add_argument('--no-flow-logs', action='store_true',
                        help='Com --enable-gamepad, gera somente a habilitacao, sem instrumentacao')
    args = parser.parse_args()
    if bool(args.apk) == bool(args.input_library):
        parser.error('Informe exatamente um entre --apk e --input-library')
    if args.no_flow_logs and not args.enable_gamepad:
        parser.error('--no-flow-logs exige --enable-gamepad')
    if not args.check_only and args.output is None:
        parser.error('--output e obrigatorio sem --check-only')
    if args.output is not None:
        output = args.output.resolve()
        manifest_path = Path(str(output) + '.patch.json')
        if (output.is_relative_to(ROOT / 'original') or output.is_relative_to(ROOT / 'build')
                or (args.apk and output == args.apk.resolve())
                or (args.input_library and output == args.input_library.resolve())):
            parser.error('Saida deve ser separada, fora de original/ e build/')
        if not args.check_only and (output.exists() or manifest_path.exists()):
            raise FileExistsError('Saida ou manifesto existente; preservado')
    if args.apk:
        with zipfile.ZipFile(args.apk) as apk:
            if apk.namelist().count(NATIVE_MEMBER) != 1:
                raise ValueError('Biblioteca ausente ou duplicada no APK')
            source = apk.read(NATIVE_MEMBER)
        source_apk_library_sha256 = SOURCE_SHA
    else:
        if not args.input_library.is_file():
            parser.error('--input-library não encontrado')
        source = args.input_library.read_bytes()
        source_apk_library_sha256 = args.source_apk_library_sha256
    result, manifest = build_diagnostic(source, args.llvm_bin, enable_gamepad=args.enable_gamepad,
                                        flow_logs=not args.no_flow_logs,
                                        source_apk_library_sha256=source_apk_library_sha256)
    if args.apk:
        manifest['inputApk'] = str(args.apk.resolve())
    else:
        manifest['inputLibrary'] = str(args.input_library.resolve())
    if not args.check_only:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(result)
        with manifest_path.open('x', encoding='utf-8') as stream:
            stream.write(json.dumps(manifest, indent=2) + '\n')
        if sha(output.read_bytes()) != manifest['outputSha256']:
            raise RuntimeError('Releitura da saida diferente do esperado')
    print(json.dumps({key: manifest[key] for key in ['status', 'sourceSha256', 'outputSha256', 'caveBytes', 'symbols']}, indent=2))
    print('Somente verificacao; nenhuma biblioteca gravada.' if args.check_only else str(output))


if __name__ == '__main__':
    main()
