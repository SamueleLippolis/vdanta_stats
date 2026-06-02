"""
rankings.py
Core logic for computing historical and weighted current rankings.
"""

import pandas as pd
from tabulate import tabulate


# ---------------------------------------------------------------------------
# Historical ranking
# ---------------------------------------------------------------------------

class PlayerStats:
    """Aggregates win/qualification/participation/relegation counts."""

    def __init__(self, player: list[str]):
        self.name = player[0]
        self.wins = player.count("W")
        self.qualifications = player.count("W") + player.count("Q")
        self.participations = (
            player.count("W") + player.count("Q")
            + player.count("N") + player.count("R")
        )
        self.relegations = player.count("R")

    def to_dict(self) -> dict:
        return {
            "Wins": self.wins,
            "Qualifications": self.qualifications,
            "Participations": self.participations,
            "Relegations": self.relegations,
        }


def compute_historical_ranking(players: list[list[str]], num_seasons: int) -> pd.DataFrame:
    """
    Compute the historical ranking up to `num_seasons` seasons.

    Sort order: most wins → most qualifications → most participations → fewest relegations.

    Parameters
    ----------
    players     : list of player rows (name + result letters).
    num_seasons : number of seasons to consider (1-indexed from the first).

    Returns
    -------
    Sorted DataFrame with columns: Name, Wins, Qualifications, Participations, Relegations.
    """
    corrected = [p[: num_seasons + 1] for p in players]
    stats_list = [PlayerStats(p) for p in corrected]

    data = {s.name: s.to_dict() for s in stats_list}
    df = pd.DataFrame(data).T

    df = df.sort_values(
        by=["Wins", "Qualifications", "Participations", "Relegations"],
        ascending=[False, False, False, True],
    )
    df = df.reset_index().rename(columns={"index": "Name"})
    df.index += 1
    return df


# ---------------------------------------------------------------------------
# Weighted current ranking
# ---------------------------------------------------------------------------

_SCORE_MAP = {"W": 10, "Q": 8, "N": 6, "A": 5.75, "R": 4}


def translate_player(player: list) -> list:
    """Replace result letters with numeric scores."""
    return [player[0]] + [_SCORE_MAP.get(item, item) for item in player[1:]]


def _weighted_score(values: list[float], weights: list[float]) -> float:
    """Dot product of values and weights, multiplied by 10 and rounded."""
    return round(sum(v * w for v, w in zip(values, weights)) * 10)


def calculate_weighted_score(player: list, how_many_years_back: int = 0) -> tuple[str, int]:
    """3-year weighted score: α = (0.2, 0.3, 0.5) oldest→newest."""
    name = player[0]
    scores = player[1:]
    idx = -(1 + how_many_years_back)
    window = [scores[idx - 2], scores[idx - 1], scores[idx]]
    return name, _weighted_score(window, [0.2, 0.3, 0.5])


def calculate_weighted_score_2years(player: list, how_many_years_back: int = 0) -> tuple[str, int]:
    """2-year weighted score: α = (0.35, 0.65)."""
    name = player[0]
    scores = player[1:]
    idx = -(1 + how_many_years_back)
    window = [scores[idx - 1], scores[idx]]
    return name, _weighted_score(window, [0.35, 0.65])


def calculate_weighted_score_1year(player: list, how_many_years_back: int = 0) -> tuple[str, int]:
    """1-year score: full weight on single season."""
    name = player[0]
    scores = player[1:]
    idx = -(1 + how_many_years_back)
    return name, _weighted_score([scores[idx]], [1.0])


def compute_current_ranking(
    players: list[list[str]],
    ranking_name: str = "Ranking",
    how_many_years_back: int = 0,
    only_two_years_available: bool = False,
    only_one_year_available: bool = False,
) -> pd.DataFrame:
    """
    Compute the weighted current ranking.

    Parameters
    ----------
    players                  : list of player rows (name + result letters).
    ranking_name             : column label for the score column.
    how_many_years_back      : 0 = current season, 1 = previous, etc.
    only_two_years_available : use 2-year weights.
    only_one_year_available  : use 1-year weight.

    Returns
    -------
    Sorted DataFrame with columns: Name, <ranking_name>.
    """
    rows = []
    for player in players:
        translated = translate_player(player)
        if only_one_year_available:
            name, score = calculate_weighted_score_1year(translated, how_many_years_back)
        elif only_two_years_available:
            name, score = calculate_weighted_score_2years(translated, how_many_years_back)
        else:
            name, score = calculate_weighted_score(translated, how_many_years_back)
        rows.append((name, score))

    df = pd.DataFrame(rows, columns=["Name", ranking_name])
    df = df.sort_values(by=ranking_name, ascending=False).reset_index(drop=True)
    df.index += 1
    return df
