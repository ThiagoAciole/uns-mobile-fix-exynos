"""Rebuild the primary 1.2.10 English message slot using the reviewed pt-BR catalogs."""
import argparse
import importlib.util
import json
import zipfile
from pathlib import Path

from xfbin_messages import rebuild, catalog


def load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("apk", type=Path)
    parser.add_argument("output", type=Path, help="Fresh separate build directory")
    parser.add_argument("--graphic-textures", type=Path, help="Prepared same-size Portuguese texture PNGs")
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError("Output directory exists; preserved")
    root = Path(__file__).resolve().parents[1]
    catalogs = root / "patches/ptbr/catalogs"
    inv = load_module("cpk_inventory", "inventory-cpk.py")
    unpack = load_module("cpk_extract", "extract-cpk-files.py")
    cpk = load_module("cpk_patch", "patch-cpk.py")
    title_bg = load_module("title_background", "patch-title-bg-s24.py")
    texture_codec = load_module("xfbin_textures", "xfbin_textures.py")
    banks = inv.inventory(args.apk)
    bank_name = "assets/data/disc/installTimeDisc.awb"
    bank = next(row for row in banks if row["member"] == bank_name)
    files = {row["path"]: row for row in bank["files"]}
    replacements, counts = {}, {}
    args.output.mkdir(parents=True)
    with zipfile.ZipFile(args.apk) as archive, archive.open(bank_name) as stream:
        for name in ("message.bin", "message_btl.bin", "itemtext.bin"):
            path = "data/event/eng/" + name + ".xfbin"
            row = files[path]
            if not 0 < row["extractSize"] <= 64 * 1024 * 1024:
                raise ValueError("Message file outside size limit")
            stream.seek(row["offset"])
            source = unpack.decompress(stream.read(row["size"]), row["extractSize"])
            document = json.loads((catalogs / (name + ".json")).read_text(encoding="utf-8"))
            result = rebuild(source, document)
            assert len(catalog(result)["entries"]) == len(document["entries"])
            output = args.output / (name + ".xfbin")
            with output.open("xb") as target:
                target.write(result)
            replacements[path] = str(output.resolve())
            counts[name] = {"records": len(document["entries"]),
                            "changed": sum(row["source"] != row["translation"] for row in document["entries"])}
        path = "data/interface/title/ANDROID/xtitle_bg_e.xfbin"
        row = files[path]
        if not 0 < row["extractSize"] <= 64 * 1024 * 1024:
            raise ValueError("Title background outside size limit")
        stream.seek(row["offset"])
        source = unpack.decompress(stream.read(row["size"]), row["extractSize"])
        result, report = title_bg.patch(source)
        output = args.output / "xtitle_bg_e.xfbin"
        with output.open("xb") as target:
            target.write(result)
        output.with_suffix(".xfbin.patch.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        replacements[path] = str(output.resolve())
        if args.graphic_textures:
            graphic_dir = args.graphic_textures.resolve()
            graphic_files = (
                ("data/interface/mode/eng/ANDROID/xmode.xfbin", {"xmode_fd_mission00":"xmode_fd_mission00.png", "xmode_fd_battle00":"xmode_fd_battle00.png", "xmode_fd_option00":"xmode_fd_option00.png"}),
                ("data/interface/mode/eng/xmode.xfbin", {"xmode_fd_mission00":"xmode_fd_mission00.png", "xmode_fd_battle00":"xmode_fd_battle00.png", "xmode_fd_option00":"xmode_fd_option00.png"}),
                ("data/interface/title/eng/ANDROID/xtitle.xfbin", {"xtitle_fd01":"xtitle_fd01.png"}),
                ("data/interface/index/eng/mindex_mode.xfbin", {"mode_indexname_fd":"mode_indexname_fd.png"}),
                ("data/interface/index/eng/ANDROID/xmindex_option.xfbin", {"option_indexname_fd":"option_indexname_fd_android.png"}),
                ("data/interface/index/eng/mindex_option.xfbin", {"option_indexname_fd":"option_indexname_fd_nonandroid.png"}),
            )
            for index, (path, texture_names) in enumerate(graphic_files):
                row = files[path]
                if not 0 < row["extractSize"] <= 64 * 1024 * 1024:
                    raise ValueError(f"Graphic file outside size limit: {path}")
                stream.seek(row["offset"])
                source = unpack.decompress(stream.read(row["size"]), row["extractSize"])
                changed, report = texture_codec.replace(source, {
                    name: (graphic_dir / filename).read_bytes()
                    for name, filename in texture_names.items()
                })
                if {item["name"] for item in report} != texture_names.keys():
                    raise ValueError(f"Not all requested textures changed in {path}")
                output = args.output / f"graphic-{index}.xfbin"
                with output.open("xb") as target:
                    target.write(changed)
                output.with_suffix(".xfbin.textures.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
                replacements[path] = str(output.resolve())
    (args.output / "cpk-plan.json").write_text(json.dumps(replacements, indent=2), encoding="utf-8")
    output_bank = args.output / "installTimeDisc.awb"
    cpk.patch(args.apk, bank_name, replacements, output_bank)
    bank_plan = {bank_name: str(output_bank.resolve())}
    if args.graphic_textures:
        option_bank = "assets/data/sim/installTime.awb"
        option_path = "data/interface/option/eng/ANDROID/moption.xfbin"
        row = next(item for bank in banks if bank["member"] == option_bank for item in bank["files"] if item["path"] == option_path)
        if not 0 < row["extractSize"] <= 64 * 1024 * 1024:
            raise ValueError("Android options menu outside size limit")
        with zipfile.ZipFile(args.apk) as archive, archive.open(option_bank) as stream:
            stream.seek(row["offset"])
            source = unpack.decompress(stream.read(row["size"]), row["extractSize"])
        changed, report = texture_codec.replace(source, {
            "option_indexname_fd": (args.graphic_textures.resolve() / "option_indexname_fd_android.png").read_bytes()
        })
        if {item["name"] for item in report} != {"option_indexname_fd"}:
            raise ValueError("Android options heading texture was not changed")
        option_output = args.output / "graphic-android-options.xfbin"
        with option_output.open("xb") as target:
            target.write(changed)
        option_output.with_suffix(".xfbin.textures.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        option_bank_output = args.output / "installTime.awb"
        cpk.patch(args.apk, option_bank, {option_path: str(option_output.resolve())}, option_bank_output)
        bank_plan[option_bank] = str(option_bank_output.resolve())
    (args.output / "apk-plan.json").write_text(json.dumps(bank_plan, indent=2), encoding="utf-8")
    (args.output / "validation.json").write_text(json.dumps(counts, indent=2), encoding="utf-8")
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    main()
