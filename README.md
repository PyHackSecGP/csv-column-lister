# csv-column-lister

# CSV Column Lister

A small utility that prints, for one or more CSV files:

- `File name - <name>`
- `Column names`
- Each column on its own line

## Usage

### Standard library version
```bash
python list_columns.py data/file1.csv data/file2.csv
python list_columns.py "data/*.csv"
python list_columns.py -r "data/**/*.csv"   # recursive
