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
    
    # Generate mock data
    generate_mock_data(db)
    
    yield db
    
    # Cleanup
    clear_mock_data(db)
    db.close()
