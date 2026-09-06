"""Generate one PNG with statistics and result history per coach."""

import re
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_results
from src.statistics import count_results


def main() -> None:
    config = _load_config()
    years = config["year_selection"]
    conversion = config["result_to_number_conversion"]
    results = load_results(
        PROJECT_ROOT / config["data"]["file_path"],
        years["first_year"],
        years["last_year"],
    )
    output_directory = _output_directory(config, years["last_year"]) / "coaches_history"
    output_directory.mkdir(parents=True, exist_ok=True)

    for coach in results.columns:
        safe_name = _safe_file_name(coach)
        _save_history(
            coach,
            results[coach],
            conversion,
            output_directory / f"{safe_name}_history.png",
        )

    print(f"Generated histories for {len(results.columns)} coaches in: {output_directory}")


def _build_summary(coach: str, results: pd.Series) -> pd.DataFrame:
    base_counts = count_results(results)
    counts = {
        "Partecipazioni": base_counts["Partecipazioni"],
        "Vittorie": base_counts["Vittorie"],
        "Primi 3": base_counts["Primi 3"] + base_counts["Vittorie"],
        "Risultati neutri": int((results == "N").sum()),
        "Retrocessioni": base_counts["Retrocessioni"],
    }
    participations = counts["Partecipazioni"]
    percentages = {
        column: f"{(value / participations * 100 if participations else 0.0):.2f}%"
        for column, value in counts.items()
        if column != "Partecipazioni"
    }
    season_count = len(results)
    percentages["Partecipazioni"] = (
        f"{(participations / season_count * 100 if season_count else 0.0):.2f}%"
    )
    return pd.DataFrame(
        [
            {"Tipo": "Conteggi", "Nome": coach, **counts},
            {
                "Tipo": "Percentuali",
                "Nome": "",
                **{column: percentages[column] for column in counts},
            },
        ]
    )


def _save_history(
    coach: str,
    results: pd.Series,
    conversion: dict[str, float],
    output_path: Path,
) -> None:
    summary = _build_summary(coach, results)
    seasons = [f"{year}/{str(year + 1)[-2:]}" for year in results.index]
    values = [np.nan if result == "A" else conversion[result] for result in results]
    x_positions = np.arange(len(seasons))

    figure = plt.figure(figsize=(10, 7))
    grid = figure.add_gridspec(2, 1, height_ratios=[1, 3], hspace=0.25)
    table_axis = figure.add_subplot(grid[0])
    chart_axis = figure.add_subplot(grid[1])

    table_axis.axis("off")
    table = table_axis.table(
        cellText=summary.values,
        colLabels=summary.columns,
        cellLoc="center",
        colLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    header_colour = "#243447"
    row_colours = ("#F5F7FA", "#E8EEF4")
    for (row, _column), cell in table.get_celld().items():
        cell.set_edgecolor("white")
        cell.set_linewidth(1.2)
        if row == 0:
            cell.set_facecolor(header_colour)
            cell.set_text_props(color="white", weight="bold")
        else:
            cell.set_facecolor(row_colours[(row - 1) % 2])

    chart_axis.plot(x_positions, values, marker="o", linewidth=2)
    chart_axis.set_xlabel("Stagione")
    chart_axis.set_ylabel("Valore del risultato")
    chart_axis.set_xticks(x_positions, seasons)
    chart_axis.set_yticks(sorted(set(conversion.values())))
    chart_axis.grid(True, alpha=0.3)
    figure.suptitle(f"Risultati per stagione - {coach}", fontsize=16, fontweight="bold")
    figure.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def _safe_file_name(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "_", str(name).strip().lower()).strip("_") or "coach"


def _load_config() -> dict:
    with (PROJECT_ROOT / "configs" / "config.yaml").open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _output_directory(config: dict, last_year: int) -> Path:
    return PROJECT_ROOT / config["reports"]["output_dir"] / f"{last_year}_{last_year + 1}"


if __name__ == "__main__":
    main()
