"""
Budget Buddy - a small expense tracker for the terminal.

Examples:
    python main.py import data/sample_expenses.csv
    python main.py add 250 food "Lunch with friends"
    python main.py budget food 3000
    python main.py summary --month 2026-10
    python main.py chart
"""
import argparse
import sys
from datetime import date

from budgetbuddy import analytics, charts, db


def cmd_add(conn, args):
    when = args.date or date.today().isoformat()
    new_id = db.add_expense(conn, when, args.category, args.amount, args.note)
    print(f"Added expense #{new_id}: Rs {args.amount:.2f} on {args.category.title()} ({when})")


def cmd_list(conn, args):
    rows = db.list_expenses(conn, args.month, args.category)
    if not rows:
        print("No expenses found.")
        return
    print(f"{'ID':<5}{'DATE':<12}{'CATEGORY':<14}{'AMOUNT':>10}  NOTE")
    for r in rows[: args.limit]:
        print(f"{r['id']:<5}{r['date']:<12}{r['category']:<14}{r['amount']:>10.2f}  {r['note']}")
    if len(rows) > args.limit:
        print(f"... and {len(rows) - args.limit} more (use --limit)")


def cmd_delete(conn, args):
    if db.delete_expense(conn, args.id):
        print(f"Deleted expense #{args.id}")
    else:
        print(f"No expense with id {args.id}")


def cmd_budget(conn, args):
    if args.category is None:
        budgets = db.get_budgets(conn)
        if not budgets:
            print("No budgets set yet. Example: python main.py budget food 3000")
        for cat, limit in budgets.items():
            print(f"{cat:<14}Rs {limit:.2f}")
        return
    db.set_budget(conn, args.category, args.limit)
    print(f"Budget for {args.category.title()} set to Rs {args.limit:.2f} per month")


def cmd_summary(conn, args):
    month = args.month or analytics.latest_month(conn)
    if not month:
        print("No data yet. Add expenses or import the sample csv first.")
        return
    df = analytics.expenses_df(conn, month)
    if df.empty:
        print(f"No expenses in {month}.")
        return

    print(f"\n=== Summary for {month} ===")
    print(f"Total spent    : Rs {df['amount'].sum():.2f}")
    print(f"Transactions   : {len(df)}")
    print(f"Daily average  : Rs {analytics.daily_average(df):.2f}")

    print("\nBy category:")
    for cat, total in analytics.category_totals(df).items():
        print(f"  {cat:<14}Rs {total:>9.2f}")

    status = analytics.budget_status(df, db.get_budgets(conn))
    if status:
        print("\nBudgets:")
        for s in status:
            flag = {"OK": "  ", "WARNING": "! ", "OVER": "!!"}[s["status"]]
            print(f" {flag}{s['category']:<12}{s['spent']:>9.2f} / {s['limit']:<8.0f} {s['percent']:>6.1f}%  {s['status']}")
    print()


def cmd_chart(conn, args):
    month = args.month or analytics.latest_month(conn)
    if not month:
        print("No data to plot.")
        return
    df = analytics.expenses_df(conn, month)
    p1 = charts.category_chart(analytics.category_totals(df), db.get_budgets(conn), month)
    p2 = charts.trend_chart(analytics.monthly_totals(analytics.expenses_df(conn)))
    print(f"Saved {p1}")
    print(f"Saved {p2}")


def cmd_import(conn, args):
    imported, skipped = db.import_csv(conn, args.file)
    print(f"Imported {imported} expenses, skipped {skipped} invalid rows.")


def build_parser():
    parser = argparse.ArgumentParser(description="Budget Buddy - track expenses and budgets.")
    parser.add_argument("--db", default=db.DEFAULT_DB, help="database file (default: budget.db)")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("add", help="add an expense")
    p.add_argument("amount", type=float)
    p.add_argument("category")
    p.add_argument("note", nargs="?", default="")
    p.add_argument("--date", help="YYYY-MM-DD (default: today)")
    p.set_defaults(func=cmd_add)

    p = sub.add_parser("list", help="list expenses")
    p.add_argument("--month", help="YYYY-MM")
    p.add_argument("--category")
    p.add_argument("--limit", type=int, default=20)
    p.set_defaults(func=cmd_list)

    p = sub.add_parser("delete", help="delete an expense by id")
    p.add_argument("id", type=int)
    p.set_defaults(func=cmd_delete)

    p = sub.add_parser("budget", help="set or show monthly budgets")
    p.add_argument("category", nargs="?")
    p.add_argument("limit", nargs="?", type=float)
    p.set_defaults(func=cmd_budget)

    p = sub.add_parser("summary", help="monthly summary with budget alerts")
    p.add_argument("--month", help="YYYY-MM (default: latest month with data)")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("chart", help="save charts to the output folder")
    p.add_argument("--month", help="YYYY-MM")
    p.set_defaults(func=cmd_chart)

    p = sub.add_parser("import", help="import expenses from a csv file")
    p.add_argument("file")
    p.set_defaults(func=cmd_import)
    return parser


def main():
    args = build_parser().parse_args()
    if args.command == "budget" and args.category and args.limit is None:
        print("Usage: python main.py budget <category> <limit>")
        sys.exit(1)
    conn = db.connect(args.db)
    try:
        args.func(conn, args)
    except (ValueError, FileNotFoundError) as err:
        print("Error:", err)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
