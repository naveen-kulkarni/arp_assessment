"""Database models for the ARP Assessment platform."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Enum as SQLEnum
from sqlalchemy.sql import func
from enum import Enum
from .database import Base


class UserRole(str, Enum):
    """User role enumeration."""
    ANALYST = "analyst"
    RISK = "risk"
    MANAGER = "manager"
    INTERN = "intern"


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(SQLEnum(UserRole), default=UserRole.INTERN)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class PortfolioHolding(Base):
    """Portfolio holding model."""
    __tablename__ = "portfolio_holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    quantity = Column(Float)
    purchase_price = Column(Float)
    current_price = Column(Float)
    asset_class = Column(String)  # stocks, bonds, crypto, commodities
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class Trade(Base):
    """Trade model."""
    __tablename__ = "trades"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    trade_type = Column(String)  # buy, sell
    quantity = Column(Float)
    price = Column(Float)
    trade_date = Column(DateTime, index=True)
    risk_score = Column(Integer, default=0)  # 1-100
    status = Column(String, default="completed")  # pending, completed, flagged
    reason_flagged = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class MarketPrice(Base):
    """Market price model."""
    __tablename__ = "market_prices"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    change_percent = Column(Float)
    volume = Column(Float)
    timestamp = Column(DateTime, index=True, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())


class RiskRule(Base):
    """Risk rule model."""
    __tablename__ = "risk_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    description = Column(Text)
    rule_type = Column(String)  # exposure_limit, volatility_check, correlation_check
    threshold = Column(Float)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())


class AuditLog(Base):
    """Audit log for AI interactions and access."""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user = Column(String, index=True)
    role = Column(String)
    question = Column(Text)
    tools_called = Column(Text)  # JSON array of tool names
    result = Column(Text)  # Summary of result or error
    allowed = Column(Boolean)  # Whether the request was allowed
    denial_reason = Column(Text, nullable=True)
    timestamp = Column(DateTime, index=True, server_default=func.now())
