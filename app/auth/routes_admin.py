# app/auth/routes_admin.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.extensions import db
from app.auth.models import IAMUserAccount, IAMRole, IAMUserRole, IAMMfaMethod, IAMAuthSession, IAMAuthLog

admin_bp = Blueprint("admin", __name__, template_folder="templates")


@admin_bp.get("/dashboard")
@login_required
def dashboard():
    """Basic admin dashboard - placeholder for now."""
    return render_template("admin/dashboard.html", user=current_user)


@admin_bp.get("/users")
@login_required
def users_list():
    """List all users."""
    try:
        users = IAMUserAccount.query.order_by(IAMUserAccount.created_at.desc()).all()
        return render_template("admin/users.html", users=users, user=current_user, current_user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error in users_list: {e}", exc_info=True)
        flash(f"Error loading users: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))


@admin_bp.get("/roles")
@login_required
def roles_list():
    """List all roles and their assignments."""
    try:
        roles = IAMRole.query.order_by(IAMRole.role_name).all()
        # Count users per role
        role_counts = {}
        for role in roles:
            role_counts[role.role_id] = IAMUserRole.query.filter_by(role_id=role.role_id).count()
        return render_template("admin/roles.html", roles=roles, role_counts=role_counts, user=current_user, current_user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error in roles_list: {e}", exc_info=True)
        flash(f"Error loading roles: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))


@admin_bp.get("/mfa")
@login_required
def mfa_list():
    """List all MFA enrollments."""
    try:
        # Get all users with MFA methods
        mfa_methods = IAMMfaMethod.query.filter_by(is_active=True).order_by(IAMMfaMethod.created_at.desc()).all()
        # Group by user
        users_with_mfa = {}
        for method in mfa_methods:
            if method.user_id not in users_with_mfa:
                users_with_mfa[method.user_id] = {
                    'user': method.user,
                    'methods': []
                }
            users_with_mfa[method.user_id]['methods'].append(method)
        return render_template("admin/mfa.html", users_with_mfa=users_with_mfa, user=current_user, current_user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error in mfa_list: {e}", exc_info=True)
        flash(f"Error loading MFA data: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))


@admin_bp.get("/audit-logs")
@login_required
def audit_logs():
    """List audit logs and sessions."""
    try:
        # Get recent audit logs
        logs = IAMAuthLog.query.order_by(IAMAuthLog.event_time.desc()).limit(100).all()
        # Get active sessions
        active_sessions = IAMAuthSession.query.filter_by(logout_time=None).order_by(IAMAuthSession.login_time.desc()).all()
        return render_template("admin/audit_logs.html", logs=logs, active_sessions=active_sessions, user=current_user, current_user=current_user)
    except Exception as e:
        current_app.logger.error(f"Error in audit_logs: {e}", exc_info=True)
        flash(f"Error loading audit logs: {str(e)}", "error")
        return redirect(url_for("admin.dashboard"))

