# app/auth/routes_login.py
from flask import Blueprint, request, render_template, redirect, url_for, flash, current_app
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.auth.models import IAMUserAccount

auth_bp = Blueprint("auth", __name__, template_folder="templates")

@auth_bp.get("/login")
def login_page():
    return render_template("login.html")

@auth_bp.post("/login")
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    user = IAMUserAccount.query.filter_by(username=username).first()
    if not user:
        flash("Invalid credentials", "error")
        return redirect(url_for("auth.login_page"))
    
    if not user.verify_password(password):
        flash("Invalid credentials", "error")
        return redirect(url_for("auth.login_page"))

    # Check account status - use direct query to avoid method shadowing issues
    from app.extensions import db
    result = db.session.execute(
        db.text("SELECT CAST(is_active AS UNSIGNED) as is_active, CAST(is_locked AS UNSIGNED) as is_locked FROM iam_user_account WHERE user_id = :user_id"),
        {"user_id": user.user_id}
    ).fetchone()
    
    # Debug logging
    current_app.logger.info(f"Login attempt for {username}: result={result}")
    
    if result:
        is_active_val = bool(result[0]) if result[0] is not None else True
        is_locked_val = bool(result[1]) if result[1] is not None else False
        account_active = is_active_val and not is_locked_val
        current_app.logger.info(f"Account check: is_active={is_active_val}, is_locked={is_locked_val}, account_active={account_active}")
    else:
        account_active = True  # Default to active if can't check
        current_app.logger.warning(f"No result from database query for user_id={user.user_id}")
    
    if not account_active:
        current_app.logger.warning(f"Login blocked for {username}: account inactive or locked")
        flash(f"Account disabled / locked", "error")
        return redirect(url_for("auth.login_page"))

    # TODO: MFA challenge hook goes here
    login_user(user)

    user.last_login_at = db.func.now()
    db.session.commit()

    return redirect(url_for("admin.dashboard"))


@auth_bp.get("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login_page"))
