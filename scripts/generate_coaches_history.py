"""Generate one statistics table and result history chart per coach."""

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
from src.statistics import COUNT_COLUMNS, count_results


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
        _build_summary(coach, results[coach]).to_csv(
            output_directory / f"{safe_name}_history.csv", index=False
        )
        _save_chart(coach, results[coach], conversion, output_directory / f"{safe_name}_history.png")

    print(f"Generated histories for {len(results.columns)} coaches in: {output_directory}")


def _build_summary(coach: str, results: pd.Series) -> pd.DataFrame:
    counts = count_results(results)
    participations = counts["Partecipazioni"]
    percentages = {
        column: (counts[column] / participations * 100 if participations else 0.0)
        for column in COUNT_COLUMNS
    }
    return pd.DataFrame(
        [
            {"Tipo": "Conteggi", "Nome": coach, **counts},
            {
                "Tipo": "Percentuali",
                "Nome": coach,
                **{column: f"{percentages[column]:.2f}%" for column in COUNT_COLUMNS},
            },
        ]
    )


def _save_chart(
    coach: str,
    results: pd.Series,
    conversion: dict[str, float],
    output_path: Path,
) -> None:
    seasons = [f"{year}/{str(year + 1)[-2:]}" for year in results.index]
    values = [np.nan if result == "A" else conversion[result] for result in results]
    x_positions = np.arange(len(seasons))

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(x_positions, values, marker="o", linewidth=2)
    axis.set_title(f"Risultati per stagione - {coach}")
    axis.set_xlabel("Stagione")
    axis.set_ylabel("Valore del risultato")
    axis.set_xticks(x_positions, seasons)
    axis.set_yticks(sorted(set(conversion.values())))
    axis.grid(True, alpha=0.3)
    figure.tight_layout()
    figure.savefig(output_path, dpi=150)
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
