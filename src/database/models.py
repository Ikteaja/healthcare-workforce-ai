# =============================================================
# src/database/models.py
# =============================================================
# This file defines the structure of your database tables.
# Think of it as designing a form before printing it.
#
# SQLAlchemy reads these classes and creates real tables
# inside data/workforce.db automatically when the app starts.
#
# THREE TABLES:
#   1. Staff    — who works here
#   2. Shift    — who works when and where
#   3. Schedule — how many staff each department needs per week
# =============================================================

from sqlalchemy import (
    Column,  # defines a column in a table
    Integer,  # number column type
    String,  # text column type
    Date,  # date column type (2026-05-20)
    Time,  # time column type (07:00)
    ForeignKey,  # links one table to another
)
from sqlalchemy.orm import declarative_base, relationship

# Base is the parent class all tables inherit from
# SQLAlchemy uses it to track all your table definitions
Base = declarative_base()


# =============================================================
# TABLE 1: Staff
# =============================================================
# Stores information about every employee.
# One row = one person.
#
# Example row:
# id=1, name="Sarah Johnson", role="Nurse", department="ICU"
# =============================================================


class Staff(Base):

    # The real table name in the database file
    __tablename__ = "staff"

    # Unique ID — auto-increments (1, 2, 3...)
    # Every table needs a primary key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Full name of the staff member
    # nullable=False means this field is required — cannot be empty
    name = Column(String(100), nullable=False)

    # Job role — Nurse, Doctor, Admin, Manager etc.
    role = Column(String(50), nullable=False)

    # Which department they belong to — ICU, ER, Ward A etc.
    department = Column(String(50), nullable=False)

    # Email address — optional (nullable=True by default)
    email = Column(String(100))

    # Phone number — optional
    phone = Column(String(20))

    # Employment status — Active or Inactive
    # default="Active" means new records get Active automatically
    status = Column(String(20), default="Active")

    # This links Staff to their Shifts
    # One staff member can have many shifts
    shifts = relationship("Shift", back_populates="staff")

    # This makes printing a Staff object readable
    def __repr__(self):
        return f"<Staff {self.name} | {self.role} | {self.department}>"


# =============================================================
# TABLE 2: Shift
# =============================================================
# Stores every work shift assignment.
# One row = one person working one shift on one day.
#
# Example row:
# id=1, staff_id=1, date=2026-05-20,
# start=07:00, end=15:00, ward="Ward A", type="morning"
# =============================================================


class Shift(Base):

    __tablename__ = "shifts"

    # Unique ID for this shift record
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Links to Staff table — which staff member is working
    # ForeignKey means this value must exist in staff.id
    staff_id = Column(Integer, ForeignKey("staff.id"), nullable=False)

    # The date of this shift
    date = Column(Date, nullable=False)

    # What time the shift starts
    start_time = Column(Time, nullable=False)

    # What time the shift ends
    end_time = Column(Time, nullable=False)

    # Which ward or area they are working in
    ward = Column(String(50), nullable=False)

    # Type of shift — morning, evening, or night
    shift_type = Column(String(20))

    # Notes about this shift — optional
    notes = Column(String(200))

    # Links back to the Staff table
    # This lets you do: shift.staff.name
    staff = relationship("Staff", back_populates="shifts")

    def __repr__(self):
        return f"<Shift {self.staff_id} | {self.date} | {self.ward}>"


# =============================================================
# TABLE 3: Schedule
# =============================================================
# Stores the minimum staffing requirements per department
# per week. Used to check if a department is understaffed.
#
# Example row:
# id=1, department="ICU", week_start=2026-05-18,
# min_staff_required=5
# =============================================================


class Schedule(Base):

    __tablename__ = "schedules"

    # Unique ID for this schedule record
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Which department this schedule is for
    department = Column(String(50), nullable=False)

    # The Monday of the week this schedule covers
    week_start = Column(Date, nullable=False)

    # Minimum number of staff needed this week
    min_staff_required = Column(Integer, nullable=False)

    # Maximum staff allowed (to avoid overstaffing)
    max_staff_allowed = Column(Integer)

    def __repr__(self):
        return f"<Schedule {self.department} | week {self.week_start} | min {self.min_staff_required}>"
