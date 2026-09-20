"""
Database layer. Everything is stored in a small SQLite file (budget.db by default).

Tables:
    expenses(id, date, category, amount, note)
    budgets(category, monthly_limit)
"""
import csv
import sqlite3
from datetime import datetime

DEFAULT_DB = "budget.db"


def connect(path=DEFAULT_DB):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    init_db(conn)
    return conn


def init_db(conn):
    conn.execute(
        """CREATE TABLE IF NOT EXISTS expenses (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               date TEXT NOT NULL,
               category TEXT NOT NULL,
               amount REAL NOT NULL CHECK (amount > 0),
               note TEXT DEFAULT ''
           )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS budgets (
               category TEXT PRIMARY KEY,
               monthly_limit REAL NOT NULL CHECK (monthly_limit > 0)
           )"""
    )
    conn.commit()


def clean_category(name):
    name = (name or "").strip().title()
    if not name:
        raise ValueError("Category cannot be empty")
    return name


def check_date(text):
    try:
        datetime.strptime(text, "%Y-%m-%d")
    except ValueError:
        raise ValueError(f"Invalid date '{text}', use YYYY-MM-DD")
    return text


def add_expense(conn, date, category, amount, note=""):
    check_date(date)
    category = clean_category(category)
    amount = float(amount)
    if amount <= 0:
        raise ValueError("Amount must be greater than 0")
    cur = conn.execute(
        "INSERT INTO expenses (date, category, amount, note) VALUES (?, ?, ?, ?)",
        (date, category, amount, note),
    )
    conn.commit()
    return cur.lastrowid


def list_expenses(conn, month=None, category=None):
    """month is 'YYYY-MM'. Returns a list of rows, newest first."""
    query = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if month:
        query += " AND substr(date, 1, 7) = ?"
        params.append(month)
    if category:
        query += " AND category = ?"
        params.append(clean_category(category))
    query += " ORDER BY date DESC, id DESC"
    return conn.execute(query, params).fetchall()


def delete_expense(conn, expense_id):
    cur = conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    return cur.rowcount > 0


def set_budget(conn, category, limit):
    category = clean_category(category)
    limit = float(limit)
    if limit <= 0:
        raise ValueError("Budget must be greater than 0")
    conn.execute(
        "INSERT INTO budgets (category, monthly_limit) VALUES (?, ?) "
        "ON CONFLICT(category) DO UPDATE SET monthly_limit = excluded.monthly_limit",
        (category, limit),
    )
    conn.commit()


def get_budgets(conn):
    rows = conn.execute("SELECT category, monthly_limit FROM budgets").fetchall()
    return {r["category"]: r["monthly_limit"] for r in rows}


def import_csv(conn, path):
    """
    Imports expenses from a csv with columns: date,category,amount,note
    Bad rows are skipped, returns (imported, skipped).
    """
    imported = skipped = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                add_expense(conn, row["date"], row["category"], row["amount"], row.get("note", ""))
                imported += 1
            except (ValueError, KeyError):
                skipped += 1
    return imported, skipped
