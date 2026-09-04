"""Generate the all-time palmares for the configured period."""

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import yaml
from tabulate import tabulate

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.data_loader import load_results
from src.statistics import build_palmares


def main() -> None:
    config = _load_config()
    years = config["year_selection"]
    output_directory = _output_directory(config, years["last_year"])
    results = load_results(
        PROJECT_ROOT / config["data"]["file_path"],
        years["first_year"],
        years["last_year"],
    )
    palmares = build_palmares(results)
    csv_output_path = output_directory / "palmares.csv"
    image_output_path = output_directory / "palmares.png"
    palmares.to_csv(csv_output_path, index=False)
    _save_table_image(palmares, image_output_path, years["last_year"])

    print(tabulate(palmares, headers="keys", tablefmt="fancy_grid", showindex=False))
    print(f"\nSaved: {csv_output_path}")
    print(f"Saved: {image_output_path}")


def _save_table_image(palmares, output_path: Path, last_year: int) -> None:
    """Save a readable, presentation-ready rendering of the palmares."""
    row_count, column_count = palmares.shape
    figure_width = max(10, column_count * 1.7)
    figure_height = max(3, 1.3 + row_count * 0.48)
    figure, axis = plt.subplots(figsize=(figure_width, figure_height))
    axis.axis("off")

    table = axis.table(
        cellText=palmares.values,
        colLabels=palmares.columns,
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

    title = f"Palmarès all-time ({last_year}/{last_year + 1})"
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
        / "palmares"
    )
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
