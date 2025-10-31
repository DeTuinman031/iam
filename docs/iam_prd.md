# 📑 Product Requirements Document (PRD)
## Project: Identity & Access Management (IAM)
**Version:** 1.1  
**Owner:** H. Poelenjee  
**Tech Lead:** Codex Team  
**Date:** 2025-11-01  
**Note:** Updated from AUM v1.0 (renamed to IAM for consistency and reusability)

---

## 1. Purpose / Vision
Develop a secure, modular **Identity & Access Management (IAM)** system that provides a unified identity, authentication, and authorization layer for enterprise web applications.

The IAM module should:
- Support **multi-tenant environments** (one “ultimate parent” and its subsidiaries).
- Support **multiple authentication methods** (local, SSO, MFA, SMS/WhatsApp).
- Enforce **Role-Based Access Control (RBAC)** with fine-grained module permissions.
- Provide an **audit-ready** trail for all authentication and authorization events.

This module must be **self-contained** and integratable into other systems (e.g., DORA Portal, Project Tracker, Ticketing System) as a plug-in or service.

---

## 2. Objectives
| Objective | Success Criteria |
|------------|------------------|
| Centralized identity management | Single user base per tenant, reusable across systems |
| Strong authentication | MFA, SSO, and step-up verification supported |
| Modular & reusable | IAM deployable as standalone service or embedded Flask blueprint |
| Secure role & tenant enforcement | No cross-tenant data leakage; audit-ready |
| Extensible | Support for email, TOTP, SMS, WhatsApp MFA channels |

---

## 3. System Architecture Overview
**Architecture Type:** Modular Flask Service  
**Backend:** Flask (Python 3.11), SQLAlchemy ORM, MySQL 8.4  
**Frontend:** Bootstrap 5 / Tailwind templates  
**Security:** JWT / session-based auth + RBAC decorators  
**Deployment:** Dockerized microservice (`iam` container)  
**Communication:** REST API (JSON) or internal blueprint  

### 3.1 Core Layers
| Layer | Responsibility |
|-------|----------------|
| Presentation | Login UI, MFA screens, user & role admin console |
| API | REST endpoints for auth, user, role, and session management |
| Service | Authentication, MFA, SSO logic, tenant scoping |
| Data | MySQL schema for users, roles, MFA, sessions, audit |

---

## 4. Core Functional Modules

### 4.1 Tenant Management
- Each tenant corresponds to an **ultimate parent organisation**.  
- Each user is tied to one tenant (`parent_id`).
- Optional hierarchy (subsidiaries, branches) managed externally.

### 4.2 User Management
**Features:**
- Create / edit / deactivate users
- Assign to tenant
- Set login method: Local | SSO
- Reset passwords (local mode)
- Assign MFA options
- Lock / unlock accounts
- View audit trail of logins, MFA events

**Data Fields:**
- username  
- email  
- display_name  
- phone_number (for SMS/WhatsApp MFA)  
- auth_provider (local / azure_ad / okta / saml)  
- status (active / locked / suspended)  
- parent_id (tenant)  

### 4.3 Role-Based Access Control (RBAC)
- Roles stored in table `iam_role` (e.g., admin, security, audit, readonly).  
- Many-to-many mapping via `iam_user_role`.  
- Flask decorators enforce per-route role permissions.  
- Role inheritance or custom roles optional in later phase.

### 4.4 Authentication Methods
| Mode | Description |
|------|--------------|
| **Local** | Username + password (bcrypt or Argon2) |
| **SSO** | Azure AD / Okta / Entra ID via OpenID Connect or SAML |
| **2FA / MFA** | Second factor required: email OTP, TOTP app, SMS, or WhatsApp message |

### 4.5 Multi-Factor Authentication (MFA)
- Email OTP (6-digit code, expires 5 min)  
- TOTP (Google Authenticator / 1Password)  
- SMS or WhatsApp OTP (via Twilio, Vonage, or other gateway)  
- Each user can register multiple methods in table `iam_mfa_method`.  
- MFA required:
  - On login  
  - For step-up actions (e.g., viewing confidential documents)

### 4.6 Session Management
- Table `iam_auth_session` tracks login/logout times, IP, user-agent.
- Session timeout configurable per tenant.
- Step-up MFA verification timestamp stored per session.

### 4.7 Audit & Logging
- Every login, MFA, logout event logged in `iam_auth_log`.  
- All sensitive DB updates include `updated_by = current_user.username`.  
- Admin dashboard for activity overview.

---

## 5. Database Schema Overview
Core tables:
| Table | Purpose |
|--------|---------|
| **iam_user_account** | Users, authentication method, tenant, status |
| **iam_role** | Role catalogue |
| **iam_user_role** | Mapping user ↔ role |
| **iam_auth_session** | Login session audit |
| **iam_mfa_method** | Enrolled MFA options per user |
| **iam_mfa_challenge** | OTP events (email/SMS/TOTP/WhatsApp) |
| **iam_auth_log** | Optional general audit log |

All tables include: `parent_id`, `created_at`, `updated_at` timestamps.

---

## 6. Authentication Flow Scenarios
### 6.1 Local Login + Email OTP
1. User enters username + password.  
2. System validates password.  
3. Generate OTP → send via email.  
4. User enters OTP → verified → session created.  

### 6.2 SSO Login (Azure AD)
1. User clicks “Sign in with Microsoft”.  
2. Redirect to IdP → authenticate + MFA handled by IdP.  
3. IdP returns OIDC token → Flask verifies signature.  
4. User session created; roles loaded from local DB.  
5. Optional local step-up MFA if resource sensitivity requires.

### 6.3 SMS / WhatsApp MFA
1. On login success or step-up request, generate code.  
2. Send via Twilio/Vonage WhatsApp or SMS.  
3. Store hash + expiry in `iam_mfa_challenge`.  
4. User submits code → verify hash → complete login.

---

## 7. REST API Endpoints
| Method | Endpoint | Description |
|---------|-----------|-------------|
| POST | `/api/auth/login` | Local login |
| POST | `/api/auth/mfa/verify` | MFA verification |
| GET  | `/api/auth/sso/login` | Redirect to IdP |
| GET  | `/api/auth/sso/callback` | Handle IdP response |
| POST | `/api/auth/logout` | Logout & invalidate session |
| GET  | `/api/users` | List users (Admin only) |
| POST | `/api/users` | Create new user |
| PATCH | `/api/users/{id}` | Update user |
| GET  | `/api/roles` | List roles |
| POST | `/api/users/{id}/roles` | Assign role |
| POST | `/api/mfa/setup` | Register MFA (TOTP/SMS/Email) |
| POST | `/api/mfa/verify` | Verify MFA challenge |
| GET  | `/api/audit/logs` | List recent login/audit events |

---

## 8. UI / UX Concepts
**Pages**
- Login Page: Username + password / SSO button  
- MFA Page: Input OTP code (email / SMS / app)  
- Admin Dashboard: Users, roles, sessions, MFA enrollments  
- User Profile: Manage MFA methods (add/remove, set primary)  
- Activity Logs: Filter by user/date/IP  

---

## 9. Security Requirements
| Control | Implementation |
|----------|----------------|
| Passwords | Argon2 or bcrypt hashing |
| MFA | Email, TOTP, SMS, WhatsApp |
| Token Storage | Server-side Flask session or JWT |
| Rate Limiting | 5 failed logins per 15 min → temporary lock |
| HTTPS | Mandatory (TLS 1.3) |
| Data Encryption | Secrets and TOTP keys encrypted at rest |
| Logging | All auth and MFA events stored for ≥ 7 years |
| Step-Up Auth | Required for sensitive actions |
| Audit Export | CSV/JSON for compliance reviews |

---

## 10. Non-Functional Requirements
| Category | Target |
|-----------|--------|
| Availability | 99.9 % |
| Scalability | Up to 50 000 users per tenant |
| Security | OWASP ASVS Level 2 |
| Response Time | < 500 ms (login) |
| Data Retention | 7 years |
| Compliance | GDPR / DORA ready |
| Integration | REST, Flask Blueprint, or microservice API |

---

## 11. MVP Scope
✅ Must-have (Sprint 1–2)
- User CRUD, roles, RBAC decorators  
- Local login + password hashing  
- Email OTP MFA  
- SSO (Azure AD OIDC) basic integration  
- Audit trail (`iam_auth_session`, `iam_auth_log`)  
- REST API + minimal UI  

🚀 Phase 2 (Sprint 3–4)
- SMS / WhatsApp MFA  
- Step-Up MFA decorators  
- Admin activity logs  
- Role management UI  

---

## 12. Deliverables
1. `/db/iam_schema.sql` – DDL for IAM tables  
2. `/app/auth/` – Flask blueprint package  
3. `/app/auth/services_mfa.py` – MFA logic  
4. `/app/auth/services_sso.py` – OIDC/SAML integration  
5. `/app/auth/routes_admin.py` – user/role admin routes  
6. `/templates/auth/*.html` – UI templates  
7. `/docs/IAM_PRD.md` (this document)  
8. `/docs/IAM_TI.md` (technical instruction)  

---

