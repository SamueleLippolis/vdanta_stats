"""
run_rankings.py
Entry point: load data from config, compute both rankings, print and save results.

Usage:
    python scripts/run_rankings.py
"""

import sys
import os
from pathlib import Path

import yaml
from tabulate import tabulate

# Allow imports from src/ when running from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_loader import extract_original_data
from src.rankings import compute_historical_ranking, compute_current_ranking


# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "config.yaml"

with open(CONFIG_PATH) as f:
    cfg = yaml.safe_load(f)

FILE_PATH        = cfg["data"]["file_path"]
FIRST_YEAR_EVER  = cfg["data"]["first_year_ever"]
SSN_YEAR         = cfg["season"]["ssn_year"]
CURRENT_YEAR     = cfg["season"]["current_year"]
REPORTS_DIR      = Path(__file__).resolve().parent.parent / cfg["reports"]["output_dir"]
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

original_data = extract_original_data(FILE_PATH)


# ---------------------------------------------------------------------------
# Historical ranking
# ---------------------------------------------------------------------------

num_seasons = SSN_YEAR - FIRST_YEAR_EVER + 1
hist_df = compute_historical_ranking(players=original_data, num_seasons=num_seasons)

print(f"\n=== Historical Ranking — up to {SSN_YEAR}/{SSN_YEAR + 1} ===")
print(tabulate(hist_df, headers="keys", tablefmt="fancy_grid"))

ssn_year_spring   = SSN_YEAR + 1
hist_df.to_csv(f"{REPORTS_DIR}/historical_ranking_after_{SSN_YEAR}_{ssn_year_spring}.csv", index=True)


# ---------------------------------------------------------------------------
# Current (weighted) ranking
# ---------------------------------------------------------------------------

ranking_name      = f"Ranking after {SSN_YEAR}/{ssn_year_spring}"
how_many_years_back = CURRENT_YEAR - SSN_YEAR - 1

only_one_year_available  = SSN_YEAR == FIRST_YEAR_EVER
only_two_years_available = (not only_one_year_available) and (SSN_YEAR - 1 == FIRST_YEAR_EVER)

curr_df = compute_current_ranking(
    players=original_data,
    ranking_name=ranking_name,
    how_many_years_back=how_many_years_back,
    only_two_years_available=only_two_years_available,
    only_one_year_available=only_one_year_available,
)

print(f"\n=== {ranking_name} ===")
print(tabulate(curr_df, headers="keys", tablefmt="fancy_grid"))

curr_df.to_csv(f"{REPORTS_DIR}/ranking_after_{SSN_YEAR}_{ssn_year_spring}.csv", index=True)

print(f"\nCSV reports saved to: {REPORTS_DIR}")
