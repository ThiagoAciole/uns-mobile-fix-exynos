"""Inventario somente de leitura; --dry-run mostra itens para revisao, sem excluir."""
import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def inventory(root):
    items = []
    def add(path, category, reason):
        items.append({'path': path.relative_to(root).as_posix(), 'category': category,
                      'reason': reason, 'cleanup': 'preservar; revisao manual'})
    for folder in ('build', 'origin', 'original', 'work'):
        base = root / folder
        if not base.is_dir() or base.is_symlink():
            continue
        for path in sorted(base.iterdir()):
            name = path.name.lower()
            if path.is_symlink():
                add(path, 'dados_persistentes', 'link nao percorrido')
            elif folder in ('origin', 'original'):
                add(path, 'dados_persistentes', 'origem ou evidencia')
            elif folder == 'build':
                if name == 'naruto ultimate ninja storm.apk':
                    add(path, 'build_aceito_declarado', 'caminho final; aceite e hash devem ser confirmados')
                else:
                    add(path, 'candidato_ou_metadado', 'estado nao comprovado pelo nome')
            elif name.startswith('build-tmp-'):
                add(path, 'temporario_possivel', 'nome de temporario; pode estar em uso')
            elif 'candidate' in name or name == 'candidates':
                add(path, 'candidato', 'nome indica candidato; conteudo nao inspecionado')
            else:
                add(path, 'dados_persistentes', 'conteudo e dependencias nao classificados')
    # Reconhece projetos sem entrar em dados de assinatura nem seguir links.
    work = root / 'work'
    if work.is_dir() and not work.is_symlink():
        for directory, dirs, files in os.walk(work, followlinks=False):
            current = Path(directory)
            dirs[:] = [d for d in dirs if d.lower() != 'signing' and not (current / d).is_symlink()]
            for name in files:
                if name.lower().endswith('.gpr'):
                    add(current / name, 'projeto_ghidra', 'marcador de projeto; preservar tambem dados associados')
    return items


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='Mostra revisao de limpeza sem executar exclusao')
    args = parser.parse_args()
    print(json.dumps({'mode': 'dry-run' if args.dry_run else 'inventory',
                      'deletion_enabled': False, 'items': inventory(ROOT)}, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
