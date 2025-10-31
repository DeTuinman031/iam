# app/auth/routes_api.py
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.auth.models import IAMUserAccount, IAMRole, IAMAuthLog, IAMAuthSession
from datetime import datetime
from sqlalchemy.exc import IntegrityError

api_bp = Blueprint("api", __name__, url_prefix="/api")


def log_auth_event(event_type: str, user_id: int = None, success: bool = True, details: str = None):
    """Helper to log authentication events."""
    try:
        log = IAMAuthLog(
            user_id=user_id,
            event_type=event_type,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            details=details or f"Event: {event_type}, Success: {success}"
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # Don't fail the request if logging fails
        pass


@api_bp.post("/auth/login")
def api_login():
    """REST API login endpoint."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"status": "error", "message": "Invalid request"}), 400
        
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return jsonify({"status": "error", "message": "Username and password required"}), 400
        
        user = IAMUserAccount.query.filter_by(username=username).first()
        
        if not user:
            log_auth_event("login_failed", success=False, details=f"User not found: {username}")
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
        if not user.verify_password(password):
            log_auth_event("login_failed", user_id=user.user_id, success=False, details="Invalid password")
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401
        
        # Check account status - use direct query to avoid method shadowing
        result = db.session.execute(
            db.text("SELECT CAST(is_active AS UNSIGNED) as is_active, CAST(is_locked AS UNSIGNED) as is_locked FROM iam_user_account WHERE user_id = :user_id"),
            {"user_id": user.user_id}
        ).fetchone()
        
        if result:
            is_active_val = bool(result[0]) if result[0] is not None else True
            is_locked_val = bool(result[1]) if result[1] is not None else False
            account_active = is_active_val and not is_locked_val
        else:
            account_active = True
        
        if not account_active:
            log_auth_event("login_failed", user_id=user.user_id, success=False, details="Account locked/inactive")
            return jsonify({"status": "error", "message": "Account disabled or locked"}), 403
        
        # Login successful
        login_user(user, remember=True)
        user.last_login_at = datetime.utcnow()
        db.session.commit()
        
        log_auth_event("login_success", user_id=user.user_id, success=True)
        
        # Return user info
        return jsonify({
            "status": "success",
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "roles": [role.role_name for role in user.roles],
                "auth_provider": user.auth_provider
            }
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.get("/auth/verify")
@login_required
def api_verify():
    """REST API verify session endpoint."""
    try:
        return jsonify({
            "authenticated": True,
            "user": {
                "user_id": current_user.user_id,
                "username": current_user.username,
                "email": current_user.email,
                "display_name": current_user.display_name,
                "roles": [role.role_name for role in current_user.roles],
                "auth_provider": current_user.auth_provider
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.post("/auth/logout")
@login_required
def api_logout():
    """REST API logout endpoint."""
    try:
        user_id = current_user.user_id if current_user else None
        logout_user()
        log_auth_event("logout", user_id=user_id, success=True)
        return jsonify({"status": "success", "message": "Logged out"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.get("/users")
@login_required
def api_users_list():
    """REST API list users endpoint."""
    try:
        # Get pagination params
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)  # Max 100 per page
        
        # Query users
        users_query = IAMUserAccount.query.order_by(IAMUserAccount.created_at.desc())
        pagination = users_query.paginate(page=page, per_page=per_page, error_out=False)
        
        users_data = []
        for user in pagination.items:
            # Get account status
            result = db.session.execute(
                db.text("SELECT CAST(is_active AS UNSIGNED) as is_active, CAST(is_locked AS UNSIGNED) as is_locked FROM iam_user_account WHERE user_id = :user_id"),
                {"user_id": user.user_id}
            ).fetchone()
            
            is_active_val = bool(result[0]) if result and result[0] is not None else True
            is_locked_val = bool(result[1]) if result and result[1] is not None else False
            
            users_data.append({
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "auth_provider": user.auth_provider,
                "roles": [role.role_name for role in user.roles],
                "is_active": is_active_val,
                "is_locked": is_locked_val,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        
        return jsonify({
            "users": users_data,
            "total": pagination.total,
            "page": page,
            "per_page": per_page,
            "pages": pagination.pages
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.get("/users/<int:user_id>")
@login_required
def api_user_detail(user_id):
    """REST API get user details endpoint."""
    try:
        user = IAMUserAccount.query.get_or_404(user_id)
        
        # Get account status
        result = db.session.execute(
            db.text("SELECT CAST(is_active AS UNSIGNED) as is_active, CAST(is_locked AS UNSIGNED) as is_locked FROM iam_user_account WHERE user_id = :user_id"),
            {"user_id": user.user_id}
        ).fetchone()
        
        is_active_val = bool(result[0]) if result and result[0] is not None else True
        is_locked_val = bool(result[1]) if result and result[1] is not None else False
        
        return jsonify({
            "user": {
                "user_id": user.user_id,
                "username": user.username,
                "email": user.email,
                "display_name": user.display_name,
                "phone_number": user.phone_number,
                "auth_provider": user.auth_provider,
                "roles": [role.role_name for role in user.roles],
                "is_active": is_active_val,
                "is_locked": is_locked_val,
                "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.get("/roles")
@login_required
def api_roles_list():
    """REST API list roles endpoint."""
    try:
        roles = IAMRole.query.order_by(IAMRole.role_name).all()
        
        roles_data = []
        for role in roles:
            user_count = len(role.users.all())
            roles_data.append({
                "role_id": role.role_id,
                "role_name": role.role_name,
                "role_description": role.role_description,
                "user_count": user_count
            })
        
        return jsonify({"roles": roles_data}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.get("/audit/logs")
@login_required
def api_audit_logs():
    """REST API audit logs endpoint."""
    try:
        limit = min(request.args.get('limit', 100, type=int), 500)
        
        logs = IAMAuthLog.query.order_by(IAMAuthLog.event_time.desc()).limit(limit).all()
        
        logs_data = []
        for log in logs:
            logs_data.append({
                "log_id": log.log_id,
                "user_id": log.user_id,
                "username": log.user.username if log.user else None,
                "event_type": log.event_type,
                "event_time": log.event_time.isoformat() if log.event_time else None,
                "ip_address": log.ip_address,
                "user_agent": log.user_agent,
                "details": log.details
            })
        
        return jsonify({"logs": logs_data, "total": len(logs_data)}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500


@api_bp.get("/sessions/active")
@login_required
def api_active_sessions():
    """REST API list active sessions."""
    try:
        sessions = IAMAuthSession.query.filter_by(logout_time=None).order_by(IAMAuthSession.login_time.desc()).all()
        
        sessions_data = []
        for session in sessions:
            sessions_data.append({
                "session_id": session.session_id,
                "user_id": session.user_id,
                "username": session.user.username if session.user else None,
                "login_time": session.login_time.isoformat() if session.login_time else None,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent
            })
        
        return jsonify({"sessions": sessions_data, "total": len(sessions_data)}), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": f"Server error: {str(e)}"}), 500

