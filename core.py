import csv
import shutil
from pathlib import Path
import fnmatch

def clean_field(field: str) -> (str, bool):
    """
    Clean a single CSV field by removing:
      - Literal "CRLF"
      - Carriage returns (\r)
      - Newlines (\n)
      - Non-breaking spaces (\u00A0)
    Returns the cleaned field and a flag indicating whether it changed.
    """
    cleaned = (
        field
        .replace("CRLF", " ")
        .replace("\r", "")
        .replace("\n", " ")
        .replace("\u00A0", " ")
    )
    return cleaned, (cleaned != field)

def process_file(
    input_file: Path,
    output_file: Path,
    log_fp=None,
    backup_dir: Path=None,
    verbose: bool=False,
    input_root: Path=None,
    only_changed: bool=False
) -> bool:
    """
    Process one CSV file:
    - Clean fields
    - Remove trailing empty columns
    - Optionally backup original when modifications occur
    - Optionally log changes
    - Optionally skip writing output if no changes and only_changed=True
    Returns True if any changes were made.
    """
    modified = False
    cleaned_rows = []

    # Read and clean fields
    with input_file.open(newline='', encoding='utf-8') as inf:
        reader = csv.reader(inf)
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
                        log_fp.write(f"{input_file}:{lineno} | {field!r} -> {cleaned!r}\n")

            if verbose and row_changed:
                print(f"Modified line {lineno} in {input_file}")

            # Remove any trailing empty columns
            while new_row and new_row[-1] == "":
                new_row.pop()
                modified = True
                if log_fp:
                    log_fp.write(f"{input_file}:{lineno} | Removed trailing empty column\n")
                if verbose:
                    print(f"Removed trailing empty column at line {lineno} in {input_file}")

            cleaned_rows.append(new_row)

    # Skip writing if only_changed=True and nothing was modified
    if only_changed and not modified:
        return False

    # Backup original if requested and modifications occurred
    if modified and backup_dir and input_root:
        rel_path = input_file.relative_to(input_root)
        target = backup_dir / rel_path
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            shutil.copy2(input_file, target)

    # Write cleaned rows out
    with output_file.open('w', newline='', encoding='utf-8') as outf:
        writer = csv.writer(outf)
        writer.writerows(cleaned_rows)

    return modified

def gather_files(base: Path, pattern: str):
    """Yield all files matching pattern under base (file or directory)."""
    if base.is_file() and fnmatch.fnmatch(base.name, pattern):
        yield base
    elif base.is_dir():
        for f in base.rglob(pattern):
            yield f
