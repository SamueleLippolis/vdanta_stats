"""Load and validate VDAnta season results."""

from pathlib import Path

import pandas as pd


VALID_RESULTS = {"W", "Q", "N", "A", "R"}


def load_results(file_path: Path, first_year: int, last_year: int) -> pd.DataFrame:
    """Return the selected seasons indexed by their starting year."""
    if first_year > last_year:
        raise ValueError("first_year cannot be greater than last_year")

    data = pd.read_excel(file_path).dropna(how="all").dropna(axis=1, how="all")
    if data.empty or len(data.columns) < 2:
        raise ValueError("The dataset must contain a season column and at least one coach")

    season_column = data.columns[0]
    data = data.rename(columns={season_column: "Season"})
    data["Year"] = data["Season"].map(_season_start_year)
    data = data[data["Year"].between(first_year, last_year)].copy()

    expected_years = set(range(first_year, last_year + 1))
    missing_years = sorted(expected_years - set(data["Year"]))
    if missing_years:
        raise ValueError(f"Dataset is missing seasons starting in: {missing_years}")

    coach_columns = [column for column in data.columns if column not in {"Season", "Year"}]
    for column in coach_columns:
        data[column] = data[column].map(_normalise_result)

    return data.set_index("Year")[coach_columns].sort_index()


def _season_start_year(value: object) -> int:
    text = str(value).strip()
    try:
        return int(text.split("/")[0])
    except ValueError as error:
        raise ValueError(f"Invalid season value: {value!r}") from error


def _normalise_result(value: object) -> str:
    if pd.isna(value):
        return "A"
    result = str(value).strip().upper()
    if result not in VALID_RESULTS:
        raise ValueError(f"Unknown result code: {value!r}")
    return result
