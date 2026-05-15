"""Role-Based Access Control (RBAC) and permissions."""
from enum import Enum
from typing import Set, Dict, List
from .models import UserRole


class Permission(str, Enum):
    """Permission definitions."""
    # Portfolio permissions
    VIEW_PORTFOLIO = "view_portfolio"
    VIEW_PORTFOLIO_SUMMARY = "view_portfolio_summary"
    
    # Trade permissions
    VIEW_TRADES = "view_trades"
    VIEW_HIGH_RISK_TRADES = "view_high_risk_trades"
    
    # Market permissions
    VIEW_MARKET_DATA = "view_market_data"
    
    # Risk permissions
    VIEW_RISK_ALERTS = "view_risk_alerts"
    MANAGE_RISK_RULES = "manage_risk_rules"
    
    # Audit permissions
    VIEW_AUDIT_LOGS = "view_audit_logs"


# Role to permissions mapping
ROLE_PERMISSIONS: Dict[UserRole, Set[Permission]] = {
    UserRole.ANALYST: {
        Permission.VIEW_PORTFOLIO,
        Permission.VIEW_MARKET_DATA,
        Permission.VIEW_PORTFOLIO_SUMMARY,
    },
    UserRole.RISK: {
        Permission.VIEW_PORTFOLIO,
        Permission.VIEW_PORTFOLIO_SUMMARY,
        Permission.VIEW_TRADES,
        Permission.VIEW_HIGH_RISK_TRADES,
        Permission.VIEW_MARKET_DATA,
        Permission.VIEW_RISK_ALERTS,
        Permission.MANAGE_RISK_RULES,
    },
    UserRole.MANAGER: {
        Permission.VIEW_PORTFOLIO_SUMMARY,
        Permission.VIEW_AUDIT_LOGS,
    },
    UserRole.INTERN: {
        Permission.VIEW_PORTFOLIO_SUMMARY,
    },
}


class RBAC:
    """Role-Based Access Control utility."""
    
    @staticmethod
    def has_permission(role: UserRole, permission: Permission) -> bool:
        """Check if role has permission."""
        return permission in ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def get_user_permissions(role: UserRole) -> Set[Permission]:
        """Get all permissions for a role."""
        return ROLE_PERMISSIONS.get(role, set())
    
    @staticmethod
    def check_tool_access(role: UserRole, tool_name: str) -> bool:
        """Check if user can access a specific tool."""
        # Map tools to required permissions
        tool_permissions = {
            "get_portfolio_summary": [Permission.VIEW_PORTFOLIO_SUMMARY],
            "get_recent_trades": [Permission.VIEW_TRADES],
            "get_asset_exposure": [Permission.VIEW_PORTFOLIO],
            "get_risk_alerts": [Permission.VIEW_RISK_ALERTS],
            "get_market_data": [Permission.VIEW_MARKET_DATA],
            "get_high_risk_trades": [Permission.VIEW_HIGH_RISK_TRADES],
        }
        
        required_permissions = tool_permissions.get(tool_name, [])
        user_permissions = RBAC.get_user_permissions(role)
        
        return any(perm in user_permissions for perm in required_permissions)
