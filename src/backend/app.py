"""Flask API server for the ARP Assessment platform."""
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import timedelta
from sqlalchemy.exc import SQLAlchemyError
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from src.backend.config import get_settings
from src.backend.database import init_db, SessionLocal, get_db
from src.backend.models import User, UserRole, AuditLog
from src.backend.security import create_access_token as create_jwt_token, verify_token
from src.backend.data_generator import generate_mock_data, clear_mock_data
from src.agents.orchestrator import AgentOrchestrator

settings = get_settings()

# Create Flask app
app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = settings.SECRET_KEY
app.config["JWT_ALGORITHM"] = settings.JWT_ALGORITHM

# Setup extensions
CORS(app)
jwt = JWTManager(app)


# ============= INITIALIZATION =============

@app.before_request
def initialize():
    """Initialize database on first request."""
    if not hasattr(app, "db_initialized"):
        try:
            init_db()
            app.db_initialized = True
        except Exception as e:
            print(f"Database initialization error: {e}")


# ============= AUTHENTICATION =============

@app.route("/api/auth/login", methods=["POST"])
def login():
    """Login endpoint."""
    data = request.get_json()
    username = data.get("username")
    
    # Mock authentication - in production, verify credentials properly
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    # Check if user exists
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        
        print(f"LOGIN: User {username}, found: {user is not None}")
        if user:
            print(f"LOGIN: Role {user.role}")
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Create JWT token
        token = create_jwt_token(
            data={"sub": user.username, "role": user.role.value},
            expires_delta=timedelta(hours=settings.JWT_EXPIRATION_HOURS)
        )
        
        return jsonify({
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "username": user.username,
                "role": user.role.value,
                "email": user.email,
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route("/api/auth/verify", methods=["POST"])
def verify():
    """Verify token endpoint."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Authorization header missing"}), 401
    
    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return jsonify({"error": "Invalid authorization header"}), 401
    
    token = parts[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    return jsonify({"valid": True, "user": payload.get("sub")}), 200


# ============= AGENT QUERIES =============

@app.route("/api/agent/query", methods=["POST"])
def agent_query():
    """Query the AI agent."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Authorization required"}), 401
    
    parts = auth_header.split()
    if len(parts) != 2:
        return jsonify({"error": "Invalid authorization header"}), 401
    
    token = parts[1]
    payload = verify_token(token)
    
    if not payload:
        return jsonify({"error": "Invalid or expired token"}), 401
    
    username = payload.get("sub")
    data = request.get_json()
    question = data.get("question")
    
    if not question:
        return jsonify({"error": "Question required"}), 400
    
    db = SessionLocal()
    try:
        # Get user
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Execute query through orchestrator
        orchestrator = AgentOrchestrator(db)
        result = orchestrator.execute_query(user, question)
        
        return jsonify(result), 200
    
    except Exception as e:
        # Log error
        print(f"Agent query error: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


# ============= DATA ENDPOINTS =============

@app.route("/api/data/portfolio", methods=["GET"])
def get_portfolio():
    """Get portfolio data."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Authorization required"}), 401
    
    payload = verify_token(auth_header.split()[1])
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        from src.backend.tools import ToolContext, get_portfolio_summary
        context = ToolContext(db, user)
        
        # Always try to get portfolio summary for authenticated users
        result = get_portfolio_summary(context)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route("/api/data/trades", methods=["GET"])
def get_trades():
    """Get trades data."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Authorization required"}), 401
    
    payload = verify_token(auth_header.split()[1])
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        from src.backend.tools import ToolContext, get_recent_trades
        context = ToolContext(db, user)
        
        if not context.check_access("get_recent_trades"):
            return jsonify({"error": "Access denied"}), 403
        
        result = get_recent_trades(context)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


@app.route("/api/data/risk-alerts", methods=["GET"])
def get_alerts():
    """Get risk alerts."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Authorization required"}), 401
    
    payload = verify_token(auth_header.split()[1])
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        from src.backend.tools import ToolContext, get_risk_alerts
        context = ToolContext(db, user)
        
        if not context.check_access("get_risk_alerts"):
            return jsonify({"error": "Access denied"}), 403
        
        result = get_risk_alerts(context)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


# ============= AUDIT LOGS =============

@app.route("/api/audit/logs", methods=["GET"])
def get_audit_logs():
    """Get audit logs."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        return jsonify({"error": "Authorization required"}), 401
    
    payload = verify_token(auth_header.split()[1])
    if not payload:
        return jsonify({"error": "Invalid token"}), 401
    
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == payload.get("sub")).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        # Check permission
        from src.backend.rbac import Permission, RBAC
        if not RBAC.has_permission(user.role, Permission.VIEW_AUDIT_LOGS):
            return jsonify({"error": "Access denied"}), 403
        
        # Get logs
        logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(100).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                "id": log.id,
                "user": log.user,
                "role": log.role,
                "question": log.question,
                "tools_called": json.loads(log.tools_called) if log.tools_called else [],
                "allowed": log.allowed,
                "denial_reason": log.denial_reason,
                "timestamp": log.timestamp.isoformat(),
            })
        
        return jsonify({"logs": logs_data}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


# ============= HEALTH & SETUP =============

@app.route("/api/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/api/setup/init-data", methods=["POST"])
def init_data():
    """Initialize mock data."""
    db = SessionLocal()
    try:
        # Clear existing data
        clear_mock_data(db)
        
        # Generate new data
        generate_mock_data(db)
        
        return jsonify({"message": "Mock data initialized"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()


# ============= ERROR HANDLERS =============

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors."""
    return jsonify({"error": "Internal server error"}), 500


if __name__ == "__main__":
    app.run(host=settings.API_HOST, port=settings.API_PORT, debug=settings.API_DEBUG)
