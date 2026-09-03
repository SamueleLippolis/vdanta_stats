"""Generate the all-time palmares for the configured period."""

import sys
from pathlib import Path

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
    output_path = output_directory / "palmares.csv"
    palmares.to_csv(output_path, index=False)

    print(tabulate(palmares, headers="keys", tablefmt="fancy_grid", showindex=False))
    print(f"\nSaved: {output_path}")


def _load_config() -> dict:
    with (PROJECT_ROOT / "configs" / "config.yaml").open(encoding="utf-8") as stream:
        return yaml.safe_load(stream)


def _output_directory(config: dict, last_year: int) -> Path:
    path = PROJECT_ROOT / config["reports"]["output_dir"] / f"{last_year}_{last_year + 1}"
    path.mkdir(parents=True, exist_ok=True)
    return path


if __name__ == "__main__":
    main()
