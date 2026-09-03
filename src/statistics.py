"""Shared calculations for the palmares and coach histories."""

import pandas as pd


COUNT_COLUMNS = ["Vittorie", "Primi 3", "Partecipazioni", "Retrocessioni"]


def count_results(results: pd.Series) -> dict[str, int]:
    """Count results, with participations defined as W + Q + N + R."""
    return {
        "Vittorie": int((results == "W").sum()),
        "Primi 3": int((results == "Q").sum()),
        "Partecipazioni": int(results.isin({"W", "Q", "N", "R"}).sum()),
        "Retrocessioni": int((results == "R").sum()),
    }


def build_palmares(results: pd.DataFrame) -> pd.DataFrame:
    """Build a sorted palmares with competition-style tied positions."""
    rows = [{"Nome": coach, **count_results(results[coach])} for coach in results.columns]
    palmares = pd.DataFrame(rows).sort_values(
        COUNT_COLUMNS,
        ascending=[False, False, False, True],
        kind="stable",
    ).reset_index(drop=True)

    ranking_keys = list(zip(*(palmares[column] for column in COUNT_COLUMNS)))
    positions: list[int] = []
    previous_key = None
    for index, key in enumerate(ranking_keys, start=1):
        positions.append(positions[-1] if key == previous_key else index)
        previous_key = key

    palmares.insert(0, "Posizione", positions)
    return palmares
