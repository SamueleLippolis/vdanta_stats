"""Generate the next-season forecast with the rules from ranking_forcast.ipynb."""

import sys
from fractions import Fraction
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


def select_forecast_coaches(data: pd.DataFrame, forecast_year: int) -> list:
    """Legge le celle originali, prima che i vuoti siano convertiti in assenze."""
    season_years = pd.to_numeric(
        data.iloc[:, 0].astype(str).str.strip().str.split("/").str[0],
        errors="coerce",
    )
    season = data.loc[season_years == forecast_year]
    if len(season) != 1:
        raise ValueError(
            f"Attesa una sola riga per la stagione {forecast_year}: trovate {len(season)}."
        )
    entries = season.iloc[0, 1:]
    return [
        coach for coach, value in entries.items()
        if pd.isna(value) or (isinstance(value, str) and not value.strip())
    ]



FORECAST_POINTS = {"W": 20, "Q": 6, "N": 1, "A": 1, "R": -2}


def build_ranking_forcast(results: pd.DataFrame, last_year: int) -> pd.DataFrame:
    """Calcola la previsione sui risultati già selezionati tramite config."""
    recent_years = range(last_year - 2, last_year + 1)
    newcomer_score = Fraction(sum(FORECAST_POINTS[r] for r in ("R", "N", "Q")), 3)
    rows = []
    for coach in results.columns:
        history = results[coach]
        played = history[history != "A"]
        participations = len(played)
        if participations == 0:
            historical = Fraction(
                sum(FORECAST_POINTS[r] for r in "WQQNNNNRRR"), 10
            )
            recent = newcomer_score
        else:
            if participations < 3:
                # Sette risultati di base, risultati reali e N fino a dieci.
                historical_results = list("WQQRRRR") + played.tolist()
                historical_results += ["N"] * (10 - len(historical_results))
                historical = Fraction(
                    sum(FORECAST_POINTS[r] for r in historical_results), 10
                )
            else:
                historical = Fraction(sum(FORECAST_POINTS[r] for r in played), participations)
            recent_results = history.reindex(recent_years, fill_value="A")
            recent = Fraction(sum(FORECAST_POINTS[r] for r in recent_results), 3)
        rows.append({
            "Nome": coach,
            "Partecipazioni": participations,
            "History score": historical,
            "Last 3 years score": recent,
            "Score": historical + recent,
        })

    columns = ["Risultato stimato", "Nome", "Ranking score", "Partecipazioni", "History score", "Last 3 years score", "Score"]
    if not rows:
        return pd.DataFrame(columns=columns)

    # Frazioni esatte: somme matematicamente uguali ricevono la stessa posizione.
    rows.sort(key=lambda row: row["Score"], reverse=True)
    top_score = rows[0]["Score"]
    if top_score == 0:
        raise ValueError("Impossibile normalizzare: la somma massima T è zero.")

    previous_score = None
    position = 0
    for index, row in enumerate(rows, start=1):
        total = row["Score"]
        if total != previous_score:
            position = index
        row["Risultato stimato"] = position
        row["Ranking score"] = float(total / top_score * 100)
        previous_score = total
        for column in ("History score", "Last 3 years score", "Score"):
            row[column] = float(row[column])
    return pd.DataFrame(rows, columns=columns)


def _format_scores(ranking: pd.DataFrame) -> pd.DataFrame:
    formatted = ranking.copy()
    for column, decimals in {"Ranking score": 2, "History score": 3,
                             "Last 3 years score": 3, "Score": 3}.items():
        formatted[column] = formatted[column].map(lambda value: f"{value:.{decimals}f}")
    return formatted


def _save_table_image(ranking, output_path: Path, forecast_year: int) -> None:
    """Render the forecast using the same style as the palmares."""
    ranking = _format_scores(ranking)
    row_count, column_count = ranking.shape
    figure_width = max(10, column_count * 2.3)
    figure_height = max(3, 1.3 + row_count * 0.48)
    figure, axis = plt.subplots(figsize=(figure_width, figure_height))
    axis.axis("off")

    table = axis.table(
        cellText=ranking.values if row_count else [["—"] * column_count],
        colLabels=ranking.columns,
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

    title = f"Risultato stimato per la stagione {forecast_year}/{forecast_year + 1}"
    figure.suptitle(title, fontsize=18, fontweight="bold", color=header_colour)
    figure.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(figure)



def main() -> None:
    with (PROJECT_ROOT / "configs" / "config.yaml").open(encoding="utf-8") as stream:
        config = yaml.safe_load(stream)
    years = config["year_selection"]
    last_year = years["last_year"]
    forecast_year = last_year + 1
    data_path = PROJECT_ROOT / config["data"]["file_path"]
    coaches = select_forecast_coaches(pd.read_excel(data_path), forecast_year)
    results = load_results(data_path, years["first_year"], last_year)
    results = results.reindex(columns=coaches, fill_value="A")
    ranking = build_ranking_forcast(results, last_year)

    output_directory = (
        PROJECT_ROOT / config["reports"]["output_dir"]
        / f"{last_year}_{last_year + 1}" / "ranking_forecast"
    )
    output_directory.mkdir(parents=True, exist_ok=True)
    csv_path = output_directory / "ranking_forecast.csv"
    image_path = output_directory / "ranking_forecast.png"
    ranking.to_csv(csv_path, index=False)
    _save_table_image(ranking, image_path, forecast_year)

    print(f"Risultato stimato per la stagione {forecast_year}/{forecast_year + 1}")
    print(tabulate(_format_scores(ranking), headers="keys", tablefmt="fancy_grid",
                   showindex=False, disable_numparse=True))
    print(f"\nSaved: {csv_path}")
    print(f"Saved: {image_path}")


if __name__ == "__main__":
    main()
