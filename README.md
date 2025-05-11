# CSV Cleaner

A minimalistic tool to clean CSV files by stripping out stray CRLF, newlines, and non-breaking spaces.  
Supports logging, backup, glob‑pattern filtering, and optional ZIP compression.

## Instructions

# CLI Usage:
csv-cleaner INPUT OUTPUT \
  [--log clean.log] \
  [--backup backups/] \
  [--pattern "*.csv"] \
  [--zip cleaned.zip]

