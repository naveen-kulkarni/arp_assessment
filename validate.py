"""Validation script to check if platform is ready."""
import sys
import os

def check_imports():
    """Check if all imports work."""
    print("Checking imports...")
    try:
        from src.backend.config import get_settings
        from src.backend.database import init_db, SessionLocal
        from src.backend.models import User, UserRole
        from src.backend.security import create_access_token
        from src.backend.rbac import RBAC
        from src.backend.tools import TOOLS
        from src.agents.orchestrator import AgentOrchestrator
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        return False


def check_database():
    """Check if database can be initialized."""
    print("\nChecking database...")
    try:
        from src.backend.database import init_db, SessionLocal
        from src.backend.data_generator import generate_mock_data
        
        # Initialize
        init_db()
        print("✅ Database initialized")
        
        # Generate data
        db = SessionLocal()
        generate_mock_data(db)
        print("✅ Mock data generated")
        
        # Check data
        from src.backend.models import User
        users = db.query(User).all()
        print(f"✅ {len(users)} users created")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ Database check failed: {e}")
        return False


def check_rbac():
    """Check RBAC system."""
    print("\nChecking RBAC...")
    try:
        from src.backend.models import UserRole
        from src.backend.rbac import RBAC, Permission
        
        # Check analyst
        assert RBAC.has_permission(UserRole.ANALYST, Permission.VIEW_PORTFOLIO_SUMMARY)
        print("✅ Analyst permissions correct")
        
        # Check risk
        assert RBAC.has_permission(UserRole.RISK, Permission.VIEW_TRADES)
        print("✅ Risk permissions correct")
        
        # Check manager
        assert RBAC.has_permission(UserRole.MANAGER, Permission.VIEW_AUDIT_LOGS)
        print("✅ Manager permissions correct")
        
        # Check intern
        assert RBAC.has_permission(UserRole.INTERN, Permission.VIEW_PORTFOLIO_SUMMARY)
        assert not RBAC.has_permission(UserRole.INTERN, Permission.VIEW_TRADES)
        print("✅ Intern permissions correct")
        
        return True
    except Exception as e:
        print(f"❌ RBAC check failed: {e}")
        return False


def check_security():
    """Check security module."""
    print("\nChecking security...")
    try:
        from src.backend.security import create_access_token, verify_token
        
        # Create token
        token = create_access_token({"sub": "test", "role": "analyst"})
        print("✅ Token created")
        
        # Verify token
        payload = verify_token(token)
        assert payload is not None
        assert payload["sub"] == "test"
        print("✅ Token verified")
        
        return True
    except Exception as e:
        print(f"❌ Security check failed: {e}")
        return False


def check_tools():
    """Check tools."""
    print("\nChecking tools...")
    try:
        from src.backend.tools import TOOLS
        
        expected_tools = [
            "get_portfolio_summary",
            "get_asset_exposure",
            "get_recent_trades",
            "get_risk_alerts",
            "get_high_risk_trades",
            "get_market_data",
            "check_risk_rules",
        ]
        
        for tool in expected_tools:
            assert tool in TOOLS, f"Missing tool: {tool}"
        
        print(f"✅ All {len(TOOLS)} tools available")
        return True
    except Exception as e:
        print(f"❌ Tools check failed: {e}")
        return False


def main():
    """Run all checks."""
    print("\n" + "="*50)
    print("ARP Assessment Platform - Validation")
    print("="*50 + "\n")
    
    checks = [
        ("Imports", check_imports),
        ("RBAC", check_rbac),
        ("Security", check_security),
        ("Tools", check_tools),
        ("Database", check_database),
    ]
    
    results = []
    for name, check in checks:
        try:
            results.append(check())
        except Exception as e:
            print(f"❌ {name} check crashed: {e}")
            results.append(False)
    
    print("\n" + "="*50)
    print("Summary")
    print("="*50)
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"✅ All {total} checks passed!")
        print("\n🎉 Platform is ready to run!")
        print("\nNext steps:")
        print("1. Run locally: ./run_local.sh (Linux/macOS) or run_local.bat (Windows)")
        print("2. Or with Docker: docker compose up")
        print("\nThen open:")
        print("- Dashboard: http://localhost:8501")
        print("- API: http://localhost:8000")
        return 0
    else:
        print(f"⚠️  {total - passed} of {total} checks failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
