# 🧾 CHANGELOG & VERSION MANAGEMENT
## Project: Identity & Access Management (IAM)
**Owner:** H. Poelenjee  
**Tech Lead:** Codex Team  
**Created:** 2025-11-01  

This file serves as both a **changelog** and a **version management ledger** for the IAM module. Every edit, insertion, or removal of code, configuration, or documentation within the IAM system must be recorded here.  
Versioning adheres to semantic style: `Major.Minor.Revision` (e.g., 1.1.1 → 1.1.1 → 1.2.0).

---

## 🧱 VERSION STRUCTURE
| Field | Definition | Example |
|--------|-------------|----------|
| **Major** | Structural or architectural change affecting compatibility | v2.0 – shift from Flask to FastAPI |
| **Minor** | Functional enhancement or new feature | v1.2 – added WebAuthn support |
| **Revision** | Bugfix, patch, security update | v1.1.3 – fixed OTP expiry logic |

---

## 🔢 CURRENT ACTIVE VERSION
**IAM v1.1.1 (2025-11-01)** – Comprehensive documentation, REST API, and plug-and-play infrastructure.  
Includes full integration guides, version management system, and deployment automation.

---

## 🕒 VERSION HISTORY

### 🧩 v1.1.1 – 2025-11-01
**Author:** Codex Team  
**Type:** Add / Edit  
**Scope:** documentation / infrastructure / tooling  
**Summary:** Added comprehensive integration documentation, version management system with bump_version.py script, plug-and-play requirements guide, automated setup script, and 18 documentation files. REST API fully implemented with CORS support. All tests passing.

### 🧩 v1.1.0 – 2025-11-01
**Status:** Archived  
**Changes:**
- Project renamed from **AUM (Access & User Management)** to **IAM (Identity & Access Management)**.  
- Created new PRD (`IAM_PRD.md`) and TI (`IAM_TI.md`).  
- Created new MySQL schema (`iam_schema.sql`).  
- Added ORM layer (`models.py`).  
- Introduced MFA (Email, TOTP, SMS, WhatsApp) and SSO (Azure AD) support.  
- Implemented tenant-based RBAC decorators.  

### 🧩 v1.0.0 – 2025-10-31
**Status:** Archived  
**Changes:**
- Original release as Access & User Management (AUM).  
- Contained PRD/TI documentation, local login, and email OTP.  
- Later superseded by IAM branding for scalability and integration alignment.  

---

## 🧩 VERSIONING RULES
1. **Every modification counts** – Any code insertion, deletion, or logic change triggers a version increment.
2. **Granular tracking** – Each commit or deployment must reference the version number.
3. **Documentation parity** – PRD, TI, and schema updates must reflect the same version.
4. **Change review** – Each version must include: author, date, type (add/edit/remove), and short rationale.
5. **Release tagging** – All production releases must be tagged in Git or release registry using the version ID.

---

## 🧩 VERSION LOG TEMPLATE
When logging a new version, append entries as follows:

```
### 🧩 vX.Y.Z – YYYY-MM-DD
**Author:** [Name]  
**Type:** [Insert / Edit / Remove]  
**Scope:** [e.g., models.py / routes_admin.py / schema.sql / MFA logic]  
**Summary:** [Short explanation of what changed and why]
```

---

## 🧩 UPCOMING (Planned Versions)
| Target Version | Description | ETA |
|----------------|-------------|-----|
| v1.2.0 | Add WebAuthn (hardware key) support | Dec 2025 |
| v1.2.1 | Step-up MFA decorator refactor | Dec 2025 |
| v1.3.0 | Integration with Project Monitoring / Ticket System | Jan 2026 |

---

## 🧩 VERSION MANAGEMENT PROCESS
1. **Code Commit:** Developer completes change → increments local version.
2. **Peer Review:** PR reviewed → version verified in `IAM_CHANGELOG.md`.
3. **Tag & Deploy:** Git tag created → deployment metadata updated.
4. **Archive:** Outdated version folder/documentation preserved for traceability.

---

## 🧭 GOVERNANCE NOTES
- IAM follows **strict version discipline** for all functional and technical artifacts.
- All documentation (`PRD`, `TI`, `Schema`, `Models`, `Routes`) must reference the same version header.
- Any cross-project usage (e.g., integration into DORA Portal or Ticket System) must declare dependency version in its own changelog.

---

**End of IAM Version Management Document**

