# Budget Buddy

A command-line expense tracker for students. You log what you spend, set a monthly budget for each category, and Budget Buddy shows monthly summaries, warns you when a category is close to (or over) its limit, and saves charts of your spending.

I made this to practise working with SQLite and pandas together, and because I wanted something simple to track my own monthly expenses.

## Features

- Add, list and delete expenses (data is stored in a local SQLite database)
- Set a monthly budget per category
- Monthly summary: total spent, number of transactions, daily average, spending by category
- Budget alerts: `OK`, `WARNING` (80% or more used) and `OVER`
- Import expenses from a CSV file (invalid rows are skipped and counted)
- Charts saved as PNG: spending by category with budget lines, and a monthly trend
- Input validation (no negative amounts, dates must be `YYYY-MM-DD`, category cannot be empty)

## Tech used

Python 3.10+, SQLite (`sqlite3`), pandas, matplotlib, argparse, pytest

## Project structure

```
budget-buddy/
├── budgetbuddy/
│   ├── db.py          # SQLite: tables, add/list/delete, budgets, csv import
│   ├── analytics.py   # pandas summaries and budget status
│   └── charts.py      # matplotlib charts
├── data/
│   └── sample_expenses.csv   # 96 made-up rows (Aug-Oct 2026)
├── tests/
│   ├── test_db.py
│   └── test_analytics.py
├── main.py            # command line interface
└── requirements.txt
```

## Setup

```bash
git clone https://github.com/vbalhara523/budget-buddy.git
cd budget-buddy

python -m venv venv
# Windows:  venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

pip install -r requirements.txt
```

## Quick start with the sample data

```bash
python main.py import data/sample_expenses.csv

python main.py budget food 3500
python main.py budget travel 2800
python main.py budget study 3000
python main.py budget fun 2500
python main.py budget bills 2000

python main.py summary
python main.py chart
```

Output:

```
=== Summary for 2026-10 ===
Total spent    : Rs 13550.00
Transactions   : 31
Daily average  : Rs 501.85

By category:
  Food          Rs   3570.00
  Travel        Rs   2350.00
  Fun           Rs   2250.00
  Shopping      Rs   2190.00
  Study         Rs   1910.00
  Bills         Rs   1280.00

Budgets:
 !!Food          3570.00 / 3500      102.0%  OVER
 ! Fun           2250.00 / 2500       90.0%  WARNING
 ! Travel        2350.00 / 2800       83.9%  WARNING
   Bills         1280.00 / 2000       64.0%  OK
   Study         1910.00 / 3000       63.7%  OK
```

(The import says "skipped 3 invalid rows" because I left 3 broken rows at the end of the sample file on purpose, to test validation.)

## All commands

| Command | What it does |
|---|---|
| `python main.py add 250 food "Lunch"` | add an expense (today's date) |
| `python main.py add 250 food "Lunch" --date 2026-10-20` | add with a specific date |
| `python main.py list --month 2026-10 --category food` | list expenses (filters are optional) |
| `python main.py delete 12` | delete expense with id 12 |
| `python main.py budget food 3000` | set a monthly budget |
| `python main.py budget` | show all budgets |
| `python main.py summary --month 2026-10` | monthly summary (default: latest month with data) |
| `python main.py chart` | save charts to the `output/` folder |
| `python main.py import file.csv` | import expenses from a csv |

CSV format for importing: `date,category,amount,note`

Use `--db other.db` before the command to use a different database file.

## Running the tests

```bash
pytest
```

## How it works

- `db.py` handles all SQL. Categories are normalised (`food`, `FOOD` and ` Food ` all become `Food`) and the database itself also rejects amounts that are zero or negative.
- `analytics.py` loads expenses into a pandas DataFrame and uses `groupby` for the category and monthly totals.
- A budget is `WARNING` when 80% or more is used and `OVER` when spending is above the limit.
- `charts.py` uses matplotlib's non-interactive backend, so charts are saved as files and no window opens.

## Limitations

- Single user, no login, data is only stored locally
- Budgets are monthly and the same for every month
- No income tracking or recurring expenses yet
- Amounts are in rupees but the currency is not configurable

## What I learned

- Using SQLite from Python, including parameterised queries to avoid SQL injection
- Reading SQL results directly into pandas with `read_sql_query`
- Building a CLI with subcommands in argparse
- Testing database code using temporary databases in pytest

## Future improvements

- Recurring expenses (rent, subscriptions)
- Export a monthly PDF report
- Simple Streamlit dashboard
- Different budgets for different months

## Author

**Vallabh Balhara** – B.Tech CSE student
[LinkedIn](https://linkedin.com/in/vallabhbalhara) · [GitHub](https://github.com/vbalhara523)

## License

MIT
