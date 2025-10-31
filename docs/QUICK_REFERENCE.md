# IAM Quick Reference Card

**Everything you need to remember in one place**

---

## 🚀 Essential Commands

### Start IAM
```bash
python manage.py run
# Access: http://localhost:5000
```

### Database Setup
```bash
# Start MySQL
docker-compose up -d mysql

# Create schema
mysql -u root < db/iam_schema.sql

# Create test user
flask create-test-user
```

### Version Management
```bash
# Bump version
python3 tools/bump_version.py rev    # 1.1.0 -> 1.1.1
python3 tools/bump_version.py minor  # 1.1.0 -> 1.2.0
python3 tools/bump_version.py major  # 1.1.0 -> 2.0.0

# Commit and tag
git commit -m "feat(iam): description [v1.2.0]"
git tag -a iam-v1.2.0 -m "IAM v1.2.0 - description"
git push origin iam-v1.2.0
```

### Testing
```bash
# Test API
python3 test_api.py

# Test database
flask test-db

# Test connection
python3 test_connection.py
```

---

## 📁 Key Files

### Application
- `app/__init__.py` - App factory
- `app/config.py` - Configuration
- `app/auth/models.py` - Database models
- `app/auth/routes_*.py` - API routes
- `manage.py` - CLI entry point

### Integration
- `iam_client.py` - Python client library
- `test_api.py` - API tests
- `test_connection.py` - DB tests

### Documentation
- `START_HERE.md` ⭐ Read this first!
- `INTEGRATION_SUMMARY.md` - Integration answers
- `NEXT_PROJECT_CHECKLIST.md` - Step-by-step
- `docs/integration_guide.md` - Full guide
- `docs/VERSION_MANAGEMENT.md` - Version workflow

### Tools
- `tools/bump_version.py` - Version management
- `setup_iam.sh` - Quick setup
- `docker-compose.yml` - Docker setup

---

## 🔗 API Endpoints

### Authentication
```
POST /api/auth/login    - Login
GET  /api/auth/verify   - Verify session
POST /api/auth/logout   - Logout
```

### Users
```
GET  /api/users         - List users
GET  /api/users/{id}    - User details
```

### Roles
```
GET  /api/roles         - List roles
```

### Audit
```
GET  /api/audit/logs    - Audit logs
GET  /api/sessions/active - Active sessions
```

---

## 🔑 Default Credentials

```
Username: testuser
Password: testpass123
Email: testuser@example.com
```

---

## 📊 Quick Stats

- **Version:** v1.1.1
- **Python:** 3.11+
- **Database:** MySQL 8.4+
- **Endpoints:** 8 REST API
- **Docs:** 20 markdown files
- **Tests:** All passing ✅

---

## 🆘 Quick Troubleshooting

### "Can't connect to MySQL"
```bash
# Start MySQL
docker-compose up -d mysql
# OR
brew services start mysql
```

### "Account disabled / locked"
- User exists, check `is_active` and `is_locked`
- Use direct DB query in models
- See: `docs/setup_findings_and_remediations.md`

### "Module not found"
```bash
pip install -r requirements.txt
```

### "CORS errors"
- Set `ALLOWED_ORIGINS` in config
- See: `docs/integration_guide.md`

---

## 📚 When You Need...

### To integrate IAM
→ `INTEGRATION_SUMMARY.md` (quick)  
→ `NEXT_PROJECT_CHECKLIST.md` (steps)  
→ `docs/integration_guide.md` (detailed)

### To understand architecture
→ `docs/iam_prd.md`  
→ `docs/iam_ti.md`  
→ `PROJECT_STATUS.md`

### To troubleshoot issues
→ `docs/setup_findings_and_remediations.md`  
→ `TESTING.md`  
→ `SETUP.md`

### To manage versions
→ `docs/VERSION_MANAGEMENT.md`  
→ `tools/bump_version.py --help`

### To deploy to production
→ `README.md` → Docker section  
→ `docker-compose.yml`  
→ `docs/integration_guide.md` → Deployment

---

## 🎯 Integration Pattern

```python
# Python project
from iam_client import IAMClient

iam = IAMClient("https://iam.yourdomain.com")
result = iam.login(username, password)
# Store session, use for auth
```

```javascript
// JavaScript project
const response = await fetch('https://iam.yourdomain.com/api/auth/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
    credentials: 'include'
});
```

---

## 📞 Support Resources

1. Documentation: `docs/README.md`
2. Changelog: `docs/iam_changelog.md`
3. Status: `PROJECT_STATUS.md`
4. Issues: `docs/setup_findings_and_remediations.md`

---

**Keep this card handy!** 📋

