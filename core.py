# core.py
import csv
import shutil
from pathlib import Path
import fnmatch

def clean_field(field: str) -> (str, bool):
    """Clean a single CSV field; return (cleaned_field, was_changed)."""
    original = field
    cleaned = (
        field.replace("CRLF", " ")
             .replace("\r", "")
             .replace("\n", " ")
             .replace("\u00A0", " ")
    )
    return cleaned, cleaned != original

def process_file(input_file: Path, output_file: Path, log_fp, backup_dir: Path=None):
    """Read, clean, write one CSV; log changes; optionally back up."""
    if backup_dir:
        backup_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(input_file, backup_dir / input_file.name)

    modified = False
    with input_file.open(newline='', encoding='utf-8') as inf, \
         output_file.open('w', newline='', encoding='utf-8') as outf:
        reader = csv.reader(inf)
        writer = csv.writer(outf)

        for lineno, row in enumerate(reader, 1):
            new_row = []
            for field in row:
                cleaned, changed = clean_field(field)
                new_row.append(cleaned)
                if changed:
                    modified = True
                    log_fp.write(f"{input_file}:{lineno} | {field!r} → {cleaned!r}\n")
            writer.writerow(new_row)
    return modified

def gather_files(base: Path, pattern: str):
    """Yield all files under base matching glob pattern."""
    if base.is_file() and fnmatch.fnmatch(base.name, pattern):
        yield base
    elif base.is_dir():
        for f in base.rglob(pattern):
            yield f
