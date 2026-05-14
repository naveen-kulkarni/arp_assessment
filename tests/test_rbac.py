"""Tests for RBAC system."""
import pytest
from src.backend.models import UserRole
from src.backend.rbac import RBAC, Permission


def test_analyst_permissions():
    """Test analyst role permissions."""
    assert RBAC.has_permission(UserRole.ANALYST, Permission.VIEW_PORTFOLIO_SUMMARY)
    assert RBAC.has_permission(UserRole.ANALYST, Permission.VIEW_MARKET_DATA)
    assert not RBAC.has_permission(UserRole.ANALYST, Permission.VIEW_TRADES)
    assert not RBAC.has_permission(UserRole.ANALYST, Permission.VIEW_AUDIT_LOGS)


def test_risk_permissions():
    """Test risk role permissions."""
    assert RBAC.has_permission(UserRole.RISK, Permission.VIEW_PORTFOLIO)
    assert RBAC.has_permission(UserRole.RISK, Permission.VIEW_TRADES)
    assert RBAC.has_permission(UserRole.RISK, Permission.VIEW_RISK_ALERTS)
    assert RBAC.has_permission(UserRole.RISK, Permission.MANAGE_RISK_RULES)
    assert not RBAC.has_permission(UserRole.RISK, Permission.VIEW_AUDIT_LOGS)


def test_manager_permissions():
    """Test manager role permissions."""
    assert RBAC.has_permission(UserRole.MANAGER, Permission.VIEW_PORTFOLIO_SUMMARY)
    assert RBAC.has_permission(UserRole.MANAGER, Permission.VIEW_AUDIT_LOGS)
    assert not RBAC.has_permission(UserRole.MANAGER, Permission.VIEW_PORTFOLIO)
    assert not RBAC.has_permission(UserRole.MANAGER, Permission.VIEW_TRADES)


def test_intern_permissions():
    """Test intern role permissions."""
    assert RBAC.has_permission(UserRole.INTERN, Permission.VIEW_PORTFOLIO_SUMMARY)
    assert not RBAC.has_permission(UserRole.INTERN, Permission.VIEW_PORTFOLIO)
    assert not RBAC.has_permission(UserRole.INTERN, Permission.VIEW_TRADES)
    assert not RBAC.has_permission(UserRole.INTERN, Permission.VIEW_AUDIT_LOGS)


def test_tool_access_analyst():
    """Test tool access for analyst."""
    assert RBAC.check_tool_access(UserRole.ANALYST, "get_portfolio_summary")
    assert RBAC.check_tool_access(UserRole.ANALYST, "get_market_data")
    assert not RBAC.check_tool_access(UserRole.ANALYST, "get_recent_trades")


def test_tool_access_risk():
    """Test tool access for risk."""
    assert RBAC.check_tool_access(UserRole.RISK, "get_portfolio_summary")
    assert RBAC.check_tool_access(UserRole.RISK, "get_recent_trades")
    assert RBAC.check_tool_access(UserRole.RISK, "get_risk_alerts")
    assert not RBAC.check_tool_access(UserRole.RISK, "view_audit_logs")


def test_tool_access_manager():
    """Test tool access for manager."""
    assert RBAC.check_tool_access(UserRole.MANAGER, "get_portfolio_summary")
    assert not RBAC.check_tool_access(UserRole.MANAGER, "get_recent_trades")


def test_tool_access_intern():
    """Test tool access for intern."""
    assert RBAC.check_tool_access(UserRole.INTERN, "get_portfolio_summary")
    assert not RBAC.check_tool_access(UserRole.INTERN, "get_recent_trades")
    assert not RBAC.check_tool_access(UserRole.INTERN, "get_risk_alerts")
