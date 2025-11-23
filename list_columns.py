#!/usr/bin/env python3
"""
CSV Column Lister

For one or more CSV files, this script prints:

File name - <filename>
Column names
<each column name on its own line>

You can pass individual files, directories, or glob patterns.
Example:
    python list_columns.py data/file1.csv data/file2.csv
    python list_columns.py "data/*.csv"
    python list_columns.py -r "data/**/*.csv"
"""

import argparse
import csv
import glob
import os
from collections import OrderedDict


def resolve_inputs(inputs, recursive=False):
    """
    Expand files, directories, and glob patterns into a unique ordered list
    of CSV file paths.
    """
    paths = []

    for item in inputs:
        # If the string has glob chars, treat it as a pattern
        if any(ch in item for ch in ["*", "?", "["]):
            matches = glob.glob(item, recursive=recursive)
            paths.extend(
                m for m in matches if os.path.isfile(m) and m.lower().endswith(".csv")
            )
        elif os.path.isdir(item):
            # Directory: find CSVs inside
            pattern = "**/*.csv" if recursive else "*.csv"
            found = glob.glob(os.path.join(item, pattern), recursive=recursive)
            paths.extend(p for p in found if os.path.isfile(p))
        else:
            # Regular file path
            if os.path.isfile(item) and item.lower().endswith(".csv"):
                paths.append(item)
            else:
                print(f"Warning: Skipping non-CSV or missing path: {item}")

    # Deduplicate while preserving order
    return list(OrderedDict.fromkeys(paths))


def read_headers(csv_path):
    """
    Return (headers, has_header_flag).

    - headers: list of strings (column names OR first row values)
    - has_header_flag: True if csv.Sniffer thinks the first row is a header

    If the file is empty or unreadable, returns ([], True).
    """
    try:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            sample = f.read(4096)
            f.seek(0)

            # Detect delimiter
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel  # fallback

            # Detect header vs data
            try:
                has_header = csv.Sniffer().has_header(sample)
            except csv.Error:
                has_header = True  # assume headers if unsure

            reader = csv.reader(f, dialect)
            first_row = next(reader, None)

            if first_row is None:
                return [], True  # empty file

            # Whether it's truly a header or not, we return that first row,
            # as requested: "column names or the 1st row"
            return first_row, has_header

    except Exception as e:
        print(f"Error reading '{csv_path}': {e}")
        return [], True


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Print 'File name -', 'Column names', then each column "
            "on a new line for multiple CSV files."
        )
    )

    parser.add_argument(
        "inputs",
        nargs="+",
        help="CSV files, directories, or glob patterns (e.g., data/*.csv or data/**/*.csv)",
    )

    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Recurse into subdirectories for directory and glob inputs.",
    )

    args = parser.parse_args()

    csv_files = resolve_inputs(args.inputs, recursive=args.recursive)

    if not csv_files:
        print("No CSV files found.")
        return

    for path in csv_files:
        headers, _ = read_headers(path)

        print(f"File name - {os.path.basename(path)}")
        print("Column names")

        if not headers:
            print("(no data)")
        else:
            for col in headers:
                print(col)

        print()  # blank line between files


if __name__ == "__main__":
    main()
