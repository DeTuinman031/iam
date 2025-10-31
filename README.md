# IAM - Identity & Access Management Service

**Version:** v1.1.1  
A secure, modular Identity & Access Management system built with Flask for enterprise web applications.

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- MySQL 8.4+ or Docker
- Git

### Installation

```bash
# Clone repository
git clone <repository-url>
cd iam

# Install dependencies
pip install -r requirements.txt

# Start MySQL (Docker)
docker-compose up -d mysql

# Or start local MySQL
brew services start mysql

# Create database and schema
mysql -u root < db/iam_schema.sql

# Run migrations (optional)
export FLASK_APP=app
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Create test user
flask create-test-user

# Start the application
python manage.py run
```

Access at: http://localhost:5000

---

## 📋 Features

✅ **Authentication**
- Local username/password authentication
- Session-based auth with Flask-Login
- Password hashing (bcrypt/Argon2)
- Account lock/unlock functionality
- Last login tracking

✅ **User Management**
- CRUD operations for users
- Multi-tenant support (parent_id)
- Role-based access control (RBAC)
- Account status management

✅ **Role Management**
- Default roles: admin, security, auditor, developer, readonly
- Many-to-many user-role assignments
- Permission checking helpers

✅ **Multi-Factor Authentication (MFA)** - *Coming Soon*
- Email OTP
- TOTP (Google Authenticator)
- SMS/WhatsApp OTP

✅ **Audit & Logging**
- Complete authentication audit trail
- Session tracking
- IP address logging
- User-agent tracking

✅ **REST API**
- JSON-based API for integration
- CORS support for cross-origin requests
- Session cookie or token-based auth
- Comprehensive error handling

---

## 🔌 Integration Patterns

### Pattern 1: Standalone Microservice (Recommended)

**For:** Multiple internet-accessible projects

**Setup:**
```yaml
# Deploy IAM as separate service
Service: https://iam.yourdomain.com
Projects: project-a.com, project-b.com, project-c.com
All projects → IAM for authentication
```

### Pattern 2: Embedded Blueprint

**For:** Single project or same-domain projects

**Setup:**
```python
from iam.app import create_app
# IAM runs within your Flask app
```

### Pattern 3: Shared Library

**For:** Multiple projects with shared codebase

**Setup:**
```python
# Install IAM as Python package
pip install iam-package

# Import in your projects
from iam import IAMClient
```

---

## 🔗 API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/login` | No | Authenticate user |
| `GET` | `/api/auth/verify` | Yes | Verify session |
| `POST` | `/api/auth/logout` | Yes | End session |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/users` | Yes | List users (paginated) |
| `GET` | `/api/users/{id}` | Yes | Get user details |

### Roles

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/roles` | Yes | List all roles |

### Audit

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/audit/logs` | Yes | Get audit logs |
| `GET` | `/api/sessions/active` | Yes | List active sessions |

**Health Check:**
| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/healthz` | No | Service health |

---

## 💻 Python Client Library

```python
from iam_client import IAMClient

# Initialize client
iam = IAMClient(base_url="https://iam.yourdomain.com")

# Login
result = iam.login("username", "password")
print(f"Logged in as: {result['user']['username']}")

# Verify session
auth_status = iam.verify_session()
if auth_status['authenticated']:
    print("Session valid")

# List users
users = iam.list_users(page=1, per_page=10)
print(f"Total users: {users['total']}")

# List roles
roles = iam.list_roles()
for role in roles['roles']:
    print(f"{role['role_name']}: {role['user_count']} users")

# Logout
iam.logout()
```

**Run example:**
```bash
python iam_client.py http://localhost:5000
```

---

## 🧪 Testing

### Test Database Connection
```bash
flask test-db
```

### Test API Endpoints
```bash
python test_api.py
```

### Test Client Library
```bash
python iam_client.py http://localhost:5000
```

### Run All Tests
```bash
python test_connection.py  # DB connectivity
python test_api.py         # API endpoints
```

---

## 📁 Project Structure

```
iam/
├── app/                           # Main application
│   ├── __init__.py               # App factory
│   ├── config.py                 # Configuration
│   ├── extensions.py             # Flask extensions
│   └── auth/                     # Auth module
│       ├── models.py             # Database models
│       ├── routes_login.py       # Login routes
│       ├── routes_admin.py       # Admin routes
│       ├── routes_api.py         # REST API routes
│       └── templates/            # Jinja2 templates
│           ├── base.html
│           ├── login.html
│           └── admin/
├── db/                           # Database schemas
│   └── iam_schema.sql           # Schema definition
├── docs/                         # Documentation
│   ├── iam_prd.md               # Product requirements
│   ├── integration_guide.md     # Integration guide
│   ├── integration_quick_reference.md
│   └── setup_findings_and_remediations.md
├── manage.py                     # Flask CLI entry point
├── requirements.txt              # Dependencies
├── docker-compose.yml            # MySQL container setup
├── iam_client.py                 # Python client library
├── test_api.py                   # API tests
└── test_connection.py            # DB connection tests
```

---

## 🔐 Security

### Implemented

✅ Password hashing (bcrypt)  
✅ Session-based authentication  
✅ Account lockout capability  
✅ HTTPS/TLS support (production)  
✅ SQL injection prevention (SQLAlchemy)  
✅ CORS configuration  

### Recommended for Production

⚠️ Rate limiting on login endpoints  
⚠️ Redis for session storage at scale  
⚠️ JWT tokens for stateless auth  
⚠️ API key authentication  
⚠️ Comprehensive audit logging  
⚠️ Security headers (HSTS, CSP, etc.)  
⚠️ Regular security audits  

---

## 🐳 Docker Deployment

### Quick Start

```bash
# Start MySQL and IAM
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f iam
```

### Production Dockerfile

See `Dockerfile` (to be created) for production deployment with:
- Gunicorn WSGI server
- Multi-worker configuration
- Health checks
- Proper signal handling

---

## 📊 Configuration

### Environment Variables

```bash
# Database
DATABASE_URL=mysql+pymysql://iam_user:iam_pass@localhost:3306/iam

# Security
FLASK_SECRET_KEY=your-secret-key-here

# CORS
ALLOWED_ORIGINS=https://project-a.com,https://project-b.com

# Environment
FLASK_ENV=development|production
```

### Configuration Files

- `app/config.py` - Development and production configs
- `.env` - Local environment variables (create as needed)

---

## 📈 Monitoring

### Health Check

```bash
curl http://localhost:5000/healthz
```

Response:
```json
{
  "status": "ok",
  "service": "IAM",
  "database": "connected"
}
```

### Logs

Check application logs for:
- Authentication events
- API access
- Errors and exceptions
- Performance metrics

---

## 🔄 Database Migrations

```bash
# Initialize migrations (first time)
export FLASK_APP=app
flask db init

# Create migration
flask db migrate -m "Description of changes"

# Apply migration
flask db upgrade

# Rollback migration
flask db downgrade
```

---

## 👥 Default Roles

1. **admin** - Full system access
2. **security** - Manage users, roles, and MFA
3. **auditor** - Read-only audit and session reports
4. **developer** - Access API and integration features
5. **readonly** - Limited read-only access

---

## 🔗 Integration with Other Projects

See detailed guides:
- [Integration Guide](docs/integration_guide.md) - Comprehensive integration documentation
- [Quick Reference](docs/integration_quick_reference.md) - Quick answers and patterns
- [Setup Findings](docs/setup_findings_and_remediations.md) - Common issues and solutions

### Quick Integration Example

**For Flask projects:**
```python
from iam_client import IAMClient

iam = IAMClient(base_url="https://iam.yourdomain.com")

@app.before_request
def require_auth():
    if not is_authenticated():
        # Redirect to IAM login
        return redirect("https://iam.yourdomain.com/auth/login")
```

**For other languages:**
- Use REST API directly with HTTP client
- Follow API specifications in integration guide

---

## 📚 CLI Commands

```bash
# Database
flask test-db              # Test database connection
flask init-db              # Create all tables

# Users
flask create-test-user     # Create test user interactively

# Application
flask run                  # Start development server

# Migrations
flask db init              # Initialize migrations
flask db migrate -m "msg"  # Create migration
flask db upgrade           # Apply migrations
```

---

## 🛠️ Development

### Running in Development

```bash
# Set environment
export FLASK_APP=app
export FLASK_ENV=development

# Run with auto-reload
flask run --reload
```

### Debugging

- Enable debug mode: `DEBUG = True` in config
- Check Flask terminal for error details
- Use Flask debugger for interactive debugging
- Check MySQL logs: `docker-compose logs mysql`

---

## 🚧 Roadmap

### Phase 1: MVP (Current)
- ✅ Local authentication
- ✅ User management
- ✅ Role-based access control
- ✅ REST API
- ✅ Admin dashboard
- ✅ Audit logging

### Phase 2: MFA
- [ ] Email OTP
- [ ] TOTP (Google Authenticator)
- [ ] SMS/WhatsApp OTP
- [ ] MFA enforcement

### Phase 3: Enterprise
- [ ] SSO/SAML integration
- [ ] OAuth 2.0 / OpenID Connect
- [ ] Multi-tenant isolation
- [ ] Advanced RBAC

### Phase 4: Operations
- [ ] Rate limiting
- [ ] Redis session storage
- [ ] Prometheus metrics
- [ ] Grafana dashboards
- [ ] Automated testing suite

---

## 📞 Support

- **Documentation:** See `/docs` folder
- **PRD:** `docs/iam_prd.md`
- **Integration Guide:** `docs/integration_guide.md`
- **Issues:** Check `docs/setup_findings_and_remediations.md`

---

## 📄 License

[Specify your license here]

---

## 🙏 Acknowledgments

Built following Flask best practices and enterprise security standards.

