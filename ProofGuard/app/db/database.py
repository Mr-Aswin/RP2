from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# Locate the main ProofGuard project folder
BASE_DIR = Path(__file__).resolve().parents[2]

# Database file location
DB_PATH = BASE_DIR / "proofguard.db"

# SQLite connection
DB_URL = f"sqlite:///{DB_PATH.as_posix()}"

# Creat the db engine
engine = create_engine(
    DB_URL,
    connect_args={"check_same_thread": False}
)

# Creating db sessions
SessionLocal = sessionmaker(
    autocommit = False,
    autoflush= False,
    bind= engine
)

# Base class for our db tables
class Base(DeclarativeBase):
    pass