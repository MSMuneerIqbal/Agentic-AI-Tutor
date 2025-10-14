#!/usr/bin/env python3
"""
Quick Backend API Testing Script
Tests core endpoints to verify fixes
"""

import requests
import json
import time
from datetime import datetime

class QuickBackendTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.test_user_email = "test_backend@example.com"
    
    def log_test(self, test_name, success, error=None):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")
    
    def test_endpoint(self, method, endpoint, data=None, headers=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=headers, timeout=5)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers, timeout=5)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers, timeout=5)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=5)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                return True, response.json() if response.content else {}
            else:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}"
        except Exception as e:
            return False, str(e)
    
    def wait_for_backend(self, max_attempts=10):
        """Wait for backend to be ready"""
        print("🔄 Waiting for backend to start...")
        for attempt in range(max_attempts):
            try:
                response = self.session.get(f"{self.base_url}/", timeout=3)
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    return True
            except:
                pass
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            time.sleep(2)
        
        print("❌ Backend not ready after maximum attempts")
        return False
    
    def test_core_endpoints(self):
        """Test core endpoints that were failing"""
        print("\n🔍 Testing Core Endpoints")
        print("=" * 50)
        
        # Test root endpoint
        success, result = self.test_endpoint("GET", "/")
        self.log_test("Root endpoint", success, result if not success else None)
        
        # Test health check
        success, result = self.test_endpoint("GET", "/healthz")
        self.log_test("Health check endpoint", success, result if not success else None)
        
        # Test API info
        success, result = self.test_endpoint("GET", "/api/v1")
        self.log_test("API info endpoint", success, result if not success else None)
    
    def test_auth_endpoints(self):
        """Test authentication endpoints"""
        print("\n🔐 Testing Authentication Endpoints")
        print("=" * 50)
        
        # Test user registration
        register_data = {
            "name": "Test User",
            "email": self.test_user_email,
            "password": "testpassword123"
        }
        success, result = self.test_endpoint("POST", "/api/v1/auth/register", register_data)
        self.log_test("User registration", success, result if not success else None)
        
        # Test user login
        login_data = {
            "email": self.test_user_email,
            "password": "testpassword123"
        }
        success, result = self.test_endpoint("POST", "/api/v1/auth/login", login_data)
        self.log_test("User login", success, result if not success else None)
    
    def test_profile_endpoints(self):
        """Test profile endpoints that were failing"""
        print("\n👤 Testing Profile Endpoints (Previously Failing)")
        print("=" * 50)
        
        # Test profile retrieval
        success, result = self.test_endpoint("GET", f"/api/v1/profiles/{self.test_user_email}")
        self.log_test("Profile retrieval", success, result if not success else None)
        
        # Test profile update
        update_data = {
            "learning_style": "visual",
            "assessment_confidence": 0.85
        }
        success, result = self.test_endpoint("PUT", f"/api/v1/profiles/{self.test_user_email}", update_data)
        self.log_test("Profile update", success, result if not success else None)
    
    def test_plan_endpoints(self):
        """Test plan endpoints that were failing"""
        print("\n📚 Testing Plan Endpoints (Previously Failing)")
        print("=" * 50)
        
        # Test plan list
        success, result = self.test_endpoint("GET", f"/api/v1/plans/{self.test_user_email}")
        self.log_test("Plan list", success, result if not success else None)
        
        # Test plan creation
        plan_data = {
            "topics": ["Docker Basics", "Kubernetes Fundamentals"],
            "learning_style": "visual",
            "estimated_hours": 10
        }
        success, result = self.test_endpoint("POST", f"/api/v1/plans/{self.test_user_email}", plan_data)
        self.log_test("Plan creation", success, result if not success else None)
    
    def test_rag_endpoints(self):
        """Test RAG endpoints that were failing"""
        print("\n🤖 Testing RAG Endpoints (Previously Failing)")
        print("=" * 50)
        
        # Test content retrieval
        content_data = {
            "query": "Docker container basics",
            "agent_type": "tutor"
        }
        success, result = self.test_endpoint("POST", "/api/v1/rag/content", content_data)
        self.log_test("RAG content retrieval", success, result if not success else None)
        
        # Test lesson generation
        lesson_data = {
            "topic": "Docker containers",
            "learning_style": "visual"
        }
        success, result = self.test_endpoint("POST", "/api/v1/rag/lesson", lesson_data)
        self.log_test("RAG lesson generation", success, result if not success else None)
    
    def test_session_endpoints(self):
        """Test session endpoints"""
        print("\n🎯 Testing Session Endpoints")
        print("=" * 50)
        
        # Test session creation
        session_data = {
            "user_email": self.test_user_email
        }
        success, result = self.test_endpoint("POST", "/api/v1/sessions/start", session_data)
        self.log_test("Session creation", success, result if not success else None)
    
    def run_quick_tests(self):
        """Run quick backend tests"""
        print("🧪 QUICK BACKEND API TESTING")
        print("=" * 60)
        print(f"🔗 Base URL: {self.base_url}")
        print(f"📧 Test User: {self.test_user_email}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Wait for backend to be ready
        if not self.wait_for_backend():
            print("❌ Backend not available, skipping tests")
            return
        
        # Run test categories
        self.test_core_endpoints()
        self.test_auth_endpoints()
        self.test_profile_endpoints()
        self.test_plan_endpoints()
        self.test_rag_endpoints()
        self.test_session_endpoints()
        
        # Print final results
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 BACKEND TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['total_tests']}")
        print(f"📈 Success Rate: {(self.results['passed'] / self.results['total_tests'] * 100):.1f}%")
        
        if self.results['errors']:
            print(f"\n❌ Errors:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    tester = QuickBackendTester()
    tester.run_quick_tests()
