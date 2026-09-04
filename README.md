# VDAnta Stats

Statistics for the "Rozzezza" fantasy-football group, originally known as "VDA".

## Dataset

The first column contains seasons in the `YYYY/YY` format. Every other column is
a coach, and every cell contains one result code:

- `W`: win
- `Q`: qualification (top three)
- `N`: neutral result
- `A`: absent
- `R`: relegation

The number of participations is calculated as `W + Q + N + R`. An absent
season (`A`) is not a participation.

## Configuration

Edit `configs/config.yaml` to choose `first_year`, `last_year`, the numeric result
conversion, the dataset path, and the report directory. A year such as `2025`
represents the `2025/2026` season.

## Generate reports

Activate the virtual environment and run:

```bash
source .venv/bin/activate
python scripts/generate_palmares.py
python scripts/generate_coaches_history.py
```

The report folder name is derived automatically from `last_year`. For example,
`last_year: 2025` produces `reports/2025_2026/`. The palmares CSV and its visual
PNG table are saved inside the `palmares` subdirectory; every coach receives a
single PNG containing the summary table and history chart inside `coaches_history`.
