FatalError's CSV Cleaner


A minimalistic Python tool to clean CSV files. Originally designed to santiize SaintCoinach output.


Command Line Interface Usage:
csv-cleaner INPUT OUTPUT [OPTIONS]

INPUT           Path to a CSV file or a directory of CSV files
OUTPUT          Path to an output file or directory

OPTIONS:
--log [LOGFILE]        Write detailed changes to LOGFILE. If no name is given, a timestamped default name is used.
--backup DIR           Back up original files (preserving subdirectories) to the specified directory when changes occur.
--pattern PATTERN      Glob pattern to select files, for example "*.csv" (default).
--zip ZIPFILE          Compress all cleaned output into the given ZIP file.
--only-changed         Only write output files for inputs that had modifications. Unchanged files are skipped.
--verbose              Print the line numbers of modified rows to the console.

Examples:

Basic Cleanup:
csv-cleaner raw.csv cleaned.csv

Directory Cleanup with Logging:
csv-cleaner data/raw_folder data/cleaned_folder --log

Only Changed Files and Logging:
csv-cleaner data/raw_folder data/cleaned_folder --only-changed --log

Verbose Mode:
csv-cleaner input.csv output.csv --verbose

Features Summary:
• Removes literal CRLF markers within CSV fields
• Strips embedded newline and carriage return characters
• Replaces non-breaking spaces with regular spaces
• Optional timestamped logging with automatic compression and cleanup
• Optional backup of original files, preserving directory structure
• "Only Changed" mode to generate output only when modifications occur
• "Verbose" mode for detailed console feedback