# Next Project Integration Checklist

**Use this when integrating IAM with your next project**

---

## Before You Start

- [ ] Read: `INTEGRATION_SUMMARY.md` (5 min read)
- [ ] Read: `docs/integration_quick_reference.md` (10 min read)
- [ ] Decide: Microservice or embedded pattern?

---

## Deployment Checklist

### IAM Service Setup

- [ ] Choose deployment method (Docker, K8s, VM)
- [ ] Set up MySQL database
- [ ] Configure IAM service
- [ ] Set domain/subdomain: `iam.yourdomain.com`
- [ ] Configure SSL/TLS (HTTPS required!)
- [ ] Test: `curl https://iam.yourdomain.com/healthz`

### Configuration

- [ ] Set `ALLOWED_ORIGINS` for CORS
- [ ] Configure `FLASK_SECRET_KEY`
- [ ] Set database connection string
- [ ] Create admin user
- [ ] Test login at IAM service

---

## Project Integration Checklist

### In Your Next Project

**Option A: Python Project**

- [ ] Copy `iam_client.py` to your project
- [ ] Or: `pip install requests` and use API directly
- [ ] Import: `from iam_client import IAMClient`
- [ ] Configure: `iam = IAMClient(base_url=os.getenv('IAM_URL'))`
- [ ] Implement login redirect
- [ ] Add auth middleware/decorator
- [ ] Store user context from IAM
- [ ] Test authentication flow

**Option B: JavaScript/React/Vue**

- [ ] Install HTTP client: `axios` or `fetch`
- [ ] Create IAM service module
- [ ] Implement login component
- [ ] Add auth context/provider
- [ ] Protect routes
- [ ] Test authentication flow

**Option C: Other Languages**

- [ ] Install HTTP client library
- [ ] Implement IAM API calls
- [ ] Store session/tokens
- [ ] Add auth checks
- [ ] Test authentication flow

---

## Required API Calls

Your next project needs to call:

```python
# 1. Login
POST https://iam.yourdomain.com/api/auth/login
{
  "username": "user@example.com",
  "password": "password"
}

# 2. Verify (before every request)
GET https://iam.yourdomain.com/api/auth/verify
Headers: Cookie: session=<token>

# 3. Logout
POST https://iam.yourdomain.com/api/auth/logout
Headers: Cookie: session=<token>
```

---

## Environment Variables Needed

Add to your project:

```bash
# IAM Service URL
IAM_SERVICE_URL=https://iam.yourdomain.com

# Optional: API key for service-to-service
IAM_API_KEY=your-api-key

# Optional: Session cookie name
IAM_SESSION_COOKIE_NAME=iam_session
```

---

## Critical Security Items

- [ ] **HTTPS enabled** (TLS 1.3)
- [ ] **CORS configured** in IAM
- [ ] **Rate limiting** on IAM (or client-side)
- [ ] **Secrets in environment** (not hardcoded)
- [ ] **Session security** (secure, httpOnly cookies)

---

## Testing Checklist

- [ ] Test: Login from your project
- [ ] Test: Session persists across requests
- [ ] Test: Logout works
- [ ] Test: Invalid credentials rejected
- [ ] Test: Locked account rejected
- [ ] Test: Cross-domain requests (if applicable)

---

## Common Issues Reference

| Issue | Solution |
|-------|----------|
| CORS errors | Configure `ALLOWED_ORIGINS` in IAM |
| Session lost | Check cookie domain settings |
| 401 on verify | Ensure session cookie sent |
| Timeout errors | Check network, add retry logic |
| SSL errors | Verify certificate is valid |

**See:** `docs/setup_findings_and_remediations.md` for detailed troubleshooting

---

## Quick Success Test

After integration, this should work:

```bash
# From your project
curl -X POST https://iam.yourdomain.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Should return 200 with user info
```

---

## Support Resources

1. **Quick answers:** `INTEGRATION_SUMMARY.md`
2. **Detailed guide:** `docs/integration_guide.md`
3. **Troubleshooting:** `docs/setup_findings_and_remediations.md`
4. **API reference:** `docs/integration_guide.md` → Section 2

---

**Time Estimate:** 2-4 hours for first integration  
**Difficulty:** Medium (API integration is straightforward)  
**Blockers:** Make sure MySQL is running and SSL is configured!

