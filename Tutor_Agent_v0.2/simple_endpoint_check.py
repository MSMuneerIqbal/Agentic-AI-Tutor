#!/usr/bin/env python3
import requests

def test_endpoint(endpoint, method="GET", data=None):
    try:
        url = f"http://localhost:8000{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=3)
        else:
            response = requests.post(url, json=data, timeout=3)
        
        if response.status_code in [200, 201]:
            return f"✅ WORKING"
        else:
            return f"❌ FAILING - Status: {response.status_code}"
    except Exception as e:
        return f"❌ FAILING - Error: {str(e)[:50]}"

print("🔍 ENDPOINT STATUS CHECK")
print("=" * 50)

# Test key endpoints
tests = [
    ("/healthz", "GET"),
    ("/api/v1/sessions/start", "POST", {"user_email": "test@example.com"}),
    ("/api/v1/profiles/test@example.com", "GET"),
    ("/api/v1/assessments/test@example.com/history", "GET"),
    ("/api/v1/assessments/stats/learning-styles", "GET"),
    ("/api/v1/plans/test@example.com", "GET"),
    ("/api/v1/plans/stats", "GET"),
    ("/api/v1/phase6/status", "GET"),
    ("/api/v1/phase6/features", "GET"),
    ("/api/v1/rag/content", "POST", {"query": "Docker", "agent_type": "tutor"}),
]

working = 0
total = len(tests)

for endpoint, method, *data in tests:
    data = data[0] if data else None
    result = test_endpoint(endpoint, method, data)
    print(f"{endpoint:<40} {result}")
    if "✅ WORKING" in result:
        working += 1

print("=" * 50)
print(f"📊 RESULTS: {working}/{total} working ({working/total*100:.1f}%)")
