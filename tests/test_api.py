"""API integration tests."""
import pytest
import json
from flask import Flask
from src.backend.app import app as flask_app
from src.backend.database import SessionLocal, init_db
from src.backend.data_generator import generate_mock_data


@pytest.fixture
def client():
    """Create test client."""
    flask_app.config['TESTING'] = True
    
    with flask_app.test_client() as client:
        with flask_app.app_context():
            # Clear database before each test
            db = SessionLocal()
            from sqlalchemy import text
            # Drop and recreate tables
            db.execute(text("DROP TABLE IF EXISTS audit_logs"))
            db.execute(text("DROP TABLE IF EXISTS risk_rules"))
            db.execute(text("DROP TABLE IF EXISTS market_prices"))
            db.execute(text("DROP TABLE IF EXISTS trades"))
            db.execute(text("DROP TABLE IF EXISTS portfolio_holdings"))
            db.execute(text("DROP TABLE IF EXISTS users"))
            db.commit()
            db.close()
            
            init_db()
            db = SessionLocal()
            generate_mock_data(db)
            db.close()
        
        yield client


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'healthy'


def test_login_valid_user(client):
    """Test login with valid user."""
    response = client.post('/api/auth/login', json={'username': 'analyst@local'})
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'access_token' in data
    assert data['user']['role'] == 'analyst'


def test_login_invalid_user(client):
    """Test login with invalid user."""
    response = client.post('/api/auth/login', json={'username': 'nonexistent@local'})
    assert response.status_code == 404


def test_login_missing_username(client):
    """Test login without username."""
    response = client.post('/api/auth/login', json={})
    assert response.status_code == 400


def test_verify_token(client):
    """Test token verification."""
    # Get token
    response = client.post('/api/auth/login', json={'username': 'analyst@local'})
    token = json.loads(response.data)['access_token']
    
    # Verify token
    response = client.post(
        '/api/auth/verify',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['valid'] == True
    assert data['user'] == 'analyst@local'


def test_verify_invalid_token(client):
    """Test verification of invalid token."""
    response = client.post(
        '/api/auth/verify',
        headers={'Authorization': 'Bearer invalid-token'}
    )
    assert response.status_code == 401


def test_init_data(client):
    """Test data initialization endpoint."""
    response = client.post('/api/setup/init-data')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'message' in data


def test_portfolio_endpoint_unauthorized(client):
    """Test portfolio endpoint without auth."""
    response = client.get('/api/data/portfolio')
    assert response.status_code == 401


def test_portfolio_endpoint_authorized(client):
    """Test portfolio endpoint with auth."""
    # Get token
    response = client.post('/api/auth/login', json={'username': 'analyst@local'})
    token = json.loads(response.data)['access_token']
    
    # Get portfolio
    response = client.get(
        '/api/data/portfolio',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'exposures' in data


def test_access_denied_for_intern(client):
    """Test that intern cannot access trades."""
    # Get intern token
    response = client.post('/api/auth/login', json={'username': 'intern@local'})
    token = json.loads(response.data)['access_token']
    
    # Try to get trades (should be denied)
    response = client.get(
        '/api/data/trades',
        headers={'Authorization': f'Bearer {token}'}
    )
    # Should be 403 Forbidden
    assert response.status_code == 403


def test_agent_query_analyst(client):
    """Test AI agent query with analyst role."""
    # Get token
    response = client.post('/api/auth/login', json={'username': 'analyst@local'})
    token = json.loads(response.data)['access_token']
    
    # Query agent
    response = client.post(
        '/api/agent/query',
        json={'question': 'What is our portfolio value?'},
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'answer' in data
    assert 'question' in data


def test_audit_logs_manager_only(client):
    """Test that only managers can view audit logs."""
    # Test with analyst (should fail)
    response = client.post('/api/auth/login', json={'username': 'analyst@local'})
    token = json.loads(response.data)['access_token']
    
    response = client.get(
        '/api/audit/logs',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 403
    
    # Test with manager (should succeed)
    response = client.post('/api/auth/login', json={'username': 'manager@local'})
    token = json.loads(response.data)['access_token']
    
    response = client.get(
        '/api/audit/logs',
        headers={'Authorization': f'Bearer {token}'}
    )
    assert response.status_code == 200
