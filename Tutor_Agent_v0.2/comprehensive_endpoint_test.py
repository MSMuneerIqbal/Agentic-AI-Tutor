#!/usr/bin/env python3
"""
Comprehensive Endpoint Testing - Exact Count of Working vs Non-Working
"""

import requests
import json
from datetime import datetime

class EndpointTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.working_endpoints = []
        self.failing_endpoints = []
        self.test_user = "test_endpoint@example.com"
        self.session_id = None
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=[200, 201]):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = requests.get(url, timeout=5)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=5)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, timeout=5)
            elif method.upper() == "DELETE":
                response = requests.delete(url, timeout=5)
            else:
                return False, f"Unsupported method: {method}"
            
            if response.status_code in expected_status:
                return True, f"Status: {response.status_code}"
            else:
                return False, f"Expected {expected_status}, got {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused"
        except requests.exceptions.Timeout:
            return False, "Timeout"
        except Exception as e:
            return False, str(e)
    
    def run_all_tests(self):
        """Test all endpoints systematically"""
        print("🔍 COMPREHENSIVE ENDPOINT TESTING")
        print("=" * 60)
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Define all endpoints to test
        endpoints = [
            # Basic endpoints
            ("GET", "/", "Root endpoint"),
            ("GET", "/healthz", "Health check"),
            ("GET", "/api/v1", "API info"),
            
            # Metrics endpoints
            ("GET", "/metrics/summary", "Metrics summary"),
            ("GET", "/metrics/health", "Health metrics"),
            ("GET", "/metrics/prometheus", "Prometheus metrics"),
            
            # Authentication endpoints
            ("POST", "/api/v1/auth/register", "User registration", {
                "name": "Test User", 
                "email": self.test_user, 
                "password": "testpass123"
            }),
            ("POST", "/api/v1/auth/login", "User login", {
                "email": self.test_user, 
                "password": "testpass123"
            }),
            
            # Session endpoints
            ("POST", "/api/v1/sessions/start", "Session creation", {
                "user_email": self.test_user
            }),
            
            # Profile endpoints
            ("GET", f"/api/v1/profiles/{self.test_user}", "Profile retrieval"),
            ("PUT", f"/api/v1/profiles/{self.test_user}", "Profile update", {
                "learning_style": "visual",
                "assessment_confidence": 0.85
            }),
            
            # Assessment endpoints
            ("GET", f"/api/v1/assessments/{self.test_user}/history", "Assessment history"),
            ("GET", "/api/v1/assessments/stats/learning-styles", "Learning style stats"),
            
            # Plan endpoints
            ("GET", f"/api/v1/plans/{self.test_user}", "Plan list"),
            ("POST", f"/api/v1/plans/{self.test_user}", "Plan creation", {
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
        
        # Run tests
        for endpoint_info in endpoints:
            method, endpoint, name = endpoint_info[0], endpoint_info[1], endpoint_info[2]
            data = endpoint_info[3] if len(endpoint_info) > 3 else None
            
            success, result = self.test_endpoint(method, endpoint, data)
            
            if success:
                self.working_endpoints.append((method, endpoint, name, result))
                print(f"✅ WORKING - {name}")
            else:
                self.failing_endpoints.append((method, endpoint, name, result))
                print(f"❌ FAILING - {name}: {result}")
            
            # Store session ID for later tests
            if success and "session_id" in str(result) and not self.session_id:
                try:
                    if data and "user_email" in data:
                        # This was session creation, try to extract session ID
                        pass
                except:
                    pass
        
        # Test session retrieval if we have a session ID
        if self.session_id:
            success, result = self.test_endpoint("GET", f"/api/v1/sessions/{self.session_id}")
            if success:
                self.working_endpoints.append(("GET", f"/api/v1/sessions/{self.session_id}", "Session retrieval", result))
                print(f"✅ WORKING - Session retrieval")
            else:
                self.failing_endpoints.append(("GET", f"/api/v1/sessions/{self.session_id}", "Session retrieval", result))
                print(f"❌ FAILING - Session retrieval: {result}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE ENDPOINT TEST RESULTS")
        print("=" * 60)
        
        total_endpoints = len(self.working_endpoints) + len(self.failing_endpoints)
        working_count = len(self.working_endpoints)
        failing_count = len(self.failing_endpoints)
        
        print(f"✅ WORKING ENDPOINTS: {working_count}")
        print(f"❌ FAILING ENDPOINTS: {failing_count}")
        print(f"📊 TOTAL ENDPOINTS: {total_endpoints}")
        
        if total_endpoints > 0:
            success_rate = (working_count / total_endpoints) * 100
            print(f"📈 SUCCESS RATE: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("🎉 EXCELLENT! Backend is working very well!")
            elif success_rate >= 80:
                print("👍 GOOD! Most endpoints are working!")
            elif success_rate >= 70:
                print("⚠️  FAIR! Some endpoints need attention!")
            elif success_rate >= 50:
                print("🚨 POOR! Many endpoints need fixing!")
            else:
                print("💥 CRITICAL! Most endpoints are broken!")
        
        print(f"\n✅ WORKING ENDPOINTS ({working_count}):")
        for method, endpoint, name, result in self.working_endpoints:
            print(f"   {method} {endpoint} - {name}")
        
        print(f"\n❌ FAILING ENDPOINTS ({failing_count}):")
        for method, endpoint, name, result in self.failing_endpoints:
            print(f"   {method} {endpoint} - {name}: {result}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    tester = EndpointTester()
    tester.run_all_tests()
