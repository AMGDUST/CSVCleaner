import csv
import shutil
from pathlib import Path
import fnmatch

def clean_field(field: str) -> (str, bool):
    """
    Clean a single CSV field by removing CRLF literals, newlines, carriage returns,
    and non-breaking spaces. Returns the cleaned field and a flag indicating change.
    """
    cleaned = (
        field.replace("CRLF", " ")
             .replace("\r", "")
             .replace("\n", " ")
             .replace("\u00A0", " ")
    )
    return cleaned, cleaned != field

def process_file(
    input_file: Path,
    output_file: Path,
    log_fp=None,
    backup_dir: Path=None,
    verbose: bool=False,
    input_root: Path=None
) -> bool:
    """
    Process one CSV file: clean fields, write to output_file.
    Optionally back up the original (preserving directory tree) and log changes.
    Returns True if any field was modified.
    """
    # Backup if requested
    if backup_dir and input_root:
        rel_path = input_file.relative_to(input_root)
        target = backup_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(input_file, target)

    modified = False
    with input_file.open(newline='', encoding='utf-8') as inf, \
         output_file.open('w', newline='', encoding='utf-8') as outf:
        reader = csv.reader(inf)
        writer = csv.writer(outf)

        for lineno, row in enumerate(reader, start=1):
            new_row = []
            row_changed = False
            for field in row:
                cleaned, changed = clean_field(field)
                new_row.append(cleaned)
                if changed:
                    modified = True
                    row_changed = True
                    if log_fp:
                        log_fp.write(f"{input_file}:{lineno} | {field!r} → {cleaned!r}\n")
            writer.writerow(new_row)
            if verbose and row_changed:
                print(f"Modified line {lineno} in {input_file}")

    return modified

def gather_files(base: Path, pattern: str):
    """Yield all files matching pattern under base (file or directory)."""
    if base.is_file() and fnmatch.fnmatch(base.name, pattern):
        yield base
    elif base.is_dir():
        for f in base.rglob(pattern):
            yield f