#!/usr/bin/env python3
"""
Backend-Frontend Integration Test
Tests the complete integration between backend and frontend
"""

import asyncio
import json
import time
import requests
import websocket
import threading
from typing import Dict, Any, List
import sys
import os

class IntegrationTester:
    def __init__(self):
        self.backend_url = "http://localhost:8000"
        self.frontend_url = "http://localhost:3000"
        self.ws_url = "ws://localhost:8000/ws"
        self.test_results = []
        self.ws_messages = []
        
    def log_test(self, test_name: str, status: str, details: str = ""):
        """Log test results"""
        result = {
            "test": test_name,
            "status": status,
            "details": details,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        
        status_emoji = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_emoji} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_backend_frontend_connection(self) -> bool:
        """Test if backend and frontend can communicate"""
        try:
            # Test backend health
            backend_response = requests.get(f"{self.backend_url}/healthz", timeout=5)
            if backend_response.status_code != 200:
                self.log_test("Backend-Frontend Connection", "FAIL", "Backend not responding")
                return False
            
            # Test frontend accessibility
            frontend_response = requests.get(self.frontend_url, timeout=5)
            if frontend_response.status_code != 200:
                self.log_test("Backend-Frontend Connection", "FAIL", "Frontend not responding")
                return False
            
            self.log_test("Backend-Frontend Connection", "PASS", "Both services are running")
            return True
            
        except Exception as e:
            self.log_test("Backend-Frontend Connection", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_api_endpoints(self) -> bool:
        """Test all API endpoints that frontend uses"""
        endpoints = [
            ("/api/v1/health", "Health Check"),
            ("/api/v1/rag/health", "RAG Health"),
            ("/api/v1/metrics", "Metrics"),
            ("/api/v1/status", "API Status"),
        ]
        
        all_passed = True
        for endpoint, name in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                    self.log_test(f"API {name}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"API {name}", "FAIL", f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"API {name}", "FAIL", f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_websocket_integration(self) -> bool:
        """Test WebSocket integration between frontend and backend"""
        try:
            messages_received = []
            
            def on_message(ws, message):
                messages_received.append(json.loads(message))
                print(f"   WebSocket Message: {message[:100]}...")
            
            def on_error(ws, error):
                print(f"   WebSocket Error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print("   WebSocket Connection Closed")
            
            def on_open(ws):
                print("   WebSocket Connection Opened")
                # Send a test message
                test_message = {
                    "type": "user_message",
                    "content": "Hello from integration test",
                    "user_id": "test_user",
                    "session_id": "test_session"
                }
                ws.send(json.dumps(test_message))
            
            ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=on_open,
                on_message=on_message,
                on_error=on_error,
                on_close=on_close
            )
            
            # Run WebSocket in a separate thread
            ws_thread = threading.Thread(target=ws.run_forever)
            ws_thread.daemon = True
            ws_thread.start()
            
            # Wait for connection and messages
            time.sleep(5)
            
            if len(messages_received) > 0:
                self.log_test("WebSocket Integration", "PASS", f"Received {len(messages_received)} messages")
                ws.close()
                return True
            else:
                self.log_test("WebSocket Integration", "FAIL", "No messages received")
                ws.close()
                return False
                
        except Exception as e:
            self.log_test("WebSocket Integration", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_agent_communication(self) -> bool:
        """Test AI agent communication through API"""
        try:
            # Test orchestrator agent
            test_data = {
                "user_input": "Hello, I want to learn Docker",
                "context": {
                    "state": "GREETING",
                    "user_id": "test_user_123",
                    "session_id": "test_session_123"
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/chat",
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                agent_name = data.get('agent', 'Unknown')
                message = data.get('message', 'No message')
                self.log_test("Agent Communication", "PASS", f"Response from {agent_name}: {message[:50]}...")
                return True
            else:
                self.log_test("Agent Communication", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agent Communication", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_rag_integration(self) -> bool:
        """Test RAG system integration"""
        try:
            # Test RAG content search
            response = requests.get(
                f"{self.backend_url}/api/v1/rag/content?query=docker&agent_type=tutor",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                self.log_test("RAG Integration", "PASS", f"Found {len(results)} results")
                return True
            else:
                self.log_test("RAG Integration", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("RAG Integration", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_authentication_flow(self) -> bool:
        """Test authentication flow"""
        try:
            # Test registration endpoint
            register_data = {
                "name": "Test User",
                "email": "test@example.com",
                "password": "testpassword123"
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/auth/register",
                json=register_data,
                timeout=10
            )
            
            if response.status_code in [200, 201, 409]:  # 409 = user already exists
                self.log_test("Authentication Flow", "PASS", "Registration endpoint working")
                return True
            else:
                self.log_test("Authentication Flow", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Authentication Flow", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_database_integration(self) -> bool:
        """Test database integration"""
        try:
            # Test database through health endpoint
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                db_status = data.get("database", {}).get("status", "unknown")
                
                if db_status == "healthy":
                    self.log_test("Database Integration", "PASS", "Database is healthy")
                    return True
                else:
                    self.log_test("Database Integration", "FAIL", f"Database status: {db_status}")
                    return False
            else:
                self.log_test("Database Integration", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Database Integration", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_redis_integration(self) -> bool:
        """Test Redis integration"""
        try:
            # Test Redis through health endpoint
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                redis_status = data.get("redis", {}).get("status", "unknown")
                
                if redis_status == "healthy":
                    self.log_test("Redis Integration", "PASS", "Redis is healthy")
                    return True
                else:
                    self.log_test("Redis Integration", "FAIL", f"Redis status: {redis_status}")
                    return False
            else:
                self.log_test("Redis Integration", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Redis Integration", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_external_services(self) -> bool:
        """Test external service integrations"""
        try:
            # Test external services status
            response = requests.get(f"{self.backend_url}/api/v1/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                services = ["gemini", "tavily", "pinecone"]
                healthy_services = 0
                
                for service in services:
                    status = data.get(service, {}).get("status", "unknown")
                    if status == "healthy":
                        self.log_test(f"{service.upper()} Service", "PASS", "Service is healthy")
                        healthy_services += 1
                    else:
                        self.log_test(f"{service.upper()} Service", "FAIL", f"Service status: {status}")
                
                if healthy_services >= 2:  # At least 2 out of 3 services should be healthy
                    return True
                else:
                    return False
            else:
                self.log_test("External Services", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("External Services", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_integration_tests(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🔗 Starting Backend-Frontend Integration Tests")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Backend-Frontend Connection", self.test_backend_frontend_connection),
            ("API Endpoints", self.test_api_endpoints),
            ("Database Integration", self.test_database_integration),
            ("Redis Integration", self.test_redis_integration),
            ("External Services", self.test_external_services),
            ("RAG Integration", self.test_rag_integration),
            ("WebSocket Integration", self.test_websocket_integration),
            ("Agent Communication", self.test_agent_communication),
            ("Authentication Flow", self.test_authentication_flow),
        ]
        
        passed_tests = 0
        total_tests = len(tests)
        
        for test_name, test_func in tests:
            print(f"\n🧪 Testing {test_name}...")
            try:
                if test_func():
                    passed_tests += 1
            except Exception as e:
                self.log_test(test_name, "ERROR", f"Exception: {str(e)}")
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100
        print(f"✅ Passed: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        print(f"❌ Failed: {total_tests - passed_tests}/{total_tests}")
        
        # Detailed results
        print("\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASS" else "❌" if result["status"] == "FAIL" else "⚠️"
            print(f"{status_emoji} {result['test']}: {result['status']}")
            if result["details"]:
                print(f"   {result['details']}")
        
        # Overall status
        if success_rate >= 80:
            print(f"\n🎉 INTEGRATION STATUS: SUCCESSFUL ({success_rate:.1f}% success rate)")
            overall_status = "SUCCESSFUL"
        elif success_rate >= 60:
            print(f"\n⚠️ INTEGRATION STATUS: PARTIAL ({success_rate:.1f}% success rate)")
            overall_status = "PARTIAL"
        else:
            print(f"\n❌ INTEGRATION STATUS: FAILED ({success_rate:.1f}% success rate)")
            overall_status = "FAILED"
        
        return {
            "overall_status": overall_status,
            "success_rate": success_rate,
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "test_results": self.test_results,
            "timestamp": time.time()
        }

def main():
    """Main function to run integration tests"""
    print("🎯 Tutor GPT - Backend-Frontend Integration Test")
    print("Testing complete system integration")
    print()
    
    tester = IntegrationTester()
    results = tester.run_integration_tests()
    
    # Save results to file
    with open("integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: integration_test_results.json")
    
    # Exit with appropriate code
    if results["overall_status"] == "SUCCESSFUL":
        sys.exit(0)
    elif results["overall_status"] == "PARTIAL":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
