"""Generate the all-time presidency for the configured period."""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import yaml
from tabulate import tabulate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_results
from src.statistics import count_results


def load_presidency(file_path: Path, first_year: int, last_year: int) -> pd.DataFrame:
    """Load P/V appointments, retaining people without any appointments."""
    if first_year > last_year:
        raise ValueError("first_year cannot be greater than last_year")
    data = pd.read_excel(file_path).dropna(how="all")
    if data.empty or len(data.columns) < 2:
        raise ValueError("The dataset must contain seasons and at least one person")
    years = data.iloc[:, 0].astype(str).str.strip().str.split("/").str[0].astype(int)
    data = data.iloc[:, 1:].copy()
    data.index = years
    data = data.loc[data.index.to_series().between(first_year, last_year)]
    if data.index.has_duplicates:
        raise ValueError("The presidency dataset contains duplicate seasons")
    missing = sorted(set(range(first_year, last_year + 1)) - set(data.index))
    if missing:
        raise ValueError(f"Presidency dataset is missing seasons starting in: {missing}")
    data.columns = data.columns.astype(str).str.strip()
    if data.columns.has_duplicates:
        raise ValueError("The presidency dataset contains duplicate names")
    for column in data:
        data[column] = data[column].fillna("").astype(str).str.strip().str.upper()
        invalid = set(data[column]) - {"", "P", "V"}
        if invalid:
            raise ValueError(f"Unknown presidency codes for {column}: {sorted(invalid)}")
    return data.sort_index()


def build_presidency(roles: pd.DataFrame, results: pd.DataFrame) -> pd.DataFrame:
    """Rank appointments, then seasons played, with competition-style ties."""
    results = results.rename(columns=lambda name: str(name).strip())
    if results.columns.has_duplicates:
        raise ValueError("The results dataset contains duplicate names")
    missing = sorted(set(roles.columns) - set(results.columns))
    if missing:
        raise ValueError(f"Cannot count participations for names missing from results: {missing}")
    counts = ["Presidenze", "Vice presidenze", "Partecipazioni"]
    rows = [
        {"Nome": name,
         "Presidenze": int(roles[name].eq("P").sum()),
         "Vice presidenze": int(roles[name].eq("V").sum()),
         "Partecipazioni": count_results(results[name])["Partecipazioni"]}
        for name in roles.columns
    ]
    ranking = pd.DataFrame(rows, columns=["Nome", *counts]).sort_values(
        counts, ascending=False, kind="stable",
    ).reset_index(drop=True)
    positions = []
    previous = None
    for index, key in enumerate(ranking[counts].itertuples(index=False, name=None), 1):
        positions.append(positions[-1] if key == previous else index)
        previous = key
    ranking.insert(0, "Posizione", positions)
    return ranking


def main() -> None:
    config = _load_config()
    years = config["year_selection"]
    output_directory = _output_directory(config, years["last_year"])
    results = load_results(
        PROJECT_ROOT / config["data"]["file_path"],
        years["first_year"],
        years["last_year"],
    )
    roles = load_presidency(
        PROJECT_ROOT / config["data"]["presidency_file_path"],
        years["first_year"], years["last_year"],
    )
    presidency = build_presidency(roles, results)
    csv_output_path = output_directory / "presidency.csv"
    image_output_path = output_directory / "presidency.png"
    presidency.to_csv(csv_output_path, index=False)
    _save_table_image(presidency, image_output_path, years["last_year"])

    print(tabulate(presidency, headers="keys", tablefmt="fancy_grid", showindex=False))
    print(f"\nSaved: {csv_output_path}")
    print(f"Saved: {image_output_path}")


def _save_table_image(presidency, output_path: Path, last_year: int) -> None:
    """Save a readable, presentation-ready rendering of the presidency."""
    row_count, column_count = presidency.shape
    figure_width = max(10, column_count * 1.7)
    figure_height = max(3, 1.3 + row_count * 0.48)
    figure, axis = plt.subplots(figsize=(figure_width, figure_height))
    axis.axis("off")

    table = axis.table(
        cellText=presidency.values,
        colLabels=presidency.columns,
        cellLoc="center",
        colLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)

    header_colour = "#243447"
    alternating_colours = ("#F5F7FA", "#E8EEF4")
    for (row, _column), cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.set_linewidth(1.2)
        if row == 0:
            cell.set_facecolor(header_colour)
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor(alternating_colours[(row - 1) % 2])
            if row <= 3:
                cell.set_text_props(weight="bold")

    title = f"Presidenze all-time ({last_year}/{last_year + 1})"
    figure.suptitle(title, fontsize=18, fontweight="bold", color=header_colour)
    figure.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _load_config() -> dict:
    with (PROJECT_ROOT / "configs" / "config.yaml").open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _output_directory(config: dict, last_year: int) -> Path:
    path = (
        PROJECT_ROOT
        / config["reports"]["output_dir"]
        / f"{last_year}_{last_year + 1}"
        / "presidency"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
