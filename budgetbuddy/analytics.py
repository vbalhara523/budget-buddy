"""Summaries and budget checks using pandas."""
import pandas as pd

WARN_AT = 0.8   # warn when 80% of a budget is used


def expenses_df(conn, month=None):
    query = "SELECT id, date, category, amount, note FROM expenses"
    params = []
    if month:
        query += " WHERE substr(date, 1, 7) = ?"
        params.append(month)
    df = pd.read_sql_query(query, conn, params=params)
    df["date"] = pd.to_datetime(df["date"])
    return df


def latest_month(conn):
    row = conn.execute("SELECT MAX(substr(date, 1, 7)) AS m FROM expenses").fetchone()
    return row["m"]


def category_totals(df):
    """Total spent per category, biggest first."""
    if df.empty:
        return pd.Series(dtype=float)
    return df.groupby("category")["amount"].sum().sort_values(ascending=False)


def monthly_totals(df):
    """Total spent per month -> Series indexed by 'YYYY-MM'."""
    if df.empty:
        return pd.Series(dtype=float)
    months = df["date"].dt.strftime("%Y-%m")
    return df.groupby(months)["amount"].sum().sort_index()


def budget_status(df, budgets):
    """
    Compares spending with budgets for the given (already filtered) dataframe.
    Returns a list of dicts sorted by percentage used.
    """
    spent = category_totals(df)
    result = []
    for category, limit in budgets.items():
        used = float(spent.get(category, 0.0))
        pct = used / limit
        if pct > 1:
            status = "OVER"
        elif pct >= WARN_AT:
            status = "WARNING"
        else:
            status = "OK"
        result.append({
            "category": category,
            "spent": round(used, 2),
            "limit": limit,
            "percent": round(pct * 100, 1),
            "status": status,
        })
    return sorted(result, key=lambda r: r["percent"], reverse=True)


def daily_average(df):
    if df.empty:
        return 0.0
    days = (df["date"].max() - df["date"].min()).days + 1
    return round(df["amount"].sum() / days, 2)
