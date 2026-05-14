"""Tests for data generation."""
import pytest
from src.backend.models import (
    User, PortfolioHolding, Trade, MarketPrice, RiskRule, AuditLog
)


def test_users_created(db_session):
    """Test that mock users are created."""
    users = db_session.query(User).all()
    assert len(users) == 4
    
    usernames = {u.username for u in users}
    assert usernames == {"analyst@local", "risk@local", "manager@local", "intern@local"}


def test_portfolio_holdings_created(db_session):
    """Test that portfolio holdings are created."""
    holdings = db_session.query(PortfolioHolding).all()
    assert len(holdings) == 7
    
    symbols = {h.symbol for h in holdings}
    assert "AAPL" in symbols
    assert "BTC" in symbols


def test_trades_created(db_session):
    """Test that trades are created."""
    trades = db_session.query(Trade).all()
    assert len(trades) == 20
    
    # Check that trades have required fields
    for trade in trades:
        assert trade.symbol is not None
        assert trade.trade_type in ["buy", "sell"]
        assert trade.quantity > 0
        assert trade.price > 0


def test_market_prices_created(db_session):
    """Test that market prices are created."""
    prices = db_session.query(MarketPrice).all()
    assert len(prices) == 7  # One for each symbol


def test_risk_rules_created(db_session):
    """Test that risk rules are created."""
    rules = db_session.query(RiskRule).all()
    assert len(rules) == 3
    
    assert all(rule.is_active for rule in rules)


def test_audit_logs_table_empty(db_session):
    """Test that audit logs table starts empty."""
    logs = db_session.query(AuditLog).all()
    assert len(logs) == 0
