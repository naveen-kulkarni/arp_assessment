"""Tests for security module."""
import pytest
from datetime import timedelta
from src.backend.security import create_access_token, verify_token, extract_token_from_header


def test_create_access_token():
    """Test JWT token creation."""
    token = create_access_token({"sub": "testuser", "role": "analyst"})
    assert token is not None
    assert isinstance(token, str)


def test_verify_valid_token():
    """Test token verification with valid token."""
    token = create_access_token({"sub": "testuser", "role": "analyst"})
    payload = verify_token(token)
    
    assert payload is not None
    assert payload["sub"] == "testuser"
    assert payload["role"] == "analyst"


def test_verify_invalid_token():
    """Test token verification with invalid token."""
    payload = verify_token("invalid-token")
    assert payload is None


def test_extract_token_valid_header():
    """Test extracting token from valid header."""
    header = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"
    token = extract_token_from_header(header)
    assert token == "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9"


def test_extract_token_invalid_header():
    """Test extracting token from invalid header."""
    assert extract_token_from_header(None) is None
    assert extract_token_from_header("Bearer") is None
    assert extract_token_from_header("Basic token") is None
    assert extract_token_from_header("InvalidFormat") is None


def test_token_expiration():
    """Test token expiration."""
    token = create_access_token(
        {"sub": "testuser"},
        expires_delta=timedelta(seconds=-1)  # Already expired
    )
    payload = verify_token(token)
    assert payload is None
