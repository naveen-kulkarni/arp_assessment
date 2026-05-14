"""Tool functions for AI agents to call."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from .models import PortfolioHolding, Trade, MarketPrice, RiskRule, User, UserRole
from .rbac import RBAC


class ToolContext:
    """Context for tool execution."""
    
    def __init__(self, db: Session, user: User):
        self.db = db
        self.user = user
        self.role = user.role
    
    def check_access(self, tool_name: str) -> bool:
        """Check if user has access to a tool."""
        return RBAC.check_tool_access(self.role, tool_name)


def get_portfolio_summary(context: ToolContext) -> Dict[str, Any]:
    """Get portfolio summary."""
    if not context.check_access("get_portfolio_summary"):
        return {"error": "Access denied"}
    
    holdings = context.db.query(PortfolioHolding).all()
    
    total_value = 0
    asset_allocation = {}
    
    for holding in holdings:
        holding_value = holding.quantity * holding.current_price
        total_value += holding_value
        
        asset_class = holding.asset_class
        if asset_class not in asset_allocation:
            asset_allocation[asset_class] = 0
        asset_allocation[asset_class] += holding_value
    
    # Calculate percentages
    allocation_percent = {}
    for asset_class, value in asset_allocation.items():
        allocation_percent[asset_class] = round((value / total_value * 100) if total_value > 0 else 0, 2)
    
    return {
        "total_portfolio_value": round(total_value, 2),
        "holdings_count": len(holdings),
        "asset_allocation": asset_allocation,
        "allocation_percentage": allocation_percent,
    }


def get_asset_exposure(context: ToolContext) -> Dict[str, Any]:
    """Get asset exposure details."""
    if not context.check_access("get_asset_exposure"):
        return {"error": "Access denied"}
    
    holdings = context.db.query(PortfolioHolding).all()
    portfolio_summary = get_portfolio_summary(context)
    
    if "error" in portfolio_summary:
        return portfolio_summary
    
    total_value = portfolio_summary["total_portfolio_value"]
    
    exposures = []
    for holding in holdings:
        holding_value = holding.quantity * holding.current_price
        exposure_percent = (holding_value / total_value * 100) if total_value > 0 else 0
        
        exposures.append({
            "symbol": holding.symbol,
            "quantity": round(holding.quantity, 2),
            "current_price": round(holding.current_price, 2),
            "position_value": round(holding_value, 2),
            "exposure_percentage": round(exposure_percent, 2),
            "asset_class": holding.asset_class,
        })
    
    # Sort by exposure percentage
    exposures.sort(key=lambda x: x["exposure_percentage"], reverse=True)
    
    # Identify overexposed assets (>30%)
    overexposed = [e for e in exposures if e["exposure_percentage"] > 30]
    
    return {
        "exposures": exposures,
        "overexposed_assets": overexposed,
    }


def get_recent_trades(context: ToolContext, days: int = 7) -> Dict[str, Any]:
    """Get recent trades."""
    if not context.check_access("get_recent_trades"):
        return {"error": "Access denied"}
    
    from datetime import datetime, timedelta
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    trades = context.db.query(Trade).filter(Trade.trade_date >= cutoff_date).all()
    
    trades_list = []
    for trade in trades:
        trades_list.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "type": trade.trade_type,
            "quantity": round(trade.quantity, 2),
            "price": round(trade.price, 2),
            "total": round(trade.quantity * trade.price, 2),
            "date": trade.trade_date.isoformat(),
            "status": trade.status,
            "risk_score": trade.risk_score,
        })
    
    return {
        "trades": trades_list,
        "total_trades": len(trades_list),
    }


def get_risk_alerts(context: ToolContext) -> Dict[str, Any]:
    """Get risk alerts."""
    if not context.check_access("get_risk_alerts"):
        return {"error": "Access denied"}
    
    alerts = []
    
    # Check for flagged trades
    flagged_trades = context.db.query(Trade).filter(Trade.status == "flagged").all()
    for trade in flagged_trades:
        alerts.append({
            "type": "flagged_trade",
            "symbol": trade.symbol,
            "reason": trade.reason_flagged,
            "risk_score": trade.risk_score,
            "severity": "high" if trade.risk_score > 70 else "medium",
        })
    
    # Check for overexposure
    asset_exposure = get_asset_exposure(context)
    if "overexposed_assets" in asset_exposure:
        for asset in asset_exposure["overexposed_assets"]:
            alerts.append({
                "type": "overexposure",
                "symbol": asset["symbol"],
                "exposure_percent": asset["exposure_percentage"],
                "severity": "high" if asset["exposure_percentage"] > 50 else "medium",
            })
    
    return {
        "alerts": alerts,
        "total_alerts": len(alerts),
        "high_severity": sum(1 for a in alerts if a["severity"] == "high"),
    }


def get_high_risk_trades(context: ToolContext, threshold: int = 70) -> Dict[str, Any]:
    """Get high risk trades."""
    if not context.check_access("get_high_risk_trades"):
        return {"error": "Access denied"}
    
    trades = context.db.query(Trade).filter(Trade.risk_score >= threshold).all()
    
    trades_list = []
    for trade in trades:
        trades_list.append({
            "id": trade.id,
            "symbol": trade.symbol,
            "type": trade.trade_type,
            "quantity": round(trade.quantity, 2),
            "price": round(trade.price, 2),
            "risk_score": trade.risk_score,
            "status": trade.status,
            "reason_flagged": trade.reason_flagged,
            "date": trade.trade_date.isoformat(),
        })
    
    return {
        "high_risk_trades": trades_list,
        "total": len(trades_list),
    }


def get_market_data(context: ToolContext) -> Dict[str, Any]:
    """Get current market data."""
    if not context.check_access("get_market_data"):
        return {"error": "Access denied"}
    
    prices = context.db.query(MarketPrice).all()
    
    market_data = []
    for price in prices:
        market_data.append({
            "symbol": price.symbol,
            "price": round(price.price, 2),
            "change_percent": round(price.change_percent, 2),
            "volume": int(price.volume),
        })
    
    return {
        "market_data": market_data,
        "total_symbols": len(market_data),
    }


def check_risk_rules(context: ToolContext) -> Dict[str, Any]:
    """Check risk rules and violations."""
    if not context.check_access("get_risk_alerts"):
        return {"error": "Access denied"}
    
    rules = context.db.query(RiskRule).filter(RiskRule.is_active == True).all()
    
    rules_list = []
    for rule in rules:
        rules_list.append({
            "id": rule.id,
            "name": rule.name,
            "description": rule.description,
            "threshold": rule.threshold,
            "type": rule.rule_type,
        })
    
    return {
        "rules": rules_list,
        "total_active_rules": len(rules_list),
    }


# Tool registry
TOOLS = {
    "get_portfolio_summary": get_portfolio_summary,
    "get_asset_exposure": get_asset_exposure,
    "get_recent_trades": get_recent_trades,
    "get_risk_alerts": get_risk_alerts,
    "get_high_risk_trades": get_high_risk_trades,
    "get_market_data": get_market_data,
    "check_risk_rules": check_risk_rules,
}
