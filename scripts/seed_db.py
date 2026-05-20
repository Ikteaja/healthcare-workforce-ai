# =============================================================
# scripts/seed_db.py
# =============================================================
# Adds sample healthcare staff, shifts and schedules
# into workforce.db for testing and development.
#
# HOW TO RUN:
#   python scripts/seed_db.py
#
# WHEN TO RUN:
#   - Once after init_db() to populate test data
#   - After deleting workforce.db to start fresh
#
# WARNING:
#   Running this twice adds duplicate data.
#   To reset: delete data/workforce.db and run again.
# =============================================================

# Fix Python path so src/ module can be found
import sys
import os
sys.path.insert(0, os.path.abspath("."))

from datetime import date, time
from src.database.db import SessionLocal, init_db
from src.database.models import Staff, Shift, Schedule

# Make sure tables exist first
init_db()

db = SessionLocal()

# ── Check if data already exists ─────────────────────────────
existing = db.query(Staff).count()
if existing > 0:
    print(f"Database already has {existing} staff records.")
    print("Delete data/workforce.db and run again to reseed.")
    db.close()
    exit()

# ── SECTION 1: Add Staff ──────────────────────────────────────
print("Adding staff...")

staff_list = [
    Staff(
        name="Sarah Johnson",
        role="Nurse",
        department="ICU",
        email="sarah.johnson@hospital.com",
        phone="0712345001",
        status="Active"
    ),
    Staff(
        name="Ahmed Ali",
        role="Doctor",
        department="ER",
        email="ahmed.ali@hospital.com",
        phone="0712345002",
        status="Active"
    ),
    Staff(
        name="Lisa Chen",
        role="Admin",
        department="Ward A",
        email="lisa.chen@hospital.com",
        phone="0712345003",
        status="Active"
    ),
    Staff(
        name="James Brown",
        role="Nurse",
        department="ICU",
        email="james.brown@hospital.com",
        phone="0712345004",
        status="Active"
    ),
    Staff(
        name="Maria Garcia",
        role="Nurse",
        department="ER",
        email="maria.garcia@hospital.com",
        phone="0712345005",
        status="Active"
    ),
    Staff(
        name="David Wilson",
        role="Doctor",
        department="Ward A",
        email="david.wilson@hospital.com",
        phone="0712345006",
        status="Active"
    ),
]

db.add_all(staff_list)
db.commit()

# Refresh to get auto-generated IDs
for s in staff_list:
    db.refresh(s)

print(f"✅ Added {len(staff_list)} staff members")

# ── SECTION 2: Add Shifts ─────────────────────────────────────
print("Adding shifts...")

shifts = [
    # Sarah — ICU morning Monday
    Shift(
        staff_id=staff_list[0].id,
        date=date(2026, 5, 20),
        start_time=time(7, 0),
        end_time=time(15, 0),
        ward="ICU",
        shift_type="morning"
    ),
    # Ahmed — ER morning Monday
    Shift(
        staff_id=staff_list[1].id,
        date=date(2026, 5, 20),
        start_time=time(8, 0),
        end_time=time(16, 0),
        ward="ER",
        shift_type="morning"
    ),
    # James — ICU evening Monday
    Shift(
        staff_id=staff_list[3].id,
        date=date(2026, 5, 20),
        start_time=time(15, 0),
        end_time=time(23, 0),
        ward="ICU",
        shift_type="evening"
    ),
    # Maria — ER night Monday
    Shift(
        staff_id=staff_list[4].id,
        date=date(2026, 5, 20),
        start_time=time(23, 0),
        end_time=time(7, 0),
        ward="ER",
        shift_type="night"
    ),
    # Sarah — ICU morning Tuesday
    Shift(
        staff_id=staff_list[0].id,
        date=date(2026, 5, 21),
        start_time=time(7, 0),
        end_time=time(15, 0),
        ward="ICU",
        shift_type="morning"
    ),
    # David — Ward A morning Tuesday
    Shift(
        staff_id=staff_list[5].id,
        date=date(2026, 5, 21),
        start_time=time(8, 0),
        end_time=time(16, 0),
        ward="Ward A",
        shift_type="morning"
    ),
]

db.add_all(shifts)
db.commit()
print(f"✅ Added {len(shifts)} shifts")

# ── SECTION 3: Add Schedules ──────────────────────────────────
print("Adding schedules...")

schedules = [
    Schedule(
        department="ICU",
        week_start=date(2026, 5, 18),
        min_staff_required=3,
        max_staff_allowed=6
    ),
    Schedule(
        department="ER",
        week_start=date(2026, 5, 18),
        min_staff_required=4,
        max_staff_allowed=8
    ),
    Schedule(
        department="Ward A",
        week_start=date(2026, 5, 18),
        min_staff_required=2,
        max_staff_allowed=5
    ),
]

db.add_all(schedules)
db.commit()
print(f"✅ Added {len(schedules)} schedules")

db.close()

print("\n" + "=" * 40)
print("Seed complete. Run check_db.py to verify.")
print("=" * 40)
