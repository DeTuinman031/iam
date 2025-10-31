# IAM Integration Guide

**Version:** 1.0  
**Date:** 2025-10-31  
**Purpose:** Guide for integrating IAM module into other projects

---

## Table of Contents

1. [Integration Patterns](#integration-patterns)
2. [API Specifications](#api-specifications)
3. [Connector Specifications](#connector-specifications)
4. [Containerization](#containerization)
5. [Authentication Flows](#authentication-flows)
6. [Security Considerations](#security-considerations)
7. [Deployment Scenarios](#deployment-scenarios)
8. [Common Issues and Solutions](#common-issues-and-solutions)
9. [Example Integrations](#example-integrations)

---

## Integration Patterns

IAM can be integrated in three ways:

### Pattern 1: Standalone Microservice (Recommended for Multiple Projects)

**Architecture:**
```
Project A (DORA Portal)     ┐
Project B (Ticketing)       ├──→  IAM Service (separate instance)
Project C (Monitoring)       ┘
```

**Pros:**
- Single source of truth
- Centralized user management
- Independent scaling
- One codebase to maintain

**Cons:**
- Network dependency
- Requires API/network access
- Latency considerations

### Pattern 2: Flask Blueprint (Embedded)

**Architecture:**
```
Project A ──→ Contains IAM blueprint (same process)
Project B ──→ Contains IAM blueprint (same process)
```

**Pros:**
- No network calls
- Fast (in-process)
- Shared database connection
- Simple deployment

**Cons:**
- Code duplication (or shared library)
- Each project has own IAM instance
- Database sharing required

### Pattern 3: Shared Library/Package

**Architecture:**
```
IAM Package (Python package)
    ├──→ Project A (imports as library)
    ├──→ Project B (imports as library)
    └──→ Project C (imports as library)
```

**Pros:**
- Code reuse
- Single codebase
- Easy updates (if versioned)

**Cons:**
- Each project manages its own instance
- Database coordination needed

**Recommendation:** Use Pattern 1 (Microservice) for internet-accessible projects.

---

## API Specifications

### Base URL Structure

```
Production:  https://iam.yourdomain.com
Development: http://iam-dev.yourdomain.com:5000
Local:       http://localhost:5000
```

### Authentication Endpoints

#### POST `/api/auth/login`
Authenticate user and create session.

**Request:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response (Success - 200):**
```json
{
  "status": "success",
  "user": {
    "user_id": 1,
    "username": "user@example.com",
    "display_name": "John Doe",
    "email": "user@example.com",
    "roles": ["admin", "developer"]
  },
  "session_token": "flask_session_token",
  "expires_at": "2025-11-01T10:00:00Z"
}
```

**Response (Error - 401):**
```json
{
  "status": "error",
  "message": "Invalid credentials"
}
```

#### GET `/api/auth/verify`
Verify current session/token.

**Headers:**
```
Cookie: session=flask_session_token
```

**Response (200):**
```json
{
  "authenticated": true,
  "user": {
    "user_id": 1,
    "username": "user@example.com",
    "roles": ["admin"]
  }
}
```

#### POST `/api/auth/logout`
Invalidate session.

**Headers:**
```
Cookie: session=flask_session_token
```

**Response (200):**
```json
{
  "status": "success",
  "message": "Logged out"
}
```

### User Management Endpoints

#### GET `/api/users`
List users (requires admin role).

**Query Parameters:**
- `page`: Page number (default: 1)
- `per_page`: Items per page (default: 50)
- `tenant_id`: Filter by tenant (optional)

**Response (200):**
```json
{
  "users": [
    {
      "user_id": 1,
      "username": "user@example.com",
      "email": "user@example.com",
      "display_name": "John Doe",
      "roles": ["admin"],
      "is_active": true,
      "is_locked": false
    }
  ],
  "total": 100,
  "page": 1,
  "per_page": 50
}
```

#### GET `/api/users/{user_id}`
Get user details.

#### POST `/api/users`
Create new user (requires admin role).

**Request:**
```json
{
  "username": "newuser@example.com",
  "email": "newuser@example.com",
  "display_name": "New User",
  "password": "securepassword",
  "parent_id": 1,
  "roles": ["readonly"]
}
```

### Role Management Endpoints

#### GET `/api/roles`
List all roles.

#### POST `/api/users/{user_id}/roles`
Assign role to user.

**Request:**
```json
{
  "role_id": 2
}
```

### Health Check

#### GET `/healthz`
Service health and database status.

**Response (200):**
```json
{
  "status": "ok",
  "service": "IAM",
  "database": "connected",
  "version": "1.1.0"
}
```

---

## Connector Specifications

### Python Connector (Recommended)

Create a Python client library that other projects can import.

**File:** `iam_client.py`

```python
import requests
from typing import Optional, Dict, List

class IAMClient:
    """Client for IAM service."""
    
    def __init__(self, base_url: str, session_cookie: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if session_cookie:
            self.session.cookies.set('session', session_cookie)
    
    def login(self, username: str, password: str) -> Dict:
        """Authenticate user."""
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password}
        )
        response.raise_for_status()
        return response.json()
    
    def verify_session(self) -> Dict:
        """Verify current session."""
        response = self.session.get(f"{self.base_url}/api/auth/verify")
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: int) -> Dict:
        """Get user details."""
        response = self.session.get(f"{self.base_url}/api/users/{user_id}")
        response.raise_for_status()
        return response.json()
    
    def list_users(self, page: int = 1, per_page: int = 50) -> Dict:
        """List users."""
        response = self.session.get(
            f"{self.base_url}/api/users",
            params={"page": page, "per_page": per_page}
        )
        response.raise_for_status()
        return response.json()
    
    def logout(self):
        """Logout current session."""
        response = self.session.post(f"{self.base_url}/api/auth/logout")
        response.raise_for_status()
        return response.json()
```

**Usage in other projects:**
```python
from iam_client import IAMClient

# Initialize client
iam = IAMClient(base_url="https://iam.yourdomain.com")

# Login
result = iam.login("user@example.com", "password")
session_token = result.get("session_token")

# Use authenticated client
iam_auth = IAMClient(
    base_url="https://iam.yourdomain.com",
    session_cookie=session_token
)

# Get user info
user_info = iam_auth.verify_session()
```

### Flask Integration (Blueprint)

For Flask projects, integrate IAM as a blueprint:

**In your project:**
```python
from flask import Flask
from iam.app import create_app as create_iam_app
from iam.app.auth.routes_admin import admin_bp as iam_admin_bp

def create_app():
    app = Flask(__name__)
    
    # Import IAM models and extensions
    from iam.app.extensions import db, login_manager
    from iam.app.config import Config
    
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    
    # Register IAM blueprints
    app.register_blueprint(iam_admin_bp, url_prefix="/auth")
    
    return app
```

### JavaScript/TypeScript Connector

For frontend integrations:

```typescript
class IAMClient {
    constructor(private baseUrl: string) {}
    
    async login(username: string, password: string): Promise<LoginResponse> {
        const response = await fetch(`${this.baseUrl}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
            credentials: 'include' // Important for cookies
        });
        return response.json();
    }
    
    async verifySession(): Promise<SessionResponse> {
        const response = await fetch(`${this.baseUrl}/api/auth/verify`, {
            credentials: 'include'
        });
        return response.json();
    }
    
    async logout(): Promise<void> {
        await fetch(`${this.baseUrl}/api/auth/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    }
}
```

---

## Containerization

### Dockerfile for IAM Service

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/
COPY manage.py .

# Environment variables
ENV FLASK_APP=app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

### Docker Compose Example

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.4
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: iam
      MYSQL_USER: iam_user
      MYSQL_PASSWORD: iam_pass
    volumes:
      - mysql_data:/var/lib/mysql
      - ./db/iam_schema.sql:/docker-entrypoint-initdb.d/01-schema.sql:ro
    ports:
      - "3306:3306"
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 10s
      timeout: 5s
      retries: 5

  iam:
    build: .
    environment:
      DATABASE_URL: mysql+pymysql://iam_user:iam_pass@mysql:3306/iam
      FLASK_SECRET_KEY: ${FLASK_SECRET_KEY}
      FLASK_ENV: production
    ports:
      - "5000:5000"
    depends_on:
      mysql:
        condition: service_healthy
    restart: unless-stopped

volumes:
  mysql_data:
```

### Kubernetes Deployment

**Deployment YAML:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: iam-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: iam
  template:
    metadata:
      labels:
        app: iam
    spec:
      containers:
      - name: iam
        image: yourregistry/iam:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: iam-secrets
              key: database-url
        - name: FLASK_SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: iam-secrets
              key: secret-key
---
apiVersion: v1
kind: Service
metadata:
  name: iam-service
spec:
  selector:
    app: iam
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

---

## Authentication Flows

### Flow 1: Direct Login (Current Implementation)

```
User → Project App → IAM Service (/api/auth/login)
                ← Session Cookie
Project App stores cookie → Uses for subsequent requests
```

### Flow 2: Token-Based (JWT) - Recommended for Microservices

```
User → Project App → IAM Service (/api/auth/login)
                ← JWT Token
Project App stores token → Sends in Authorization header
IAM Service validates token → Returns user info
```

**Implementation needed:**
- Add JWT token generation in IAM
- Store refresh tokens
- Add token refresh endpoint

### Flow 3: OAuth 2.0 / OpenID Connect

```
User → Project App → IAM Service (Authorization endpoint)
                ← Redirect to IAM login
User logs in → IAM → Redirect back with code
Project App exchanges code for token
```

**Implementation needed:**
- OAuth 2.0 provider implementation
- Token endpoint
- User info endpoint

### Flow 4: SSO/SAML (Enterprise)

```
User → Project App → Redirect to IAM SAML endpoint
IAM → External IdP (Azure AD, Okta)
IdP → IAM (SAML assertion)
IAM → Project App (user authenticated)
```

---

## Security Considerations

### 1. CORS Configuration

**For API access from other domains:**

```python
# In app/__init__.py
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    
    # Configure CORS
    CORS(app, 
         origins=["https://dora-portal.com", "https://ticketing.com"],
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"])
    
    return app
```

### 2. Session Security

**Production settings:**
```python
# config.py
class ProdConfig(Config):
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
```

### 3. Rate Limiting

**Add rate limiting:**
```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login_submit():
    # Login logic
```

### 4. API Keys for Service-to-Service

**For programmatic access:**
```python
@app.before_request
def verify_api_key():
    if request.path.startswith('/api/'):
        api_key = request.headers.get('X-API-Key')
        if not validate_api_key(api_key):
            return jsonify({"error": "Invalid API key"}), 401
```

### 5. HTTPS/TLS

**Mandatory for production:**
- Use reverse proxy (Nginx, Traefik) with SSL termination
- Or use cloud load balancer with SSL
- Never expose IAM service directly to internet without TLS

---

## Deployment Scenarios

### Scenario 1: Single IAM for Multiple Projects (Microservice)

```
Internet
  ├──→ Nginx/ALB (SSL Termination)
  │     ├──→ DORA Portal (project-a.com)
  │     ├──→ Ticketing System (tickets.com)
  │     └──→ Monitoring (monitor.com)
  │
  └──→ IAM Service (iam.yourdomain.com)
        └──→ MySQL Database
```

**Configuration:**
- IAM on dedicated subdomain: `iam.yourdomain.com`
- All projects redirect to IAM for login
- Session cookies with appropriate domain settings
- Shared database or API-based access

### Scenario 2: Embedded IAM (Same Domain)

```
Internet
  └──→ Project App (app.yourdomain.com)
          ├──→ /auth/* (IAM routes)
          └──→ /app/* (Application routes)
```

**Configuration:**
- IAM as blueprint in each project
- Shared database connection
- Same session domain

### Scenario 3: Kubernetes Multi-Tenant

```
Kubernetes Cluster
  ├──→ IAM Service (Deployment)
  ├──→ Project A (Deployment)
  ├──→ Project B (Deployment)
  └──→ Shared MySQL (StatefulSet)
```

---

## Common Issues and Solutions

### Issue 1: CORS Errors

**Symptom:** `Access-Control-Allow-Origin` errors in browser console.

**Solution:**
```python
from flask_cors import CORS

CORS(app, 
     origins=["https://trusted-domain.com"],
     supports_credentials=True)
```

### Issue 2: Session Cookie Not Sent

**Symptom:** Session not persisting across requests.

**Solution:**
- Ensure `credentials: 'include'` in fetch requests
- Set correct `SESSION_COOKIE_DOMAIN` (e.g., `.yourdomain.com` for subdomains)
- Use HTTPS in production

### Issue 3: Database Connection Pooling

**Symptom:** "Too many connections" errors.

**Solution:**
```python
# config.py
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 10,
    'pool_recycle': 3600,
    'pool_pre_ping': True,
    'max_overflow': 20
}
```

### Issue 4: Service Discovery

**Symptom:** Hardcoded URLs break in different environments.

**Solution:**
- Use environment variables
- Service discovery (Consul, etcd)
- DNS-based routing
- Kubernetes service names

### Issue 5: Authentication State Management

**Symptom:** User logged out unexpectedly.

**Solution:**
- Implement token refresh mechanism
- Use longer-lived refresh tokens
- Store session state in Redis for scalability
- Implement session timeout warnings

### Issue 6: Load Balancing Session Affinity

**Symptom:** Sessions lost when load balancing.

**Solution:**
- Use Redis for session storage (instead of Flask's default)
- Or enable sticky sessions in load balancer
- Or use JWT tokens (stateless)

```python
from flask_session import Session

app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
Session(app)
```

---

## Example Integrations

### Example 1: Flask Project Integration

```python
# In your project's app.py
from flask import Flask, session, redirect, url_for, request
from iam_client import IAMClient

app = Flask(__name__)
IAM_BASE_URL = "https://iam.yourdomain.com"
iam = IAMClient(IAM_BASE_URL)

@app.before_request
def require_auth():
    if request.endpoint not in ['login', 'static']:
        if 'iam_session' not in session:
            return redirect(url_for('login'))
        
        # Verify session is still valid
        try:
            result = iam.verify_session(
                session_cookie=session['iam_session']
            )
            if not result.get('authenticated'):
                return redirect(url_for('login'))
        except:
            return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        result = iam.login(username, password)
        if result.get('status') == 'success':
            session['iam_session'] = result['session_token']
            return redirect(url_for('dashboard'))
        else:
            return "Login failed", 401
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user_info = iam.verify_session(session_cookie=session['iam_session'])
    return render_template('dashboard.html', user=user_info['user'])
```

### Example 2: Django Project Integration

```python
# middleware.py
class IAMAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.iam = IAMClient("https://iam.yourdomain.com")
    
    def __call__(self, request):
        if 'iam_session' in request.session:
            try:
                result = self.iam.verify_session(
                    session_cookie=request.session['iam_session']
                )
                if result.get('authenticated'):
                    request.user = result['user']
            except:
                pass
        
        return self.get_response(request)

# views.py
from django.shortcuts import redirect

def login_view(request):
    if request.method == 'POST':
        iam = IAMClient("https://iam.yourdomain.com")
        result = iam.login(
            request.POST['username'],
            request.POST['password']
        )
        if result.get('status') == 'success':
            request.session['iam_session'] = result['session_token']
            return redirect('/dashboard')
    return render(request, 'login.html')
```

### Example 3: React/Vue Frontend Integration

```typescript
// authService.ts
import { IAMClient } from './iam-client';

class AuthService {
    private client: IAMClient;
    
    constructor() {
        this.client = new IAMClient('https://iam.yourdomain.com');
    }
    
    async login(username: string, password: string) {
        const result = await this.client.login(username, password);
        if (result.status === 'success') {
            localStorage.setItem('iam_session', result.session_token);
            return result;
        }
        throw new Error(result.message);
    }
    
    async checkAuth() {
        const session = localStorage.getItem('iam_session');
        if (!session) return false;
        
        try {
            const result = await this.client.verifySession();
            return result.authenticated;
        } catch {
            return false;
        }
    }
    
    logout() {
        localStorage.removeItem('iam_session');
        this.client.logout();
    }
}

// ProtectedRoute.tsx
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from './authService';

export function ProtectedRoute({ children }) {
    const [authenticated, setAuthenticated] = useState(false);
    const navigate = useNavigate();
    
    useEffect(() => {
        authService.checkAuth().then(isAuth => {
            if (!isAuth) {
                navigate('/login');
            } else {
                setAuthenticated(true);
            }
        });
    }, [navigate]);
    
    return authenticated ? children : null;
}
```

---

## Checklist for Integration

### Pre-Integration

- [ ] Decide on integration pattern (microservice vs embedded)
- [ ] Set up IAM service with proper domain/URL
- [ ] Configure CORS for allowed origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure database connection pooling
- [ ] Set up session storage (Redis if scaling)

### Security

- [ ] Enable HTTPS/TLS
- [ ] Configure secure session cookies
- [ ] Implement rate limiting
- [ ] Set up API keys for service-to-service auth
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerting

### Testing

- [ ] Test login/logout flows
- [ ] Test session persistence
- [ ] Test token refresh (if JWT)
- [ ] Test CORS from all client domains
- [ ] Load testing
- [ ] Security testing (OWASP)

### Deployment

- [ ] Containerize IAM service
- [ ] Set up CI/CD pipeline
- [ ] Configure environment variables
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Document API endpoints
- [ ] Create client libraries/SDKs

---

## Quick Start Integration

### For Flask Projects

```bash
# Install IAM client
pip install iam-client

# In your Flask app
from iam_client import IAMClient

iam = IAMClient("https://iam.yourdomain.com")
```

### For Other Languages

Use the REST API directly with appropriate HTTP client libraries:
- **Node.js:** `axios`, `node-fetch`
- **Go:** `net/http` or `resty`
- **Java:** `OkHttp`, `RestTemplate`
- **Ruby:** `faraday`, `httparty`

---

## Support and Maintenance

### Monitoring Endpoints

- `/healthz` - Service health
- `/metrics` - Prometheus metrics (to be implemented)

### Logging

Ensure structured logging for:
- Authentication events
- API access
- Errors and exceptions
- Performance metrics

### Updates

- Version API endpoints
- Maintain backward compatibility
- Use semantic versioning
- Document breaking changes

---

**End of Integration Guide**

