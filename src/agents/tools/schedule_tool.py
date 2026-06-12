# =============================================================
# src/agents/tools/schedule_tool.py
# =============================================================
# PURPOSE:
#   A LangChain tool that queries the SQLite database
#   for staff schedules, shift assignments, and ward coverage.
#
# HOW IT WORKS:
#   Queries workforce.db directly using SQLAlchemy.
#   Returns formatted staff and shift information.
#
# CALLED BY: orchestrator.py when agent picks this tool
# QUERIES:   data/workforce.db — Staff and Shift tables
# =============================================================

from langchain.tools import tool
from src.database.db import SessionLocal
from src.database.models import Staff, Shift


@tool
def schedule_tool(question: str) -> str:
    """
    Use this tool for questions about:
    - Who is working on a specific date or ward
    - Staff shift assignments and schedules
    - Which nurses or doctors are on duty
    - Ward coverage and staffing levels
    - Morning, evening, or night shift assignments
    - Staff names, roles, and departments

    Input: the scheduling question as a string
    Output: staff and shift information from the database
    """

    db = SessionLocal()

    try:
        # Get all staff
        all_staff = db.query(Staff).all()

        # Get all shifts with staff details
        all_shifts = db.query(Shift).all()

        # Build readable staff list
        staff_info = []
        for s in all_staff:
            staff_info.append(
                f"{s.name} | Role: {s.role} | "
                f"Dept: {s.department} | Status: {s.status}"
            )

        # Build readable shift list
        shift_info = []
        for sh in all_shifts:
            staff = db.query(Staff).filter(Staff.id == sh.staff_id).first()
            staff_name = staff.name if staff else "Unknown"
            shift_info.append(
                f"{staff_name} | Date: {sh.date} | "
                f"Ward: {sh.ward} | "
                f"Time: {sh.start_time}-{sh.end_time} | "
                f"Type: {sh.shift_type}"
            )

        result = "STAFF IN DATABASE:\n"
        result += "\n".join(staff_info)
        result += "\n\nSHIFT SCHEDULE:\n"
        result += "\n".join(shift_info)

        return result

    except Exception as e:
        return f"Error querying schedule database: {e}"

    finally:
        db.close()
