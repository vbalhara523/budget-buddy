import pytest

from budgetbuddy import db


@pytest.fixture
def conn(tmp_path):
    c = db.connect(str(tmp_path / "test.db"))
    yield c
    c.close()


def test_add_and_list_expense(conn):
    db.add_expense(conn, "2026-10-05", "food", 120, "lunch")
    rows = db.list_expenses(conn)
    assert len(rows) == 1
    assert rows[0]["category"] == "Food"        # category is normalised
    assert rows[0]["amount"] == 120


def test_negative_amount_rejected(conn):
    with pytest.raises(ValueError):
        db.add_expense(conn, "2026-10-05", "food", -10)


def test_bad_date_rejected(conn):
    with pytest.raises(ValueError):
        db.add_expense(conn, "05-10-2026", "food", 10)


def test_empty_category_rejected(conn):
    with pytest.raises(ValueError):
        db.add_expense(conn, "2026-10-05", "  ", 10)


def test_filter_by_month_and_category(conn):
    db.add_expense(conn, "2026-09-10", "food", 100)
    db.add_expense(conn, "2026-10-10", "food", 200)
    db.add_expense(conn, "2026-10-11", "travel", 300)
    assert len(db.list_expenses(conn, month="2026-10")) == 2
    assert len(db.list_expenses(conn, month="2026-10", category="travel")) == 1


def test_delete_expense(conn):
    new_id = db.add_expense(conn, "2026-10-05", "fun", 50)
    assert db.delete_expense(conn, new_id) is True
    assert db.delete_expense(conn, new_id) is False


def test_set_budget_updates_existing(conn):
    db.set_budget(conn, "food", 2000)
    db.set_budget(conn, "Food", 2500)
    assert db.get_budgets(conn) == {"Food": 2500}


def test_import_skips_invalid_rows(conn, tmp_path):
    f = tmp_path / "data.csv"
    f.write_text(
        "date,category,amount,note\n"
        "2026-10-01,food,100,ok\n"
        "2026-10-02,food,-5,negative\n"
        "bad-date,food,50,bad\n"
    )
    imported, skipped = db.import_csv(conn, str(f))
    assert (imported, skipped) == (1, 2)
