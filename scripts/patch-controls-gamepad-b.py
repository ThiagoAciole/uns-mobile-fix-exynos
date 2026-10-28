"""Compoe em memoria o candidato de prompts e protecao do B do gamepad."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('select_patch', ROOT / 'scripts/patch-controls-select-prompts.py')
select = importlib.util.module_from_spec(spec)
spec.loader.exec_module(select)
HOOKS = (0x9e7c30, 0x9e7cbc)

def compose(data, manifest, llvm):
    base, report = select.build_patch(data, manifest, llvm)
    offset = select.extender.INSERT_OFFSET
    va = select.extender.CODE_VA
    pos = (report['payloadBytes'] + 15) & ~15
    address = va + pos
    with tempfile.TemporaryDirectory(prefix='storm-b-hook-') as folder:
        folder = Path(folder)
        objs = []
        for i, name in enumerate(('gamepad-b-hook.S', 'gamepad-b-policy.c')):
            obj = folder / f'{i}.o'
            subprocess.run([str(llvm / 'clang.exe'), '--target=aarch64-linux-android28', '-ffreestanding', '-fno-stack-protector', '-fno-jump-tables', '-fno-asynchronous-unwind-tables', '-fno-unwind-tables', '-fno-pic', '-Os', '-c', str(ROOT / 'patches/controls-diag' / name), '-o', str(obj)], check=True, capture_output=True)
            objs.append(obj)
        elf, raw = folder / 'payload.elf', folder / 'payload.bin'
        symbols = {'game_event_type':0x12ecb30, 'game_event_source':0x12ec9e0, 'game_key_code':0x12eca40, 'game_finish_event':0x12ecb20}
        command = [str(llvm / 'ld.lld.exe'), '-Ttext='+hex(address), '--entry=gamepad_b_finish_hook', '--no-undefined'] + ['--defsym='+k+'='+hex(v) for k,v in symbols.items()] + [*map(str,objs), '-o',str(elf)]
        subprocess.run(command, check=True, capture_output=True)
        reloc = subprocess.check_output([str(llvm / 'llvm-readelf.exe'), '-r', str(elf)], text=True)
        sections = subprocess.check_output([str(llvm / 'llvm-readelf.exe'), '-S', '-W', str(elf)], text=True)
        if 'There are no relocations' not in reloc or any(s in sections for s in ('.rodata', '.data ', '.bss ')):
            raise ValueError('Payload possui relocacoes ou secoes inesperadas')
        subprocess.run([str(llvm / 'llvm-objcopy.exe'), '-O','binary','--only-section=.text',str(elf),str(raw)],check=True,capture_output=True)
        payload = raw.read_bytes()
    result=bytearray(base)
    if not payload or pos+len(payload)>select.extender.CODE_CAPACITY or any(result[offset+pos:offset+pos+len(payload)]):
        raise ValueError('Cave indisponivel ou insuficiente')
    result[offset+pos:offset+pos+len(payload)] = payload
    changes=[]
    for hook in HOOKS:
        at=hook-select.VA_DELTA
        expected=select.branch(hook, 0x12ecb20)
        expected=struct.pack('<I',struct.unpack('<I',expected)[0] | 0x80000000)
        if base[at:at+4]!=expected: raise ValueError(f'Chamada inesperada {hook:#x}')
        after=struct.pack('<I',struct.unpack('<I',select.branch(hook,address))[0] | 0x80000000)
        result[at:at+4]=after
        changes.append({'elfVa':hex(hook),'before':expected.hex(),'after':after.hex()})
    restored=bytearray(result)
    restored[offset+pos:offset+pos+len(payload)]=bytes(len(payload))
    for c in changes:
        at=int(c['elfVa'],16)-select.VA_DELTA
        restored[at:at+4]=bytes.fromhex(c['before'])
    if bytes(restored)!=base: raise AssertionError('Alteracao inesperada')
    return bytes(result), {'status':'experimental-host-only', 'inputSha256':select.SOURCE_SHA256, 'sourceSha256':select.SOURCE_SHA256, 'selectPayloadSha256':report['outputSha256'], 'outputSha256':hashlib.sha256(result).hexdigest(), 'buildId':select.extender.BUILD_ID, 'hookVa':hex(address), 'hookBytes':len(payload), 'patches':changes, 'limitations':['B em todas as telas depende de validacao no S24', 'nao comprova cancelamento em menus nem ataque em combate']}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--check-only', action='store_true')
    mode.add_argument('--output', type=Path, help='Nova biblioteca fora de build/ e original/')
    p.add_argument('--llvm-bin',type=Path,default=select.DEFAULT_LLVM)
    a=p.parse_args()
    if a.output:
        output = a.output.resolve()
        if output == a.input.resolve() or output.is_relative_to(ROOT / 'build') or output.is_relative_to(ROOT / 'original'):
            p.error('Saida deve ser separada e fora de build e original')
        if output.exists() or Path(str(output) + '.patch.json').exists():
            p.error('Saida ou manifesto existente; preservado')
    manifest=json.loads(Path(str(a.input)+'.patch.json').read_text(encoding='utf-8-sig'))
    result,report=compose(a.input.read_bytes(),manifest,a.llvm_bin)
    if a.output:
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open('xb') as stream:
            stream.write(result)
        if hashlib.sha256(output.read_bytes()).hexdigest() != report['outputSha256']:
            raise RuntimeError('Hash da biblioteca gravada difere do manifesto')
        with Path(str(output) + '.patch.json').open('x', encoding='utf-8') as stream:
            json.dump(report, stream, indent=2)
            stream.write('\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__': main()
