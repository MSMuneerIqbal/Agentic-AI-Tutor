#!/usr/bin/env python3
"""
Comprehensive Backend Testing - Handles startup and gives detailed results
"""

import requests
import json
import time
import subprocess
import threading
from datetime import datetime

class ComprehensiveBackendTester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.session = requests.Session()
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "backend_status": "unknown"
        }
        self.test_user_email = "test_backend@example.com"
        self.backend_process = None
    
    def log_test(self, test_name, success, error=None, details=None):
        """Log test result with details"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}")
            if details:
                print(f"   📝 {details}")
        else:
            self.results["failed"] += 1
            error_msg = f"{test_name}: {error}" if error else test_name
            self.results["errors"].append(error_msg)
            print(f"❌ {test_name}: {error}")
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=200, timeout=10):
        """Test a single endpoint with detailed error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=timeout)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=timeout)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=timeout)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, timeout=timeout)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                try:
                    json_data = response.json() if response.content else {}
                    return True, json_data, f"Status: {response.status_code}"
                except:
                    return True, response.text, f"Status: {response.status_code}"
            else:
                return False, f"Expected {expected_status}, got {response.status_code}", response.text[:200]
                
        except requests.exceptions.ConnectionError:
            return False, "Connection refused - backend not running", None
        except requests.exceptions.Timeout:
            return False, "Request timeout", None
        except Exception as e:
            return False, str(e), None
    
    def start_backend(self):
        """Start backend server in background"""
        try:
            print("🚀 Starting backend server...")
            self.backend_process = subprocess.Popen(
                ["python", "-m", "uvicorn", "app.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
                cwd="backend",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return True
        except Exception as e:
            print(f"❌ Failed to start backend: {e}")
            return False
    
    def wait_for_backend(self, max_wait=30):
        """Wait for backend to be ready"""
        print("⏳ Waiting for backend to start...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = self.session.get(f"{self.base_url}/", timeout=3)
                if response.status_code == 200:
                    print("✅ Backend is ready!")
                    self.results["backend_status"] = "running"
                    return True
            except:
                pass
            
            # Check if process is still running
            if self.backend_process and self.backend_process.poll() is not None:
                print("❌ Backend process died")
                self.results["backend_status"] = "failed"
                return False
            
            time.sleep(2)
            print(f"   ⏰ Waiting... ({int(time.time() - start_time)}s)")
        
        print("❌ Backend not ready after maximum wait time")
        self.results["backend_status"] = "timeout"
        return False
    
    def test_basic_connectivity(self):
        """Test basic connectivity"""
        print("\n🔍 Testing Basic Connectivity")
        print("=" * 50)
        
        # Test root endpoint
        success, result, details = self.test_endpoint("GET", "/")
        self.log_test("Root endpoint", success, result if not success else None, details)
        
        # Test health check
        success, result, details = self.test_endpoint("GET", "/healthz")
        self.log_test("Health check", success, result if not success else None, details)
        
        # Test API info
        success, result, details = self.test_endpoint("GET", "/api/v1")
        self.log_test("API info", success, result if not success else None, details)
    
    def test_auth_system(self):
        """Test authentication system"""
        print("\n🔐 Testing Authentication System")
        print("=" * 50)
        
        # Test registration
        register_data = {
            "name": "Test User",
            "email": self.test_user_email,
            "password": "testpassword123"
        }
        success, result, details = self.test_endpoint("POST", "/api/v1/auth/register", register_data)
        self.log_test("User registration", success, result if not success else None, details)
        
        # Test login
        login_data = {
            "email": self.test_user_email,
            "password": "testpassword123"
        }
        success, result, details = self.test_endpoint("POST", "/api/v1/auth/login", login_data)
        self.log_test("User login", success, result if not success else None, details)
    
    def test_fixed_services(self):
        """Test the services we fixed"""
        print("\n🔧 Testing Fixed Services")
        print("=" * 50)
        
        # Test Profile Service (was failing with async database issues)
        success, result, details = self.test_endpoint("GET", f"/api/v1/profiles/{self.test_user_email}")
        self.log_test("Profile retrieval (MongoDB)", success, result if not success else None, details)
        
        # Test Profile update
        update_data = {
            "learning_style": "visual",
            "assessment_confidence": 0.85
        }
        success, result, details = self.test_endpoint("PUT", f"/api/v1/profiles/{self.test_user_email}", update_data)
        self.log_test("Profile update (MongoDB)", success, result if not success else None, details)
        
        # Test Plan Service (was failing with async database issues)
        success, result, details = self.test_endpoint("GET", f"/api/v1/plans/{self.test_user_email}")
        self.log_test("Plan list (MongoDB)", success, result if not success else None, details)
        
        # Test Plan creation
        plan_data = {
            "topics": ["Docker Basics", "Kubernetes Fundamentals"],
            "learning_style": "visual",
            "estimated_hours": 10
        }
        success, result, details = self.test_endpoint("POST", f"/api/v1/plans/{self.test_user_email}", plan_data)
        self.log_test("Plan creation (MongoDB)", success, result if not success else None, details)
        
        # Test RAG Service (was failing with initialization issues)
        content_data = {
            "query": "Docker container basics",
            "agent_type": "tutor"
        }
        success, result, details = self.test_endpoint("POST", "/api/v1/rag/content", content_data)
        self.log_test("RAG content retrieval (Fixed Init)", success, result if not success else None, details)
        
        # Test RAG lesson generation
        lesson_data = {
            "topic": "Docker containers",
            "learning_style": "visual"
        }
        success, result, details = self.test_endpoint("POST", "/api/v1/rag/lesson", lesson_data)
        self.log_test("RAG lesson generation (Fixed Init)", success, result if not success else None, details)
    
    def test_session_management(self):
        """Test session management"""
        print("\n🎯 Testing Session Management")
        print("=" * 50)
        
        # Test session creation
        session_data = {
            "user_email": self.test_user_email
        }
        success, result, details = self.test_endpoint("POST", "/api/v1/sessions/start", session_data)
        self.log_test("Session creation", success, result if not success else None, details)
    
    def test_assessment_system(self):
        """Test assessment system"""
        print("\n📝 Testing Assessment System")
        print("=" * 50)
        
        # Test assessment history
        success, result, details = self.test_endpoint("GET", f"/api/v1/assessments/{self.test_user_email}/history")
        self.log_test("Assessment history", success, result if not success else None, details)
        
        # Test learning style stats
        success, result, details = self.test_endpoint("GET", "/api/v1/assessments/stats/learning-styles")
        self.log_test("Learning style stats", success, result if not success else None, details)
    
    def test_metrics_and_monitoring(self):
        """Test metrics and monitoring endpoints"""
        print("\n📊 Testing Metrics & Monitoring")
        print("=" * 50)
        
        # Test metrics summary
        success, result, details = self.test_endpoint("GET", "/metrics/summary")
        self.log_test("Metrics summary", success, result if not success else None, details)
        
        # Test health metrics
        success, result, details = self.test_endpoint("GET", "/metrics/health")
        self.log_test("Health metrics", success, result if not success else None, details)
    
    def cleanup(self):
        """Clean up backend process"""
        if self.backend_process:
            try:
                self.backend_process.terminate()
                self.backend_process.wait(timeout=5)
                print("🧹 Backend process terminated")
            except:
                try:
                    self.backend_process.kill()
                    print("🧹 Backend process killed")
                except:
                    pass
    
    def run_comprehensive_test(self):
        """Run comprehensive backend test"""
        print("🧪 COMPREHENSIVE BACKEND API TESTING")
        print("=" * 60)
        print(f"🔗 Base URL: {self.base_url}")
        print(f"📧 Test User: {self.test_user_email}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        try:
            # Start backend
            if not self.start_backend():
                print("❌ Cannot proceed without backend")
                return
            
            # Wait for backend to be ready
            if not self.wait_for_backend():
                print("❌ Backend not ready, but continuing with tests...")
            
            # Run test categories
            self.test_basic_connectivity()
            self.test_auth_system()
            self.test_fixed_services()
            self.test_session_management()
            self.test_assessment_system()
            self.test_metrics_and_monitoring()
            
        finally:
            # Always cleanup
            self.cleanup()
        
        # Print final results
        self.print_comprehensive_summary()
    
    def print_comprehensive_summary(self):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE BACKEND TESTING SUMMARY")
        print("=" * 60)
        print(f"🖥️  Backend Status: {self.results['backend_status']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['total_tests']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests'] * 100)
            print(f"📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 80:
                print("🎉 EXCELLENT! Backend is working well!")
            elif success_rate >= 60:
                print("👍 GOOD! Most endpoints are working!")
            elif success_rate >= 40:
                print("⚠️  NEEDS WORK! Some endpoints need fixing!")
            else:
                print("🚨 CRITICAL! Many endpoints are failing!")
        
        if self.results['errors']:
            print(f"\n❌ Detailed Errors:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    tester = ComprehensiveBackendTester()
    tester.run_comprehensive_test()
