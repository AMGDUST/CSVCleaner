import argparse
import zipfile
import os
from pathlib import Path
from datetime import datetime
from core import process_file, gather_files

def main():
    parser = argparse.ArgumentParser(
        prog="csv-cleaner",
        description="Clean CSVs: remove CRLF, newlines, NBSP; optional log, backup, zip, verbose, only-changed."
    )
    parser.add_argument("input", help="Input file or directory")
    parser.add_argument("output", help="Output file or directory")
    parser.add_argument(
        "--log", nargs='?', const="clean_log.txt",
        help="Optional log file name. If provided without value, defaults to clean_log_TIMESTAMP.log"
    )
    parser.add_argument("--backup", help="Optional backup directory")
    parser.add_argument("--pattern", default="*.csv", help="File glob pattern (default: '*.csv')")
    parser.add_argument("--zip", dest="zip_out", help="Optional ZIP for cleaned output")
    parser.add_argument(
        "--only-changed", action="store_true",
        help="Only write output files if modifications occurred"
    )
    parser.add_argument("--verbose", action="store_true", help="Print modified line numbers")
    args = parser.parse_args()

    # Configure log
    log_fp = None
    if args.log:
        if args.log == "clean_log.txt":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            args.log = f"clean_log_{timestamp}.log"
        log_fp = open(args.log, 'w', encoding='utf-8')

    inp = Path(args.input)
    out = Path(args.output)
    files = list(gather_files(inp, args.pattern))

    for f in files:
        rel = f.relative_to(inp) if inp.is_dir() else Path(f.name)
        target = (out / rel) if inp.is_dir() else out
        target.parent.mkdir(parents=True, exist_ok=True)
        changed = process_file(
            f, target,
            log_fp=log_fp,
            backup_dir=Path(args.backup) if args.backup else None,
            verbose=args.verbose,
            input_root=inp if args.backup else None,
            only_changed=args.only_changed
        )
        print(f"{'✔' if changed else '–'} {f}")

    # Finish logging
    if log_fp:
        log_fp.close()
        log_zip = Path(args.log).with_suffix('.zip')
        with zipfile.ZipFile(log_zip, 'w', zipfile.ZIP_DEFLATED) as z:
            z.write(args.log, Path(args.log).name)
        os.remove(args.log)
        print(f"Log compressed → {log_zip}")

    # Zip cleaned output
    if args.zip_out:
        with zipfile.ZipFile(args.zip_out, 'w', zipfile.ZIP_DEFLATED) as z:
            for item in (out.rglob('*') if out.is_dir() else [out]):
                z.write(item, item.relative_to(out))
        print(f"Output compressed → {args.zip_out}")

if __name__ == "__main__":
    main()