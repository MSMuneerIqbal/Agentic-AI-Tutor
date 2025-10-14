#!/usr/bin/env python3
"""
Comprehensive Backend API Testing Script
Tests all FastAPI endpoints systematically
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime
import time

class BackendTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": []
        }
        self.test_session_id = None
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
                response = self.session.get(url, headers=headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                return True, response.json() if response.content else {}
            else:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text}"
        except Exception as e:
            return False, str(e)
    
    def test_basic_endpoints(self):
        """Test basic API endpoints"""
        print("\n🔍 Testing Basic Endpoints")
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
    
    def test_metrics_endpoints(self):
        """Test metrics endpoints"""
        print("\n📊 Testing Metrics Endpoints")
        print("=" * 50)
        
        # Test metrics summary
        success, result = self.test_endpoint("GET", "/metrics/summary")
        self.log_test("Metrics summary", success, result if not success else None)
        
        # Test health metrics
        success, result = self.test_endpoint("GET", "/metrics/health")
        self.log_test("Health metrics", success, result if not success else None)
        
        # Test Prometheus metrics
        success, result = self.test_endpoint("GET", "/metrics/prometheus")
        self.log_test("Prometheus metrics", success, result if not success else None)
    
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
    
    def test_session_endpoints(self):
        """Test session management endpoints"""
        print("\n🎯 Testing Session Endpoints")
        print("=" * 50)
        
        # Test session creation
        session_data = {
            "user_email": self.test_user_email
        }
        success, result = self.test_endpoint("POST", "/api/v1/sessions/start", session_data)
        if success and "session_id" in result:
            self.test_session_id = result["session_id"]
            print(f"   📝 Session ID: {self.test_session_id}")
        self.log_test("Session creation", success, result if not success else None)
        
        # Test session retrieval
        if self.test_session_id:
            success, result = self.test_endpoint("GET", f"/api/v1/sessions/{self.test_session_id}")
            self.log_test("Session retrieval", success, result if not success else None)
    
    def test_profile_endpoints(self):
        """Test user profile endpoints"""
        print("\n👤 Testing Profile Endpoints")
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
    
    def test_assessment_endpoints(self):
        """Test assessment endpoints"""
        print("\n📝 Testing Assessment Endpoints")
        print("=" * 50)
        
        # Test assessment history
        success, result = self.test_endpoint("GET", f"/api/v1/assessments/{self.test_user_email}/history")
        self.log_test("Assessment history", success, result if not success else None)
        
        # Test learning style stats
        success, result = self.test_endpoint("GET", "/api/v1/assessments/stats/learning-styles")
        self.log_test("Learning style stats", success, result if not success else None)
    
    def test_plan_endpoints(self):
        """Test study plan endpoints"""
        print("\n📚 Testing Plan Endpoints")
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
        
        # Test plan stats
        success, result = self.test_endpoint("GET", "/api/v1/plans/stats")
        self.log_test("Plan stats", success, result if not success else None)
    
    def test_rag_endpoints(self):
        """Test RAG (Retrieval-Augmented Generation) endpoints"""
        print("\n🤖 Testing RAG Endpoints")
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
        
        # Test topic-specific content
        topic_data = {
            "topic": "Kubernetes pods",
            "agent_type": "tutor"
        }
        success, result = self.test_endpoint("POST", "/api/v1/rag/topic", topic_data)
        self.log_test("RAG topic content", success, result if not success else None)
    
    async def test_websocket_endpoint(self):
        """Test WebSocket endpoint"""
        print("\n🔌 Testing WebSocket Endpoint")
        print("=" * 50)
        
        if not self.test_session_id:
            print("❌ No session ID available for WebSocket test")
            return
        
        try:
            ws_url = f"ws://localhost:8000/ws/sessions/{self.test_session_id}"
            async with websockets.connect(ws_url) as websocket:
                # Wait for initial greeting
                initial_message = await websocket.recv()
                initial_data = json.loads(initial_message)
                
                if "text" in initial_data:
                    self.log_test("WebSocket connection", True)
                    print(f"   📨 Initial greeting: {initial_data['text'][:100]}...")
                    
                    # Send test message
                    test_message = {
                        "message": "Hello, test message",
                        "type": "user_message",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send(json.dumps(test_message))
                    
                    # Wait for response
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if "text" in response_data:
                        self.log_test("WebSocket message handling", True)
                        print(f"   📨 Response: {response_data['text'][:100]}...")
                    else:
                        self.log_test("WebSocket message handling", False, "No text in response")
                else:
                    self.log_test("WebSocket connection", False, "No greeting received")
                    
        except Exception as e:
            self.log_test("WebSocket endpoint", False, str(e))
    
    def test_phase6_endpoints(self):
        """Test Phase 6 advanced endpoints"""
        print("\n🚀 Testing Phase 6 Endpoints")
        print("=" * 50)
        
        # Test phase 6 status
        success, result = self.test_endpoint("GET", "/api/v1/phase6/status")
        self.log_test("Phase 6 status", success, result if not success else None)
        
        # Test phase 6 features
        success, result = self.test_endpoint("GET", "/api/v1/phase6/features")
        self.log_test("Phase 6 features", success, result if not success else None)
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🧪 COMPREHENSIVE BACKEND API TESTING")
        print("=" * 60)
        print(f"🔗 Base URL: {self.base_url}")
        print(f"📧 Test User: {self.test_user_email}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run all test categories
        self.test_basic_endpoints()
        self.test_metrics_endpoints()
        self.test_auth_endpoints()
        self.test_session_endpoints()
        self.test_profile_endpoints()
        self.test_assessment_endpoints()
        self.test_plan_endpoints()
        self.test_rag_endpoints()
        self.test_phase6_endpoints()
        
        # Test WebSocket (async)
        print("\n🔌 Testing WebSocket (Async)")
        print("=" * 50)
        asyncio.run(self.test_websocket_endpoint())
        
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
    tester = BackendTester()
    tester.run_all_tests()
