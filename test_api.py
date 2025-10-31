#!/usr/bin/env python3
"""
Test script for IAM REST API endpoints.
Usage: python test_api.py
"""
import json
from app import create_app

app = create_app()

def test_endpoints():
    """Test all API endpoints."""
    with app.test_client() as client:
        print("=" * 70)
        print("IAM REST API Endpoint Tests")
        print("=" * 70)
        
        # Test 1: Health check
        print("\n1. GET /healthz")
        response = client.get('/healthz')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ {data}")
        else:
            print(f"   ❌ Error")
        
        # Test 2: API Login
        print("\n2. POST /api/auth/login")
        response = client.post('/api/auth/login',
            json={"username": "testuser", "password": "testpass123"},
            content_type='application/json'
        )
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Login successful")
            print(f"   User: {data.get('user', {}).get('username')}")
            session_token = response.headers.get('Set-Cookie')
        else:
            print(f"   ❌ {response.data.decode()[:100]}")
            return
        
        # Test 3: Verify Session
        print("\n3. GET /api/auth/verify")
        with client.session_transaction() as sess:
            from app.auth.models import IAMUserAccount
            with app.app_context():
                user = IAMUserAccount.query.filter_by(username='testuser').first()
                if user:
                    sess['_user_id'] = str(user.user_id)
        
        response = client.get('/api/auth/verify')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Authenticated: {data.get('authenticated')}")
        
        # Test 4: List Users
        print("\n4. GET /api/users")
        response = client.get('/api/users?per_page=5')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Total users: {data.get('total', 0)}")
            for user in data.get('users', [])[:3]:
                print(f"      - {user.get('username')}")
        
        # Test 5: List Roles
        print("\n5. GET /api/roles")
        response = client.get('/api/roles')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Found {len(data.get('roles', []))} roles:")
            for role in data.get('roles', []):
                print(f"      - {role.get('role_name')} ({role.get('user_count')} users)")
        
        # Test 6: Audit Logs
        print("\n6. GET /api/audit/logs")
        response = client.get('/api/audit/logs?limit=10')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Found {data.get('total', 0)} logs")
            for log in data.get('logs', [])[:3]:
                print(f"      - {log.get('event_type')} by {log.get('username', 'Unknown')}")
        
        # Test 7: Active Sessions
        print("\n7. GET /api/sessions/active")
        response = client.get('/api/sessions/active')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = json.loads(response.data)
            print(f"   ✅ Found {data.get('total', 0)} active sessions")
        
        # Test 8: Logout
        print("\n8. POST /api/auth/logout")
        response = client.post('/api/auth/logout')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   ✅ Logout successful")
        
        print("\n" + "=" * 70)
        print("All API tests completed!")
        print("=" * 70)

if __name__ == "__main__":
    test_endpoints()

