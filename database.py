# database.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
from config import DATABASE_URL

if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set. Please configure it in environment variables.")

# Base class for models
Base = declarative_base()

# Engine
engine = create_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True,   # helps avoid stale connections on Render
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db():
    """Dependency to get a DB session (FastAPI-style / can be used in Flask too)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection() -> bool:
    """
    Returns True if DB is reachable, otherwise False.
    You can call this in a /health route.
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connected successfully")
        return True
    except SQLAlchemyError as e:
        print("❌ Database connection failed:", str(e))
        return False


def init_db():
    """
    Import models and create tables in the connected database.
    Call this once on startup.
    """
    # Import models so that they are registered with Base
    from models import Project, Client, Contact, Subscriber  # noqa: F401

    Base.metadata.create_all(bind=engine)
    print("🛠️ Tables created (if they did not already exist).")


# Optional: run tests when executed directly
if __name__ == "__main__":
    if test_connection():
        init_db()
