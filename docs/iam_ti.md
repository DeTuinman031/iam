# ⚙️ Technical Instruction (TI)
## Implementation Guide for Identity & Access Management (IAM)
**Version:** 1.1  
**Owner:** H. Poelenjee  
**Tech Lead:** Codex Team  
**Date:** 2025-11-01  
**Note:** Updated from AUM v1.0 to IAM v1.1 for naming consistency.

---

### 1. Technology Stack
| Component | Choice |
|------------|---------|
| Language | Python 3.11 + Flask 3.x |
| ORM | SQLAlchemy 2 |
| DB | MySQL 8.4 |
| Auth | Flask-Login + itsdangerous or JWT |
| MFA | pyotp (TOTP), smtplib (Email), Twilio/Vonage (SMS/WhatsApp) |
| SSO | Authlib (OIDC) |
| Crypto | bcrypt / argon2-cffi |

---

### 2. Directory Structure
```text
app/
  __init__.py
  config.py
  extensions.py

  auth/
    models.py            # DB models
    routes_login.py      # /auth/login, logout, sso
    routes_admin.py      # /admin/users, roles
    services_mfa.py      # generate, send, verify OTP
    services_sso.py      # Azure AD OIDC flow
    security.py          # decorators for RBAC, MFA, tenant
    templates/
      login.html
      mfa_verify.html
      admin_users.html

db/
  iam_schema.sql         # all DDL
docs/
  IAM_PRD.md
  IAM_TI.md
```

---

### 3. Database Schema (core)
Core tables:
- `iam_user_account`
- `iam_role`
- `iam_user_role`
- `iam_auth_session`
- `iam_mfa_method`
- `iam_mfa_challenge`
- `iam_auth_log`

Add `phone_number` to `iam_user_account` for SMS/WhatsApp MFA.

---

### 4. Authentication Workflow
#### 4.1 Local Login
```python
@app.route('/auth/login', methods=['POST'])
def login():
    user = IAMUserAccount.query.filter_by(username=form.username).first()
    if user and check_password_hash(user.password_hash, form.password):
        if user.has_active_mfa():
            issue_mfa_challenge(user, method='email_otp')
            return redirect(url_for('auth.verify_mfa'))
        login_user(user)
        return redirect('/')
```

#### 4.2 MFA Verification
```python
@app.route('/auth/mfa/verify', methods=['POST'])
def verify_mfa():
    if verify_mfa_code(current_user, form.code):
        complete_mfa_session(current_user)
        return redirect('/')
    else:
        flash("Invalid or expired code.")
```

#### 4.3 SMS / WhatsApp Sending (services_mfa.py)
```python
from twilio.rest import Client

def send_sms_otp(user, code):
    client = Client(account_sid, auth_token)
    msg = f"Your verification code is {code}"
    client.messages.create(
        body=msg,
        from_=TWILIO_NUMBER,
        to=user.phone_number
    )
```
WhatsApp can use the same API with a WhatsApp-enabled number.

#### 4.4 SSO (Authlib)
```python
oauth.register(
    name='azure',
    client_id=AZURE_CLIENT_ID,
    client_secret=AZURE_CLIENT_SECRET,
    server_metadata_url='https://login.microsoftonline.com/<tenant>/v2.0/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'}
)

@app.route('/auth/sso/login')
def sso_login():
    redirect_uri = url_for('auth.sso_callback', _external=True)
    return oauth.azure.authorize_redirect(redirect_uri)

@app.route('/auth/sso/callback')
def sso_callback():
    token = oauth.azure.authorize_access_token()
    userinfo = token['userinfo']
    user = find_or_create_user(userinfo)
    login_user(user)
    return redirect('/')
```

---

### 5. RBAC & Tenant Enforcement
In `security.py`:
```python
def requires_role(roles):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not current_user.has_any_role(roles):
                abort(403)
            return f(*args, **kwargs)
        return decorated
    return wrapper

def requires_parent(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        obj = get_object(kwargs['id'])
        if obj.parent_id != current_user.parent_id:
            abort(403)
        return f(*args, **kwargs)
    return decorated
```

---

### 6. MFA Decorator (Step-Up Auth)
```python
def requires_step_up(purpose):
    def wrapper(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not recent_successful_mfa(current_user, purpose):
                issue_mfa_challenge(current_user, method='totp', purpose=purpose)
                return redirect(url_for('auth.verify_mfa', next=request.url))
            return f(*args, **kwargs)
        return decorated
    return wrapper
```
Apply to sensitive endpoints (e.g., viewing confidential IAM data).

---

### 7. SMS / WhatsApp Integration
Use configurable provider (`SMS_PROVIDER` env var).  
Supported APIs:
- Twilio REST (`client.messages.create(...)`)
- Vonage (`client.send_message()`)
- WhatsApp Business Cloud API (`/v1/messages`)

All send functions funnel through `services_mfa.send_otp(user, code, method)`.

---

### 8. Audit Trail
- On every login → insert into `iam_auth_session`.  
- On every MFA → insert into `iam_mfa_challenge` with `consumed_at`.  
- On logout → update `iam_auth_session.logout_time`.  
- On failed login → record in `iam_auth_log` (with IP).  
- Provide admin view `/admin/audit/logs`.

---

### 9. Security Controls
| Control | Implementation |
|----------|----------------|
| Hashing | `argon2` (preferred) or `bcrypt` |
| Secret Keys | `.env` with `FLASK_SECRET_KEY`, `JWT_SECRET`, `MFA_ENCRYPTION_KEY` |
| Encryption | Encrypt TOTP secrets using Fernet |
| Rate Limiting | Flask-Limiter (per IP and user) |
| Session Timeout | Configurable (default = 30 min) |
| CSRF | Flask-WTF enabled |
| HTTPS Enforcement | via Nginx reverse proxy |

---

### 10. Testing & Validation
| Type | Description |
|------|-------------|
| Unit Tests | Models, MFA generation/validation, RBAC decorators |
| Integration | SSO login, MFA flow end-to-end |
| Security | Pen-test login, OTP bypass, replay attacks |
| Load | 100 concurrent logins / 5 s response |
| User Acceptance | Admin creates user → MFA → login → audit trail visible |

---

### 11. Deliverables (Sprint 1–2)
- Fully functional `/auth` blueprint (local + SSO + MFA)  
- RBAC decorators usable by other modules  
- Admin dashboard for users/roles/sessions  
- REST API endpoints for identity ops  
- Documentation (`IAM_PRD.md`, `IAM_TI.md`)  

---

### 12. Future Extensions
- WebAuthn / FIDO2 hardware keys  
- Push-based approval app  
- Group-based dynamic role mapping from AD/Okta claims  
- Federated identity microservice mode (standalone OAuth 2.0 provider)  

---

**Summary:** The IAM Technical Instruction provides the engineering blueprint to implement modular authentication, RBAC, and MFA with SSO, ready to integrate across enterprise systems.  
This version aligns naming and schema references with the IAM convention.

