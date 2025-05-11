# cli.py
import argparse
from pathlib import Path
import sys
from core import process_file, gather_files

def main():
    p = argparse.ArgumentParser(prog="csv-cleaner",
        description="Clean CSVs: remove CRLF, newlines, NBSP; log; backup; zip.")
    p.add_argument("input",  help="File or directory")
    p.add_argument("output", help="File or directory")
    p.add_argument("--log",    default="clean_log.txt")
    p.add_argument("--backup", help="Backup directory")
    p.add_argument("--pattern", default="*.csv")
    p.add_argument("--zip",    help="Zip output to this filename")
    args = p.parse_args()

    inp, out = Path(args.input), Path(args.output)
    log_fp = open(args.log, 'a', encoding='utf-8')

    files = list(gather_files(inp, args.pattern))
    for f in files:
        rel = f.relative_to(inp) if inp.is_dir() else Path(f.name)
        dest = (out / rel) if inp.is_dir() else out
        dest.parent.mkdir(parents=True, exist_ok=True)
        changed = process_file(f, dest, log_fp,
                               backup_dir=Path(args.backup) if args.backup else None)
        print(f"{'✔' if changed else '–'} {f}")

    log_fp.close()

    if args.zip:
        import zipfile
        with zipfile.ZipFile(args.zip, 'w', zipfile.ZIP_DEFLATED) as z:
            for file in (out if out.is_dir() else [out]).__iter__():
                for item in (Path(args.output).rglob('*') if out.is_dir() else [out]):
                    z.write(item, item.relative_to(out))
        print(f"Output compressed → {args.zip}")

if __name__ == "__main__":
    main()
