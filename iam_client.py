#!/usr/bin/env python3
"""
IAM Client Library
Simple client for interacting with IAM service via REST API.
Version: v1.1.1

Usage:
    from iam_client import IAMClient
    
    client = IAMClient(base_url="https://iam.yourdomain.com")
    result = client.login("username", "password")
"""
import requests
from typing import Optional, Dict, List
import warnings


class IAMClient:
    """Client for IAM service REST API."""
    
    def __init__(self, base_url: str, session_cookie: Optional[str] = None):
        """
        Initialize IAM client.
        
        Args:
            base_url: Base URL of IAM service (e.g., "https://iam.yourdomain.com")
            session_cookie: Optional session cookie for authenticated requests
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        if session_cookie:
            self.session.cookies.set('session', session_cookie)
    
    def login(self, username: str, password: str) -> Dict:
        """
        Authenticate user and establish session.
        
        Args:
            username: Username or email
            password: User password
            
        Returns:
            Dict with status, user info, and session details
            
        Raises:
            requests.RequestException: On network or HTTP errors
        """
        response = self.session.post(
            f"{self.base_url}/api/auth/login",
            json={"username": username, "password": password},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        # Store session cookie if login successful
        if data.get('status') == 'success' and 'session' in response.cookies:
            self.session.cookies.set('session', response.cookies['session'])
        
        return data
    
    def verify_session(self) -> Dict:
        """
        Verify current session is valid.
        
        Returns:
            Dict with authentication status and user info
            
        Raises:
            requests.RequestException: On network or HTTP errors
        """
        response = self.session.get(f"{self.base_url}/api/auth/verify", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def logout(self) -> Dict:
        """
        Invalidate current session.
        
        Returns:
            Dict with logout status
        """
        response = self.session.post(f"{self.base_url}/api/auth/logout", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def get_user(self, user_id: int) -> Dict:
        """
        Get user details by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Dict with user information
        """
        response = self.session.get(f"{self.base_url}/api/users/{user_id}", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def list_users(self, page: int = 1, per_page: int = 50) -> Dict:
        """
        List all users with pagination.
        
        Args:
            page: Page number (default: 1)
            per_page: Items per page (default: 50, max: 100)
            
        Returns:
            Dict with users list and pagination info
        """
        params = {"page": page, "per_page": min(per_page, 100)}
        response = self.session.get(f"{self.base_url}/api/users", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def list_roles(self) -> Dict:
        """
        List all roles.
        
        Returns:
            Dict with roles list
        """
        response = self.session.get(f"{self.base_url}/api/roles", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def get_audit_logs(self, limit: int = 100) -> Dict:
        """
        Get recent audit logs.
        
        Args:
            limit: Maximum number of logs (default: 100, max: 500)
            
        Returns:
            Dict with audit logs list
        """
        params = {"limit": min(limit, 500)}
        response = self.session.get(f"{self.base_url}/api/audit/logs", params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    
    def get_active_sessions(self) -> Dict:
        """
        Get list of active sessions.
        
        Returns:
            Dict with active sessions list
        """
        response = self.session.get(f"{self.base_url}/api/sessions/active", timeout=5)
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict:
        """
        Check IAM service health.
        
        Returns:
            Dict with service status
        """
        response = self.session.get(f"{self.base_url}/healthz", timeout=5)
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python iam_client.py <base_url>")
        print("Example: python iam_client.py http://localhost:5000")
        sys.exit(1)
    
    base_url = sys.argv[1]
    
    # Create client
    client = IAMClient(base_url)
    
    # Test health check
    print("Testing health check...")
    try:
        health = client.health_check()
        print(f"✅ Health check: {health}")
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        sys.exit(1)
    
    # Test login
    print("\nTesting login...")
    try:
        result = client.login("testuser", "testpass123")
        if result.get('status') == 'success':
            print(f"✅ Login successful")
            print(f"   User: {result.get('user', {}).get('username')}")
            print(f"   Roles: {result.get('user', {}).get('roles')}")
        else:
            print(f"❌ Login failed: {result.get('message')}")
    except Exception as e:
        print(f"❌ Login error: {e}")
    
    # Test verify session
    print("\nTesting session verification...")
    try:
        result = client.verify_session()
        if result.get('authenticated'):
            print(f"✅ Session valid")
            print(f"   User: {result.get('user', {}).get('username')}")
        else:
            print(f"❌ Session invalid")
    except Exception as e:
        print(f"❌ Verify error: {e}")
    
    # Test list users
    print("\nTesting list users...")
    try:
        result = client.list_users(per_page=5)
        print(f"✅ Found {result.get('total', 0)} users")
        for user in result.get('users', [])[:3]:
            print(f"   - {user.get('username')} ({user.get('email')})")
    except Exception as e:
        print(f"❌ List users error: {e}")

