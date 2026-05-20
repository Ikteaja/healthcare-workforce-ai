# =============================================================
# scripts/check_db.py
# =============================================================
# UTILITY SCRIPT — run this manually anytime you want to
# inspect what is inside your workforce.db database.
#
# It shows:
#   - All tables that exist
#   - All columns in each table
#   - All rows of data saved in each table
#
# HOW TO RUN:
#   cd C:\Users\Ikteaja.Hasan\Projects\healthcare-workforce-ai
#   python scripts/check_db.py
#
# WHEN TO USE:
#   - After running init_db() to confirm tables were created
#   - After adding sample data to confirm it was saved
#   - Any time you want to see what is in the database
# =============================================================

from sqlalchemy import create_engine, inspect, text

# Connect to the database file
engine = create_engine("sqlite:///data/workforce.db")
inspector = inspect(engine)

# ── SECTION 1: Show all tables and their columns ─────────────
print("=" * 50)
print("DATABASE STRUCTURE")
print("=" * 50)

tables = inspector.get_table_names()

if not tables:
    print("No tables found — run init_db() first")
else:
    for table in tables:
        cols = inspector.get_columns(table)
        print(f"\nTable: {table}")
        print("-" * 30)
        for col in cols:
            nullable = "required" if not col["nullable"] else "optional"
            print(f"  - {col['name']} ({col['type']}) [{nullable}]")

# ── SECTION 2: Show all rows in each table ───────────────────
print("\n" + "=" * 50)
print("DATA IN DATABASE")
print("=" * 50)

with engine.connect() as conn:
    for table in tables:
        print(f"\nTable: {table}")
        print("-" * 30)

        # Count rows
        count = conn.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar()
        print(f"Total rows: {count}")

        if count == 0:
            print("  No data yet")
        else:
            # Show all rows
            rows = conn.execute(
                text(f"SELECT * FROM {table}")
            ).fetchall()
            for row in rows:
                print(f"  {dict(row._mapping)}")

print("\n" + "=" * 50)
print("Check complete")
print("=" * 50)