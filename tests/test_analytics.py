import pytest

from budgetbuddy import analytics, db


@pytest.fixture
def conn(tmp_path):
    c = db.connect(str(tmp_path / "test.db"))
    db.add_expense(c, "2026-09-03", "food", 500)
    db.add_expense(c, "2026-10-01", "food", 900)
    db.add_expense(c, "2026-10-04", "food", 400)
    db.add_expense(c, "2026-10-05", "travel", 600)
    yield c
    c.close()


def test_category_totals(conn):
    df = analytics.expenses_df(conn, "2026-10")
    totals = analytics.category_totals(df)
    assert totals["Food"] == 1300
    assert totals.index[0] == "Food"            # sorted biggest first


def test_monthly_totals(conn):
    totals = analytics.monthly_totals(analytics.expenses_df(conn))
    assert totals["2026-09"] == 500
    assert totals["2026-10"] == 1900


def test_latest_month(conn):
    assert analytics.latest_month(conn) == "2026-10"


def test_budget_status_levels(conn):
    df = analytics.expenses_df(conn, "2026-10")
    budgets = {"Food": 1000, "Travel": 700, "Fun": 500}
    result = {r["category"]: r for r in analytics.budget_status(df, budgets)}
    assert result["Food"]["status"] == "OVER"        # 1300 / 1000
    assert result["Travel"]["status"] == "WARNING"   # 600 / 700 = 85%
    assert result["Fun"]["status"] == "OK"           # nothing spent
    assert result["Food"]["percent"] == 130.0


def test_empty_dataframe_is_handled(tmp_path):
    c = db.connect(str(tmp_path / "empty.db"))
    df = analytics.expenses_df(c)
    assert analytics.category_totals(df).empty
    assert analytics.daily_average(df) == 0.0
    c.close()
