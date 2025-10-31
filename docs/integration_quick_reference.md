# IAM Integration Quick Reference

**Quick answers to common integration questions**

---

## Do We Need Containerization?

### ✅ **YES, Recommended for Production**

**Why:**
1. **Consistency:** Same environment across dev/staging/prod
2. **Isolation:** IAM service isolated from other services
3. **Scalability:** Easy to scale horizontally
4. **Portability:** Run on any platform (K8s, Docker Swarm, cloud)
5. **Dependencies:** MySQL, Python packages bundled

### Containerization Options:

1. **Docker Compose** (Simplest, single server)
   - Use for: Development, small deployments
   - Includes: IAM + MySQL in same compose file

2. **Docker** (Container orchestration)
   - Use for: Production with manual management
   - Deploy IAM and MySQL separately

3. **Kubernetes** (Best for multiple projects)
   - Use for: Production, multiple environments
   - Benefits: Auto-scaling, service discovery, load balancing

**Minimal Setup:** Docker Compose is sufficient for starting.

---

## Connector Specifications

### For Other Projects (What They Need)

#### 1. **API Endpoints** (REST)

All projects need to call these endpoints:

```
POST   /api/auth/login      - Authenticate user
GET    /api/auth/verify     - Verify session
POST   /api/auth/logout     - End session
GET    /api/users           - List users (admin)
GET    /api/users/{id}      - Get user details
GET    /api/roles           - List roles
GET    /healthz             - Health check
```

#### 2. **Authentication Method**

**Option A: Session Cookies (Current)**
- IAM sets cookie on login
- Projects pass cookie to IAM for verification
- Simple but requires same-origin or CORS

**Option B: JWT Tokens (Recommended for microservices)**
- IAM returns JWT token
- Projects store token, send in Authorization header
- Stateless, works across domains

**Option C: API Keys (Service-to-service)**
- For programmatic access
- Projects use API key in header
- For automated tasks

#### 3. **Client Library / SDK**

**Python Projects:**
```python
from iam_client import IAMClient

iam = IAMClient(base_url="https://iam.yourdomain.com")
result = iam.login(username, password)
```

**JavaScript/TypeScript Projects:**
```typescript
import { IAMClient } from '@yourcompany/iam-client';

const iam = new IAMClient('https://iam.yourdomain.com');
await iam.login(username, password);
```

**Other Languages:**
- Use REST API directly with HTTP client
- Follow API specifications in integration guide

---

## What Projects Need to Provide

### 1. **Configuration**

```python
# In project's config
IAM_SERVICE_URL = "https://iam.yourdomain.com"
IAM_API_KEY = "your-api-key"  # If using API keys
IAM_SESSION_COOKIE_NAME = "iam_session"
```

### 2. **Authentication Middleware/Decorator**

**Flask:**
```python
@app.before_request
def require_iam_auth():
    # Verify IAM session
    pass
```

**Django:**
```python
class IAMAuthMiddleware:
    # Verify IAM session
    pass
```

### 3. **User Context**

Projects need to store:
- User ID
- Username/Email
- Roles
- Session token

### 4. **Redirect Handling**

After IAM login, redirect back to:
```
https://iam.yourdomain.com/login?redirect=https://yourproject.com/callback
```

---

## Required API Endpoints (To Implement)

Currently, IAM has web routes but needs REST API endpoints:

### High Priority (Must Have)
- [ ] `POST /api/auth/login` - REST login endpoint
- [ ] `GET /api/auth/verify` - Verify session
- [ ] `POST /api/auth/logout` - REST logout
- [ ] `GET /api/users` - List users API
- [ ] `GET /api/users/{id}` - Get user API
- [ ] `GET /api/roles` - List roles API

### Medium Priority (Nice to Have)
- [ ] `POST /api/users` - Create user API
- [ ] `PATCH /api/users/{id}` - Update user API
- [ ] `POST /api/users/{id}/roles` - Assign role API
- [ ] `GET /api/audit-logs` - Audit log API

### Low Priority (Future)
- [ ] JWT token endpoints
- [ ] OAuth 2.0 endpoints
- [ ] SAML endpoints

---

## Likely Issues to Address

### 1. **CORS Configuration** ⚠️

**Issue:** Browser blocks requests to different domain.

**Solution:**
```python
from flask_cors import CORS

CORS(app, 
     origins=["https://project-a.com", "https://project-b.com"],
     supports_credentials=True)
```

**Add to requirements.txt:**
```
Flask-CORS>=4.0.0
```

### 2. **Session Cookie Domain** ⚠️

**Issue:** Cookies not shared across subdomains.

**Solution:**
```python
# For .yourdomain.com (shared across subdomains)
app.config['SESSION_COOKIE_DOMAIN'] = '.yourdomain.com'
```

### 3. **Network Latency** ⚠️

**Issue:** Each request adds network round-trip.

**Solution:**
- Cache user info in project (with TTL)
- Use JWT tokens (stateless)
- Implement connection pooling

### 4. **Service Discovery** ⚠️

**Issue:** Hardcoded URLs break in different environments.

**Solution:**
- Use environment variables
- DNS-based routing
- Service mesh (Istio, Linkerd)

### 5. **Database Connection Limits** ⚠️

**Issue:** Too many connections when multiple projects connect.

**Solution:**
```python
# Connection pooling
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'max_overflow': 40,
    'pool_recycle': 3600
}
```

### 6. **Session Storage at Scale** ⚠️

**Issue:** Flask default sessions don't scale across multiple instances.

**Solution:**
```python
# Use Redis for session storage
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://...')
Session(app)
```

### 7. **Rate Limiting** ⚠️

**Issue:** API abuse, brute force attacks.

**Solution:**
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)
limiter.limit("5 per minute")(login_endpoint)
```

### 8. **SSL/TLS Termination** ⚠️

**Issue:** Unencrypted traffic on internet.

**Solution:**
- Use reverse proxy (Nginx, Traefik)
- Cloud load balancer with SSL
- Let's Encrypt certificates

### 9. **Error Handling** ⚠️

**Issue:** IAM service down breaks all projects.

**Solution:**
- Implement circuit breaker pattern
- Graceful degradation
- Retry logic with exponential backoff

### 10. **Versioning** ⚠️

**Issue:** API changes break existing integrations.

**Solution:**
- Version API endpoints: `/api/v1/auth/login`
- Maintain backward compatibility
- Document deprecation timelines

---

## Recommended Architecture for Multiple Internet Projects

```
                    Internet
                       │
            ┌──────────┴──────────┐
            │   Nginx/ALB         │
            │   (SSL/TLS)         │
            └──────────┬──────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐   ┌────▼────┐   ┌────▼────┐
   │ Project │   │ Project │   │ Project │
   │    A    │   │    B    │   │    C    │
   └────┬────┘   └────┬────┘   └────┬────┘
        │              │              │
        └──────────────┼──────────────┘
                       │
                ┌──────▼──────┐
                │ IAM Service │
                │  (Docker)   │
                └──────┬──────┘
                       │
                ┌──────▼──────┐
                │   MySQL     │
                │  (Docker)   │
                └─────────────┘
```

**Deployment:**
- IAM on `iam.yourdomain.com` (dedicated subdomain)
- Projects redirect to IAM for login
- Shared session cookies or JWT tokens
- Docker Compose or Kubernetes

---

## Implementation Priority

### Phase 1: Basic Integration (Week 1)
1. ✅ Create REST API endpoints (`/api/auth/login`, `/api/auth/verify`)
2. ✅ Add CORS support
3. ✅ Create Python client library
4. ✅ Dockerize IAM service
5. ✅ Test with one project

### Phase 2: Production Ready (Week 2)
1. ✅ Add JWT token support (alternative to sessions)
2. ✅ Implement Redis session storage
3. ✅ Add rate limiting
4. ✅ SSL/TLS configuration
5. ✅ Monitoring and logging

### Phase 3: Advanced (Month 2)
1. ✅ OAuth 2.0 support
2. ✅ Multi-tenant isolation
3. ✅ Advanced RBAC
4. ✅ Audit log API
5. ✅ Admin API endpoints

---

## Quick Decision Tree

**Q: How many projects need IAM?**
- 1 project → Flask Blueprint (embedded)
- 2-3 projects → Microservice with Docker Compose
- 4+ projects → Microservice with Kubernetes

**Q: Projects on different domains?**
- Same domain → Session cookies work
- Different domains → JWT tokens or CORS + cookies

**Q: Internet-accessible?**
- Yes → Containerization required, SSL mandatory
- No (internal) → Simpler setup, session cookies OK

**Q: Need high availability?**
- Yes → Kubernetes, load balancing, Redis sessions
- No → Docker Compose sufficient

---

## Next Steps

1. **Review integration guide** (`docs/integration_guide.md`)
2. **Decide on integration pattern** (microservice recommended)
3. **Implement REST API endpoints** (currently only web routes exist)
4. **Create client library/SDK**
5. **Set up containerization** (Docker Compose minimum)
6. **Configure CORS and security**
7. **Test integration** with one project
8. **Scale to multiple projects**

---

**See also:**
- [Full Integration Guide](./integration_guide.md)
- [Setup Findings](./setup_findings_and_remediations.md)

