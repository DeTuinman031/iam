# app/auth/models.py

__version__ = "1.1.0"

from datetime import datetime
from typing import List
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db


class IAMUserAccount(UserMixin, db.Model):
    """
    Represents an application user (human or service account).
    Bound to a tenant (parent_id) and supports local or SSO auth.
    Mirrors iam_user_account.
    """
    __tablename__ = "iam_user_account"

    user_id         = db.Column(db.Integer, primary_key=True)
    parent_id       = db.Column(db.Integer, nullable=False)  # tenant / ultimate parent

    username        = db.Column(db.String(150), unique=True, nullable=False)
    email           = db.Column(db.String(255), unique=True, nullable=False)
    phone_number    = db.Column(db.String(50))

    display_name    = db.Column(db.String(255), nullable=False)

    auth_provider   = db.Column(
        db.Enum('local', 'azure_ad', 'okta', 'saml', 'other', name="auth_provider_enum"),
        nullable=False,
        default='local'
    )

    password_hash   = db.Column(db.String(255))  # may be NULL for SSO users

    is_active       = db.Column(db.Boolean, nullable=False, default=True)
    is_locked       = db.Column(db.Boolean, nullable=False, default=False)

    last_login_at   = db.Column(db.DateTime)

    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by      = db.Column(db.String(255))
    updated_by      = db.Column(db.String(255))

    # relationships
    roles           = db.relationship(
        "IAMRole",
        secondary="iam_user_role",
        back_populates="users",
        lazy="joined"
    )

    mfa_methods     = db.relationship(
        "IAMMfaMethod",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    sessions        = db.relationship(
        "IAMAuthSession",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    mfa_challenges  = db.relationship(
        "IAMMfaChallenge",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    auth_logs       = db.relationship(
        "IAMAuthLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic"
    )

    # Flask-Login integration
    def get_id(self):
        return str(self.user_id)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    @property
    def is_active_account(self):
        # Flask-Login uses is_active(), not is_active_account as property,
        # but we keep both to avoid confusion with column is_active.
        # Since the method name conflicts with the column, query the database directly
        from app.extensions import db
        try:
            result = db.session.execute(
                db.text("SELECT CAST(is_active AS UNSIGNED) as is_active, CAST(is_locked AS UNSIGNED) as is_locked FROM iam_user_account WHERE user_id = :user_id"),
                {"user_id": self.user_id}
            ).fetchone()
            if result:
                # CAST as UNSIGNED converts BIT(1) to int (0 or 1)
                active_val = bool(result[0]) if result[0] is not None else True
                locked_val = bool(result[1]) if result[1] is not None else False
                return bool(active_val and not locked_val)
            else:
                return True  # Default to active if user not found
        except Exception as e:
            # If query fails, default to active
            return True

    def is_active(self):  # Flask-Login hook
        return self.is_active_account

    # Password helpers (local auth only)
    def set_password(self, raw_password: str):
        self.password_hash = generate_password_hash(raw_password)

    def verify_password(self, raw_password: str) -> bool:
        if not self.password_hash:
            return False
        return check_password_hash(self.password_hash, raw_password)

    # RBAC helpers
    def has_role(self, role_name: str) -> bool:
        return any(r.role_name == role_name for r in self.roles)

    def has_any_role(self, role_names: List[str]) -> bool:
        names = {r.role_name for r in self.roles}
        return any(r in names for r in role_names)

    # MFA helpers
    def has_active_mfa(self) -> bool:
        return self.mfa_methods.filter_by(is_active=True).count() > 0


class IAMRole(db.Model):
    """
    RBAC role definition. e.g. 'admin', 'security', 'auditor', etc.
    Mirrors iam_role.
    """
    __tablename__ = "iam_role"

    role_id          = db.Column(db.Integer, primary_key=True)
    role_name        = db.Column(db.String(100), unique=True, nullable=False)
    role_description = db.Column(db.String(255))

    created_at       = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at       = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    users            = db.relationship(
        "IAMUserAccount",
        secondary="iam_user_role",
        back_populates="roles",
        lazy="dynamic"
    )


class IAMUserRole(db.Model):
    """
    Join table for users <-> roles.
    Mirrors iam_user_role.
    """
    __tablename__ = "iam_user_role"

    user_id     = db.Column(db.Integer, db.ForeignKey("iam_user_account.user_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    role_id     = db.Column(db.Integer, db.ForeignKey("iam_role.role_id", ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)

    assigned_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    assigned_by = db.Column(db.String(255))


class IAMAuthSession(db.Model):
    """
    Represents a login session, for auditing and step-up MFA reuse.
    Mirrors iam_auth_session.
    """
    __tablename__ = "iam_auth_session"

    session_id          = db.Column(db.String(64), primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("iam_user_account.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    login_time          = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    logout_time         = db.Column(db.DateTime)

    ip_address          = db.Column(db.String(64))
    user_agent          = db.Column(db.String(255))
    sso_idp_session_ref = db.Column(db.String(255))

    created_at          = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user                = db.relationship("IAMUserAccount", back_populates="sessions")


class IAMMfaMethod(db.Model):
    """
    Stores MFA enrollment per user. A user can have multiple factors.
    Mirrors iam_mfa_method.
    """
    __tablename__ = "iam_mfa_method"

    mfa_id          = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("iam_user_account.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    method_type     = db.Column(
        db.Enum('email_otp','totp','sms','whatsapp','webauthn','custom_app', name="mfa_method_type_enum"),
        nullable=False
    )

    totp_secret     = db.Column(db.String(255))  # should be encrypted at rest
    is_primary      = db.Column(db.Boolean, nullable=False, default=False)
    is_active       = db.Column(db.Boolean, nullable=False, default=True)

    created_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    user            = db.relationship("IAMUserAccount", back_populates="mfa_methods")


class IAMMfaChallenge(db.Model):
    """
    Temporary OTP / challenge for login or step-up MFA.
    Mirrors iam_mfa_challenge.
    """
    __tablename__ = "iam_mfa_challenge"

    challenge_id    = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("iam_user_account.user_id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False)

    method_type     = db.Column(
        db.Enum('email_otp','totp','sms','whatsapp','webauthn','custom_app', name="mfa_challenge_method_enum"),
        nullable=False
    )

    otp_code_hash   = db.Column(db.String(255))  # store hashed OTP / code (never plaintext)

    issued_at       = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    expires_at      = db.Column(db.DateTime, nullable=False)
    consumed_at     = db.Column(db.DateTime)

    ip_address      = db.Column(db.String(64))

    purpose         = db.Column(
        db.Enum('login','step_up','admin_action','view_confidential_data', name="mfa_purpose_enum"),
        nullable=False,
        default='login'
    )

    user            = db.relationship("IAMUserAccount", back_populates="mfa_challenges")


class IAMAuthLog(db.Model):
    """
    General audit logging of authentication and access events.
    Mirrors iam_auth_log.
    """
    __tablename__ = "iam_auth_log"

    log_id          = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("iam_user_account.user_id", ondelete="SET NULL", onupdate="CASCADE"))

    event_type      = db.Column(
        db.Enum('login_success','login_failed','logout','mfa_sent','mfa_verified','sso_login','lockout','password_reset',
                name="auth_event_type_enum"),
        nullable=False
    )

    event_time      = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    ip_address      = db.Column(db.String(64))
    user_agent      = db.Column(db.String(255))

    details         = db.Column(db.Text)

    user            = db.relationship("IAMUserAccount", back_populates="auth_logs")
