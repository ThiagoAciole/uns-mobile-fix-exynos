"""Reserva espaco executavel na biblioteca F1.1, preservando os segmentos existentes.

Esta ferramenta nao aplica prompts nem produz APK. A saida nao foi validada no S24.
"""
import argparse
import hashlib
import json
from pathlib import Path
import struct

SOURCE_SHA256 = '557b842e7f3372b1498843fce78df8b32bab43e26030d4092ef6c66ce290cb9e'
BUILD_ID = 'c3e506f9be350dfb4a00c79228754028'
INSERT_OFFSET = 0x13148C0
INSERT_SIZE = 0x4000
CODE_VA = 0x13188C0
CODE_CAPACITY = 0x3740
SCRATCH_VA = 0x1566390
SCRATCH_CAPACITY = 0x400
EXPECTED_RX = (1, 5, 0x90C890, 0x910890, 0x910890, 0xA08030, 0xA08030, 0x4000)
EXPECTED_LAST_RW = (1, 6, 0x13DE6E0, 0x13EA6E0, 0x13EA6E0, 0x7B978, 0x17BCA8, 0x4000)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def direct_branch_target(word, address):
    """Decodifica B/BL, B.cond, CBZ/CBNZ e TBZ/TBNZ; indiretos nao sao cobertos."""
    if word & 0x7c000000 == 0x14000000:
        immediate, width = word & 0x3ffffff, 26
    elif word & 0xff000010 == 0x54000000 or word & 0x7e000000 == 0x34000000:
        immediate, width = (word >> 5) & 0x7ffff, 19
    elif word & 0x7e000000 == 0x36000000:
        immediate, width = (word >> 5) & 0x3fff, 14
    else:
        return None
    if immediate & (1 << (width - 1)):
        immediate -= 1 << width
    return address + immediate * 4


def reserve_executable_space(data):
    """Devolve ELF reescrito e layout; aceita somente a biblioteca F1.1 conhecida."""
    if sha(data) != SOURCE_SHA256:
        raise ValueError('SHA-256 diferente da biblioteca F1.1 aceita')
    if data[:6] != b'\x7fELF\x02\x01' or struct.unpack_from('<HH', data, 16) != (3, 183):
        raise ValueError('Esperado ELF64 AArch64 compartilhado')
    if data[0x318:0x328].hex() != BUILD_ID:
        raise ValueError('Build ID diferente')
    phoff = struct.unpack_from('<Q', data, 32)[0]
    shoff = struct.unpack_from('<Q', data, 40)[0]
    phsize, phnum = struct.unpack_from('<HH', data, 54)
    shsize, shnum = struct.unpack_from('<HH', data, 58)
    if (phoff, phsize, phnum, shsize, shnum) != (0x40, 56, 10, 64, 27):
        raise ValueError('Cabecalhos ELF diferentes')
    if not (INSERT_OFFSET < shoff and shoff + shsize * shnum <= len(data)):
        raise ValueError('Tabela de secoes fora do arquivo')
    headers = [struct.unpack_from('<IIQQQQQQ', data, phoff + i * phsize) for i in range(phnum)]
    if (headers[2] != EXPECTED_RX or headers[3][0:4] != (1, 6, INSERT_OFFSET, 0x131C8C0)
            or headers[4] != EXPECTED_LAST_RW):
        raise ValueError('Segmentos executavel e de dados diferentes')
    if EXPECTED_RX[2] + EXPECTED_RX[5] != INSERT_OFFSET:
        raise ValueError('Espaco de insercao nao coincide com fim do segmento executavel')
    next_page = headers[3][3] & ~(INSERT_SIZE - 1)
    if CODE_VA + CODE_CAPACITY != next_page:
        raise ValueError('Extensao executavel sobrepoe pagina de dados gravavel')
    rw_end = EXPECTED_LAST_RW[3] + EXPECTED_LAST_RW[6]
    if not (rw_end <= SCRATCH_VA < SCRATCH_VA + SCRATCH_CAPACITY <=
            ((rw_end + INSERT_SIZE - 1) & ~(INSERT_SIZE - 1))):
        raise ValueError('Reserva gravavel fora da ultima pagina BSS')
    executable = memoryview(data)[EXPECTED_RX[2]:EXPECTED_RX[2] + EXPECTED_RX[5]]
    for index, (word,) in enumerate(struct.iter_unpack('<I', executable)):
        at = EXPECTED_RX[3] + index * 4
        target = direct_branch_target(word, at)
        if target is not None and CODE_VA <= target < CODE_VA + CODE_CAPACITY:
            raise ValueError(f'Branch direto existente aponta para a nova regiao: {at:#x}')

    result = bytearray(data[:INSERT_OFFSET] + bytes(INSERT_SIZE) + data[INSERT_OFFSET:])
    struct.pack_into('<Q', result, 40, shoff + INSERT_SIZE)
    for index, header in enumerate(headers):
        position = phoff + index * phsize
        if header[2] >= INSERT_OFFSET:
            struct.pack_into('<Q', result, position + 8, header[2] + INSERT_SIZE)
        if index == 2:
            struct.pack_into('<QQ', result, position + 32,
                             header[5] + CODE_CAPACITY, header[6] + CODE_CAPACITY)
        if index == 4:
            struct.pack_into('<Q', result, position + 40,
                             SCRATCH_VA + SCRATCH_CAPACITY - header[3])
    new_shoff = shoff + INSERT_SIZE
    for index in range(shnum):
        old_section = shoff + index * shsize
        section_offset = struct.unpack_from('<Q', data, old_section + 24)[0]
        if section_offset >= INSERT_OFFSET:
            struct.pack_into('<Q', result, new_shoff + index * shsize + 24,
                             section_offset + INSERT_SIZE)

    output = bytes(result)
    if len(output) != len(data) + INSERT_SIZE or output[INSERT_OFFSET:INSERT_OFFSET + INSERT_SIZE] != bytes(INSERT_SIZE):
        raise AssertionError('Releitura da reserva ELF falhou')
    if output[0x270:INSERT_OFFSET] != data[0x270:INSERT_OFFSET]:
        raise AssertionError('Bytes originais anteriores a insercao mudaram')
    if output[INSERT_OFFSET + INSERT_SIZE:shoff + INSERT_SIZE] != data[INSERT_OFFSET:shoff]:
        raise AssertionError('Bytes originais dos segmentos posteriores mudaram')
    layout = {'code_offset': INSERT_OFFSET, 'code_va': CODE_VA,
              'code_capacity': CODE_CAPACITY, 'inserted_bytes': INSERT_SIZE,
              'scratch_va': SCRATCH_VA, 'scratch_capacity': SCRATCH_CAPACITY,
              'sourceSha256': SOURCE_SHA256, 'outputSha256': sha(output),
              'branchCheck': 'B/BL, B.cond, CBZ/CBNZ, TBZ/TBNZ; indiretos nao cobertos',
              'status': 'host-only-no-payload-not-device-tested'}
    return output, layout


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--check-only', action='store_true', help='Valida em memoria sem gravar')
    args = parser.parse_args()
    if not args.check_only:
        parser.error('Por enquanto somente --check-only e permitido')
    _, layout = reserve_executable_space(args.input.read_bytes())
    print(json.dumps(layout, indent=2))


if __name__ == '__main__':
    main()
