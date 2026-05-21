# =============================================================
# src/database/db.py
# =============================================================
# Creates the connection to workforce.db
# and builds all tables defined in models.py
# =============================================================

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from src.database.models import Base

load_dotenv()

# Path to the database file
DB_PATH = os.getenv("DB_PATH", "./data/workforce.db")

# Create engine — this is the connection to the file
engine = create_engine(f"sqlite:///{DB_PATH}", echo=True)

# Session factory — used to query the database
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Creates all tables in workforce.db"""
    Base.metadata.create_all(engine)
    print("✅ Database tables created successfully")


def get_db():
    """Returns a database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
