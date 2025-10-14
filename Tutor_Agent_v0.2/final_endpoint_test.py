#!/usr/bin/env python3
"""
Final Endpoint Test - Identify All Failing Endpoints
"""

import requests
import json

def test_endpoint(method, endpoint, data=None, expected_status=[200, 201]):
    """Test a single endpoint"""
    url = f"http://localhost:8000{endpoint}"
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=5)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        if response.status_code in expected_status:
            return True, f"Status: {response.status_code}"
        else:
            return False, f"Expected {expected_status}, got {response.status_code}"
    except Exception as e:
        return False, str(e)

# Test all endpoints systematically
endpoints = [
    # Basic endpoints
    ("GET", "/", "Root endpoint"),
    ("GET", "/healthz", "Health check"),
    ("GET", "/api/v1", "API info"),
    
    # Metrics endpoints
    ("GET", "/metrics/summary", "Metrics summary"),
    ("GET", "/metrics/health", "Health metrics"),
    ("GET", "/metrics/prometheus", "Prometheus metrics"),
    
    # Auth endpoints
    ("POST", "/api/v1/auth/register", "User registration", {
        "name": "Test User", 
        "email": "test@example.com", 
        "password": "testpass123"
    }),
    ("POST", "/api/v1/auth/login", "User login", {
        "email": "test@example.com", 
        "password": "testpass123"
    }),
    
    # Session endpoints
    ("POST", "/api/v1/sessions/start", "Session creation", {
        "user_email": "test@example.com"
    }),
    
    # Profile endpoints
    ("GET", "/api/v1/profiles/test@example.com", "Profile retrieval"),
    ("PUT", "/api/v1/profiles/test@example.com", "Profile update", {
        "learning_style": "visual",
        "assessment_confidence": 0.85
    }),
    
    # Assessment endpoints
    ("GET", "/api/v1/assessments/test@example.com/history", "Assessment history"),
    ("GET", "/api/v1/assessments/stats/learning-styles", "Learning style stats"),
    
    # Plan endpoints
    ("GET", "/api/v1/plans/test@example.com", "Plan list"),
    ("POST", "/api/v1/plans/test@example.com", "Plan creation", {
        "topics": ["Docker", "Kubernetes"],
        "learning_style": "visual",
        "estimated_hours": 10
    }),
    ("GET", "/api/v1/plans/stats", "Plan statistics"),
    
    # RAG endpoints
    ("POST", "/api/v1/rag/content", "RAG content", {
        "query": "Docker containers",
        "agent_type": "tutor"
    }),
    ("POST", "/api/v1/rag/lesson", "RAG lesson", {
        "topic": "Docker basics",
        "learning_style": "visual"
    }),
    ("POST", "/api/v1/rag/topic", "RAG topic", {
        "topic": "Kubernetes pods",
        "agent_type": "tutor"
    }),
    
    # Phase 6 endpoints
    ("GET", "/api/v1/phase6/status", "Phase 6 status"),
    ("GET", "/api/v1/phase6/features", "Phase 6 features"),
]

print("🔍 FINAL ENDPOINT TEST - ALL FAILING ENDPOINTS")
print("=" * 60)

working = []
failing = []

for endpoint_info in endpoints:
    method, endpoint, name = endpoint_info[0], endpoint_info[1], endpoint_info[2]
    data = endpoint_info[3] if len(endpoint_info) > 3 else None
    
    success, result = test_endpoint(method, endpoint, data)
    
    if success:
        working.append((method, endpoint, name, result))
    else:
        failing.append((method, endpoint, name, result))

print(f"✅ WORKING ENDPOINTS: {len(working)}")
for method, endpoint, name, result in working:
    print(f"   {method} {endpoint} - {name}")

print(f"\n❌ FAILING ENDPOINTS: {len(failing)}")
for method, endpoint, name, result in failing:
    print(f"   {method} {endpoint} - {name}: {result}")

print(f"\n📊 FINAL SCORE: {len(working)}/{len(working)+len(failing)} working ({len(working)/(len(working)+len(failing))*100:.1f}%)")

if len(failing) > 0:
    print(f"\n🚨 FAILING ENDPOINTS DETAILS:")
    for method, endpoint, name, result in failing:
        print(f"   ❌ {method} {endpoint}")
        print(f"      Name: {name}")
        print(f"      Error: {result}")
        print()
