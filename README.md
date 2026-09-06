# VDAnta Stats

Statistics and next-season forecasts for the “Rozzezza” fantasy-football group, originally known as “VDA” group. 

Three scripts turn the season dataset into tables and charts ready to share.

## Main features

### 1. Palmarès — `generate_palmares.py`

Builds a cumulative ranking over the configured seasons, with wins, second/third-place finishes, participations, and relegations. Coaches are sorted by wins, then second/third-place finishes, then participations (all descending), and finally relegations (ascending). Equal records share a position, using ranks such as `1, 2, 2, 4`.

Outputs a CSV, a styled PNG table, and a table in the terminal. In this report, the column labelled `Primi 3` counts `Q` results; wins are listed separately under `Vittorie`.

### 2. Coach history — `generate_coaches_history.py`

Creates one PNG per coach, combining a summary table with a season-by-season result chart. Absent seasons appear as gaps in the chart.

The summary includes counts and percentages:

- **Participations:** non-absent seasons (`W + Q + N + R`); the percentage uses all seasons in the configured period as its denominator.
- **Wins:** `W` results.
- **Top-three finishes:** `Q + W`, including the winner.
- **Neutral results:** `N` results.
- **Relegations:** `R` results.

All result percentages use the coach’s participations as their denominator. Percentages are shown as `0.00%` when the denominator is zero. Chart values come from `result_to_number_conversion` in the config.

### 3. Next-season forecast — `generate_ranking_forecast.py`

Estimates the ranking for the season starting in `last_year + 1`, using only the configured historical period. Only coaches with an empty cell (or whitespace) in the forecast season are included; `A` and any other non-empty value exclude a coach.

The calculation uses fixed weights: `W = 20`, `Q = 6`, `N = 1`, `A = 1`, and `R = -2`. These are independent of the chart conversion in the config.

- **History score:** average score across seasons actually played, excluding absences.
- **Last 3 years score:** total score for the final three seasons of the historical window, divided by three. Absences and seasons before the window starts contribute `1` each.
- **Newcomers:** coaches with no participations in the window receive `5/3` for each of the two scores.
- **Score:** History score + Last 3 years score.
- **Ranking score:** Score divided by the highest Score among selected participants, multiplied by 100. This is a relative score, not a probability of winning.

Coaches are ranked by Score, with exact ties sharing a position before display rounding. A highest Score of zero raises an error because normalization is undefined. Negative scores are retained; if the highest Score is negative, the ordering still follows Score. The forecast season must have exactly one row in the dataset.

Outputs a CSV, a styled PNG table matching the palmarès graphics, and a table in the terminal. The PNG title is generated automatically, for example: **“Risultato stimato per la stagione 2026/2027”**.

## How to use

### 1. Install dependencies

From the repository root, create and activate a virtual environment, then install the dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

On Windows PowerShell, activate it with `.venv\Scripts\Activate.ps1` instead.

### 2. Update the dataset

Edit `datasets/vdanta_piazzamenti.ods` (or the file specified in the config). The first column contains seasons such as `2025/26`; each remaining column represents one coach.

Add a column for each new coach and mark historical seasons they did not play with `A`. Add a row for the upcoming season:

- Leave the cells **empty for coaches who will participate**.
- Enter **`A` for coaches who will not participate**.

At the end of each season, replace participant blanks with their final result:

| Code | Meaning |
| --- | --- |
| `W` | Winner / first place |
| `Q` | Second or third place; excludes the winner |
| `N` | Neutral result: neither top three nor relegated |
| `R` | Relegated |
| `A` | Absent / did not participate |

For example:

| Season | Coach Alice | Coach Bob | New coach |
| --- | --- | --- | --- |
| 2025/26 | W | Q | A |
| 2026/27 | | A | |

Here, Alice and the new coach enter the 2026/2027 forecast; Bob does not. Keep all historical results filled in: empty cells in the historical window are treated as absences.

### 3. Configure the historical period

Edit `configs/config.yaml`:

```yaml
data:
  file_path: "datasets/vdanta_piazzamenti.ods"

year_selection:
  first_year: 2020 # means season 2020/21
  last_year: 2025 # means season 2025/26

result_to_number_conversion:
  W: 10
  Q: 8
  N: 6
  A: 6
  R: 4

reports:
  output_dir: "reports"
```

Use the **starting year** of each season. Set `last_year` to the last season whose results you want to include, and `first_year` to the start of the historical window. Both endpoints are included, and every season in that range must exist in the dataset.

With `last_year: 2025`, the reports cover results through **2025/2026** and the forecast targets **2026/2027**. Keep the ongoing or upcoming season outside the historical window.

### 4. Run the three scripts

From the repository root, with the virtual environment activated:

```bash
python scripts/generate_palmares.py
python scripts/generate_coaches_history.py
python scripts/generate_ranking_forecast.py
```

### 5. Find your reports

All outputs belong to the final historical season selected in the config, including the forecast for the following season. With `last_year: 2025`, the output structure is:

```text
reports/2025_2026/
├── palmares/
│   ├── palmares.csv
│   └── palmares.png
├── coaches_history/
│   └── <coach>_history.png
└── ranking_forecast/
    ├── ranking_forecast.csv
    └── ranking_forecast.png
```

Running the scripts again updates the corresponding files. Generated reports are excluded from Git by `.gitignore`.
