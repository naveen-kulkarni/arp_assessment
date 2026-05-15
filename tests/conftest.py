"""Conftest for pytest."""
import pytest
import os
from src.backend.database import SessionLocal, init_db
from src.backend.data_generator import generate_mock_data, clear_mock_data


@pytest.fixture(scope="session")
def setup_test_db():
    """Setup test database for the session."""
    os.environ["DATABASE_URL"] = "sqlite:///test.db"
    init_db()
    yield
    # Cleanup
    if os.path.exists("test.db"):
        os.remove("test.db")


@pytest.fixture
def db_session(setup_test_db):
    """Create a fresh database session for each test."""
    db = SessionLocal()
    
    # Clear all data before generating fresh mock data
    from sqlalchemy import text
    try:
        db.execute(text("DELETE FROM audit_logs"))
        db.execute(text("DELETE FROM risk_rules"))
        db.execute(text("DELETE FROM market_prices"))
        db.execute(text("DELETE FROM trades"))
        db.execute(text("DELETE FROM portfolio_holdings"))
        db.execute(text("DELETE FROM users"))
        db.commit()
    except Exception:
        db.rollback()
    
    # Generate mock data
    generate_mock_data(db)
    db.commit()
    
    yield db
    
    # Cleanup
    try:
        db.execute(text("DELETE FROM audit_logs"))
        db.execute(text("DELETE FROM risk_rules"))
        db.execute(text("DELETE FROM market_prices"))
        db.execute(text("DELETE FROM trades"))
        db.execute(text("DELETE FROM portfolio_holdings"))
        db.execute(text("DELETE FROM users"))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
