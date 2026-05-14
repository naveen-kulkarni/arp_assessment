"""Mock data generator for the ARP Assessment platform."""
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.backend.models import (
    User, UserRole, PortfolioHolding, Trade, MarketPrice, RiskRule, AuditLog
)


def generate_mock_data(db: Session):
    """Generate mock data for testing."""
    
    # Create users
    users = [
        User(username="analyst@local", email="analyst@local", role=UserRole.ANALYST),
        User(username="risk@local", email="risk@local", role=UserRole.RISK),
        User(username="manager@local", email="manager@local", role=UserRole.MANAGER),
        User(username="intern@local", email="intern@local", role=UserRole.INTERN),
    ]
    
    for user in users:
        db.merge(user)
    
    # Create portfolio holdings
    symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "BTC", "ETH"]
    asset_classes = {
        "AAPL": "stocks",
        "MSFT": "stocks",
        "GOOGL": "stocks",
        "AMZN": "stocks",
        "NVDA": "stocks",
        "BTC": "crypto",
        "ETH": "crypto",
    }
    
    for symbol in symbols:
        holding = PortfolioHolding(
            symbol=symbol,
            quantity=random.uniform(10, 500),
            purchase_price=random.uniform(50, 500),
            current_price=random.uniform(50, 600),
            asset_class=asset_classes.get(symbol, "stocks"),
        )
        db.merge(holding)
    
    # Create trades
    for _ in range(20):
        trade_date = datetime.utcnow() - timedelta(days=random.randint(0, 30))
        trade = Trade(
            symbol=random.choice(symbols),
            trade_type=random.choice(["buy", "sell"]),
            quantity=random.uniform(1, 100),
            price=random.uniform(50, 500),
            trade_date=trade_date,
            risk_score=random.randint(1, 100),
            status=random.choice(["completed", "flagged"]) if random.random() > 0.8 else "completed",
            reason_flagged="High concentration" if random.random() > 0.7 else None,
        )
        db.merge(trade)
    
    # Create market prices
    for symbol in symbols:
        market_price = MarketPrice(
            symbol=symbol,
            price=random.uniform(50, 600),
            change_percent=random.uniform(-10, 10),
            volume=random.uniform(1000000, 100000000),
        )
        db.merge(market_price)
    
    # Create risk rules
    risk_rules = [
        RiskRule(
            name="Max Asset Exposure",
            description="No single asset should exceed 30% of portfolio",
            rule_type="exposure_limit",
            threshold=30.0,
            is_active=True,
        ),
        RiskRule(
            name="Volatility Check",
            description="Trades with daily volatility > 15% require review",
            rule_type="volatility_check",
            threshold=15.0,
            is_active=True,
        ),
        RiskRule(
            name="Sector Correlation",
            description="Highly correlated trades need approval",
            rule_type="correlation_check",
            threshold=0.85,
            is_active=True,
        ),
    ]
    
    for rule in risk_rules:
        db.merge(rule)
    
    db.commit()


def clear_mock_data(db: Session):
    """Clear all mock data."""
    db.query(AuditLog).delete()
    db.query(RiskRule).delete()
    db.query(MarketPrice).delete()
    db.query(Trade).delete()
    db.query(PortfolioHolding).delete()
    db.query(User).delete()
    db.commit()
