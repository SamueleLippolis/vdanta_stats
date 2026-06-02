"""
data_loader.py
Functions to load and parse the VDAnta results spreadsheet.
"""

import pandas as pd


def extract_original_data(file_path: str) -> list[list[str]]:
    """
    Reads an Excel/ODS file with:
      - first column  = season year (ignored)
      - other columns = trainer names
      - values below each name = result letters

    Returns a list of lists like:
        [
            ['Lippo', 'W', 'Q', 'R', 'N', 'N', 'Q'],
            ['Gallo', 'Q', 'R', 'R', 'R', 'W', 'Q'],
            ...
        ]

    Result codes:
        W = Winner
        Q = Qualified
        R = Relegated
        N = Not qualified
        A = Absent
    """
    # For .ods files you may need: pip install odfpy
    df = pd.read_excel(file_path)

    # Drop fully empty rows/columns
    df = df.dropna(how="all")
    df = df.dropna(axis=1, how="all")

    # All columns except the first (season year)
    names_columns = df.columns[1:]

    original_data = []
    for name in names_columns:
        values = df[name].dropna().astype(str).tolist()
        original_data.append([str(name)] + values)

    return original_data
