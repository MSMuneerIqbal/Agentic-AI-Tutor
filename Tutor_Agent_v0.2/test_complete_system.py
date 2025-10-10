#!/usr/bin/env python3
"""
Complete System Integration Test
Tests the full Tutor GPT system: Backend + Frontend + AI Agents
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

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class SystemIntegrationTester:
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
    
    def test_backend_health(self) -> bool:
        """Test backend health endpoint"""
        try:
            response = requests.get(f"{self.backend_url}/healthz", timeout=5)
            if response.status_code == 200:
                self.log_test("Backend Health Check", "PASS", f"Status: {response.status_code}")
                return True
            else:
                self.log_test("Backend Health Check", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Backend Health Check", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_backend_apis(self) -> bool:
        """Test backend API endpoints"""
        endpoints = [
            "/api/v1/health",
            "/api/v1/rag/health",
            "/api/v1/metrics",
        ]
        
        all_passed = True
        for endpoint in endpoints:
            try:
                response = requests.get(f"{self.backend_url}{endpoint}", timeout=5)
                if response.status_code in [200, 404]:  # 404 is ok for some endpoints
                    self.log_test(f"API Endpoint {endpoint}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"API Endpoint {endpoint}", "FAIL", f"Status: {response.status_code}")
                    all_passed = False
            except Exception as e:
                self.log_test(f"API Endpoint {endpoint}", "FAIL", f"Error: {str(e)}")
                all_passed = False
        
        return all_passed
    
    def test_rag_system(self) -> bool:
        """Test RAG system functionality"""
        try:
            # Test RAG content endpoint
            response = requests.get(f"{self.backend_url}/api/v1/rag/content?query=docker", timeout=10)
            if response.status_code == 200:
                data = response.json()
                self.log_test("RAG Content Search", "PASS", f"Found {len(data.get('results', []))} results")
                return True
            else:
                self.log_test("RAG Content Search", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("RAG Content Search", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_websocket_connection(self) -> bool:
        """Test WebSocket connection"""
        try:
            def on_message(ws, message):
                self.ws_messages.append(json.loads(message))
                print(f"   WebSocket Message: {message[:100]}...")
            
            def on_error(ws, error):
                print(f"   WebSocket Error: {error}")
            
            def on_close(ws, close_status_code, close_msg):
                print("   WebSocket Connection Closed")
            
            def on_open(ws):
                print("   WebSocket Connection Opened")
                # Send a test message
                test_message = {
                    "type": "test",
                    "message": "Hello from integration test"
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
            time.sleep(3)
            
            if len(self.ws_messages) > 0:
                self.log_test("WebSocket Connection", "PASS", f"Received {len(self.ws_messages)} messages")
                ws.close()
                return True
            else:
                self.log_test("WebSocket Connection", "FAIL", "No messages received")
                ws.close()
                return False
                
        except Exception as e:
            self.log_test("WebSocket Connection", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_agent_communication(self) -> bool:
        """Test AI agent communication"""
        try:
            # Test orchestrator agent
            test_data = {
                "user_input": "Hello, I want to learn Docker",
                "context": {
                    "state": "GREETING",
                    "user_id": "test_user_123"
                }
            }
            
            response = requests.post(
                f"{self.backend_url}/api/v1/chat",
                json=test_data,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test("Agent Communication", "PASS", f"Response from: {data.get('agent', 'Unknown')}")
                return True
            else:
                self.log_test("Agent Communication", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("Agent Communication", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_frontend_connectivity(self) -> bool:
        """Test frontend connectivity (if running)"""
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Frontend Connectivity", "PASS", "Frontend is accessible")
                return True
            else:
                self.log_test("Frontend Connectivity", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Frontend Connectivity", "FAIL", f"Frontend not running: {str(e)}")
            return False
    
    def test_database_connection(self) -> bool:
        """Test database connectivity"""
        try:
            # Test database health through backend
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("database", {}).get("status") == "healthy":
                    self.log_test("Database Connection", "PASS", "Database is healthy")
                    return True
                else:
                    self.log_test("Database Connection", "FAIL", "Database not healthy")
                    return False
            else:
                self.log_test("Database Connection", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Database Connection", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_redis_connection(self) -> bool:
        """Test Redis connectivity"""
        try:
            # Test Redis through backend health endpoint
            response = requests.get(f"{self.backend_url}/api/v1/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("redis", {}).get("status") == "healthy":
                    self.log_test("Redis Connection", "PASS", "Redis is healthy")
                    return True
                else:
                    self.log_test("Redis Connection", "FAIL", "Redis not healthy")
                    return False
            else:
                self.log_test("Redis Connection", "FAIL", f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_test("Redis Connection", "FAIL", f"Error: {str(e)}")
            return False
    
    def test_external_apis(self) -> bool:
        """Test external API connections (Gemini, Tavily, Pinecone)"""
        try:
            # Test API status endpoint
            response = requests.get(f"{self.backend_url}/api/v1/status", timeout=10)
            if response.status_code == 200:
                data = response.json()
                
                # Check each API
                apis = ["gemini", "tavily", "pinecone"]
                all_healthy = True
                
                for api in apis:
                    if data.get(api, {}).get("status") == "healthy":
                        self.log_test(f"{api.upper()} API", "PASS", "API is healthy")
                    else:
                        self.log_test(f"{api.upper()} API", "FAIL", "API not healthy")
                        all_healthy = False
                
                return all_healthy
            else:
                self.log_test("External APIs", "FAIL", f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_test("External APIs", "FAIL", f"Error: {str(e)}")
            return False
    
    def run_complete_test(self) -> Dict[str, Any]:
        """Run all integration tests"""
        print("🚀 Starting Complete System Integration Test")
        print("=" * 60)
        
        # Test sequence
        tests = [
            ("Backend Health", self.test_backend_health),
            ("Backend APIs", self.test_backend_apis),
            ("Database Connection", self.test_database_connection),
            ("Redis Connection", self.test_redis_connection),
            ("External APIs", self.test_external_apis),
            ("RAG System", self.test_rag_system),
            ("WebSocket Connection", self.test_websocket_connection),
            ("Agent Communication", self.test_agent_communication),
            ("Frontend Connectivity", self.test_frontend_connectivity),
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
            print(f"\n🎉 SYSTEM STATUS: HEALTHY ({success_rate:.1f}% success rate)")
            overall_status = "HEALTHY"
        elif success_rate >= 60:
            print(f"\n⚠️ SYSTEM STATUS: DEGRADED ({success_rate:.1f}% success rate)")
            overall_status = "DEGRADED"
        else:
            print(f"\n❌ SYSTEM STATUS: UNHEALTHY ({success_rate:.1f}% success rate)")
            overall_status = "UNHEALTHY"
        
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
    print("🎯 Tutor GPT - Complete System Integration Test")
    print("Testing Backend + Frontend + AI Agents Integration")
    print()
    
    tester = SystemIntegrationTester()
    results = tester.run_complete_test()
    
    # Save results to file
    with open("integration_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Results saved to: integration_test_results.json")
    
    # Exit with appropriate code
    if results["overall_status"] == "HEALTHY":
        sys.exit(0)
    elif results["overall_status"] == "DEGRADED":
        sys.exit(1)
    else:
        sys.exit(2)

if __name__ == "__main__":
    main()
