#!/usr/bin/env python3
"""
Quick Endpoint Status Check
"""

import requests
import json

def test_endpoint(method, endpoint, data=None):
    """Test a single endpoint"""
    url = f"http://localhost:8000{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        return response.status_code, "OK" if response.status_code in [200, 201] else f"Status: {response.status_code}"
    except Exception as e:
        return 0, str(e)

# Test key endpoints
endpoints = [
    ("GET", "/healthz"),
    ("GET", "/api/v1/sessions/start", {"user_email": "test@example.com"}),
    ("GET", "/api/v1/profiles/test@example.com"),
    ("GET", "/api/v1/assessments/test@example.com/history"),
    ("GET", "/api/v1/phase6/status"),
    ("GET", "/api/v1/phase6/features"),
]

print("🔍 QUICK ENDPOINT STATUS CHECK")
print("=" * 50)

working = 0
total = len(endpoints)

for method, endpoint, *data in endpoints:
    data = data[0] if data else None
    status, result = test_endpoint(method, endpoint, data)
    
    if status in [200, 201]:
        print(f"✅ WORKING - {endpoint}")
        working += 1
    else:
        print(f"❌ FAILING - {endpoint}: {result}")

print(f"\n📊 QUICK RESULTS: {working}/{total} working ({working/total*100:.1f}%)")