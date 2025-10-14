#!/usr/bin/env python3
"""
Comprehensive Testing of All 6 Agents According to Plan & Specs
Tests the complete agent flow from greeting to completion
"""

import requests
import json
import asyncio
import websockets
from datetime import datetime
import time

class AgentFlowTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "errors": [],
            "agent_status": {}
        }
        self.test_user_email = "test_agent_flow@example.com"
        self.session_id = None
    
    def log_test(self, test_name, success, error=None, agent=None):
        """Log test result"""
        self.results["total_tests"] += 1
        if success:
            self.results["passed"] += 1
            print(f"✅ {test_name}")
            if agent:
                self.results["agent_status"][agent] = "WORKING"
        else:
            self.results["failed"] += 1
            self.results["errors"].append(f"{test_name}: {error}")
            print(f"❌ {test_name}: {error}")
            if agent:
                self.results["agent_status"][agent] = "FAILED"
    
    def test_endpoint(self, method, endpoint, data=None, expected_status=200):
        """Test a single endpoint"""
        url = f"{self.base_url}{endpoint}"
        try:
            if method.upper() == "GET":
                response = self.session.get(url, timeout=5)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=5)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            if response.status_code == expected_status:
                return True, response.json() if response.content else {}
            else:
                return False, f"Expected {expected_status}, got {response.status_code}: {response.text[:200]}"
        except Exception as e:
            return False, str(e)
    
    def setup_test_environment(self):
        """Setup test user and session"""
        print("\n🔧 Setting Up Test Environment")
        print("=" * 50)
        
        # Create test user
        register_data = {
            "name": "Agent Test User",
            "email": self.test_user_email,
            "password": "testpassword123"
        }
        success, result = self.test_endpoint("POST", "/api/v1/auth/register", register_data)
        self.log_test("Create test user", success, result if not success else None)
        
        # Create test session
        session_data = {
            "user_email": self.test_user_email
        }
        success, result = self.test_endpoint("POST", "/api/v1/sessions/start", session_data)
        if success and "session_id" in result:
            self.session_id = result["session_id"]
            print(f"   📝 Session ID: {self.session_id}")
        self.log_test("Create test session", success, result if not success else None)
        
        return self.session_id is not None
    
    async def test_agent_flow_via_websocket(self):
        """Test complete agent flow via WebSocket"""
        if not self.session_id:
            print("❌ No session ID available for WebSocket testing")
            return
        
        print("\n🤖 Testing Complete Agent Flow via WebSocket")
        print("=" * 50)
        
        try:
            ws_url = f"ws://localhost:8000/ws/sessions/{self.session_id}"
            async with websockets.connect(ws_url) as websocket:
                
                # Test 1: Orchestrator Agent - Initial Greeting
                print("\n1️⃣ Testing Orchestrator Agent - Initial Greeting")
                initial_message = await websocket.recv()
                initial_data = json.loads(initial_message)
                
                if "text" in initial_data and "Hello" in initial_data["text"]:
                    self.log_test("Orchestrator Agent - Initial Greeting", True, agent="Orchestrator")
                    print(f"   📨 Greeting: {initial_data['text'][:100]}...")
                else:
                    self.log_test("Orchestrator Agent - Initial Greeting", False, "No greeting received", "Orchestrator")
                
                # Test 2: Assessment Agent - Learning Style Assessment
                print("\n2️⃣ Testing Assessment Agent - Learning Style Assessment")
                
                # Send user response to start assessment
                assessment_message = {
                    "message": "yes",
                    "type": "user_message",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(assessment_message))
                
                # Wait for assessment question
                assessment_response = await websocket.recv()
                assessment_data = json.loads(assessment_response)
                
                if "text" in assessment_data and ("question" in assessment_data["text"].lower() or "choose" in assessment_data["text"].lower()):
                    self.log_test("Assessment Agent - Question Generation", True, agent="Assessment")
                    print(f"   📨 Assessment Question: {assessment_data['text'][:100]}...")
                else:
                    self.log_test("Assessment Agent - Question Generation", False, "No assessment question received", "Assessment")
                
                # Test assessment flow with sample answers
                for i in range(3):  # Test first 3 questions
                    # Send answer
                    answer_message = {
                        "message": "a",  # Simple answer
                        "type": "user_message", 
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    await websocket.send(json.dumps(answer_message))
                    
                    # Wait for next question or completion
                    response = await websocket.recv()
                    response_data = json.loads(response)
                    
                    if "text" in response_data:
                        if "question" in response_data["text"].lower():
                            print(f"   📝 Question {i+2}: {response_data['text'][:80]}...")
                        elif "thank you" in response_data["text"].lower() or "learning style" in response_data["text"].lower():
                            self.log_test("Assessment Agent - Assessment Completion", True, agent="Assessment")
                            print(f"   ✅ Assessment Complete: {response_data['text'][:100]}...")
                            break
                
                # Test 3: Planning Agent - Study Plan Creation
                print("\n3️⃣ Testing Planning Agent - Study Plan Creation")
                
                plan_request = {
                    "message": "create my study plan",
                    "type": "user_message",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(plan_request))
                
                plan_response = await websocket.recv()
                plan_data = json.loads(plan_response)
                
                if "text" in plan_data and ("plan" in plan_data["text"].lower() or "study" in plan_data["text"].lower()):
                    self.log_test("Planning Agent - Plan Creation", True, agent="Planning")
                    print(f"   📨 Study Plan: {plan_data['text'][:100]}...")
                else:
                    self.log_test("Planning Agent - Plan Creation", False, "No study plan created", "Planning")
                
                # Test 4: Tutor Agent - Lesson Delivery
                print("\n4️⃣ Testing Tutor Agent - Lesson Delivery")
                
                lesson_request = {
                    "message": "teach me about Docker containers",
                    "type": "user_message",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(lesson_request))
                
                lesson_response = await websocket.recv()
                lesson_data = json.loads(lesson_response)
                
                if "text" in lesson_data and ("docker" in lesson_data["text"].lower() or "container" in lesson_data["text"].lower() or "explain" in lesson_data["text"].lower()):
                    self.log_test("Tutor Agent - Lesson Delivery", True, agent="Tutor")
                    print(f"   📨 Lesson: {lesson_data['text'][:100]}...")
                else:
                    self.log_test("Tutor Agent - Lesson Delivery", False, "No lesson delivered", "Tutor")
                
                # Test 5: Quiz Agent - Quiz Generation
                print("\n5️⃣ Testing Quiz Agent - Quiz Generation")
                
                quiz_request = {
                    "message": "give me a quiz about Docker",
                    "type": "user_message",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(quiz_request))
                
                quiz_response = await websocket.recv()
                quiz_data = json.loads(quiz_response)
                
                if "text" in quiz_data and ("quiz" in quiz_data["text"].lower() or "question" in quiz_data["text"].lower() or "?" in quiz_data["text"]):
                    self.log_test("Quiz Agent - Quiz Generation", True, agent="Quiz")
                    print(f"   📨 Quiz: {quiz_data['text'][:100]}...")
                else:
                    self.log_test("Quiz Agent - Quiz Generation", False, "No quiz generated", "Quiz")
                
                # Test 6: Feedback Agent - Progress Feedback
                print("\n6️⃣ Testing Feedback Agent - Progress Feedback")
                
                feedback_request = {
                    "message": "how am I doing?",
                    "type": "user_message",
                    "timestamp": datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(feedback_request))
                
                feedback_response = await websocket.recv()
                feedback_data = json.loads(feedback_response)
                
                if "text" in feedback_data and ("progress" in feedback_data["text"].lower() or "doing" in feedback_data["text"].lower() or "feedback" in feedback_data["text"].lower()):
                    self.log_test("Feedback Agent - Progress Feedback", True, agent="Feedback")
                    print(f"   📨 Feedback: {feedback_data['text'][:100]}...")
                else:
                    self.log_test("Feedback Agent - Progress Feedback", False, "No feedback provided", "Feedback")
                
        except Exception as e:
            self.log_test("WebSocket Agent Flow Test", False, str(e))
    
    def test_agent_endpoints(self):
        """Test agent-related endpoints"""
        print("\n🔗 Testing Agent-Related Endpoints")
        print("=" * 50)
        
        # Test RAG endpoints (used by agents)
        content_data = {
            "query": "Docker container basics",
            "agent_type": "tutor"
        }
        success, result = self.test_endpoint("POST", "/api/v1/rag/content", content_data)
        self.log_test("RAG Content for Tutor Agent", success, result if not success else None)
        
        # Test lesson generation
        lesson_data = {
            "topic": "Docker containers",
            "learning_style": "visual"
        }
        success, result = self.test_endpoint("POST", "/api/v1/rag/lesson", lesson_data)
        self.log_test("RAG Lesson Generation", success, result if not success else None)
        
        # Test assessment history
        success, result = self.test_endpoint("GET", f"/api/v1/assessments/{self.test_user_email}/history")
        self.log_test("Assessment History Retrieval", success, result if not success else None)
        
        # Test study plan creation
        plan_data = {
            "topics": ["Docker Basics", "Kubernetes Fundamentals"],
            "learning_style": "visual",
            "estimated_hours": 10
        }
        success, result = self.test_endpoint("POST", f"/api/v1/plans/{self.test_user_email}", plan_data)
        self.log_test("Study Plan Creation", success, result if not success else None)
    
    def run_comprehensive_agent_test(self):
        """Run comprehensive agent testing"""
        print("🤖 COMPREHENSIVE AGENT TESTING")
        print("=" * 60)
        print(f"🔗 Base URL: {self.base_url}")
        print(f"📧 Test User: {self.test_user_email}")
        print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Setup test environment
        if not self.setup_test_environment():
            print("❌ Cannot proceed without test environment")
            return
        
        # Test agent endpoints
        self.test_agent_endpoints()
        
        # Test complete agent flow via WebSocket
        print("\n🔌 Testing Agent Flow via WebSocket...")
        asyncio.run(self.test_agent_flow_via_websocket())
        
        # Print final results
        self.print_agent_summary()
    
    def print_agent_summary(self):
        """Print agent testing summary"""
        print("\n" + "=" * 60)
        print("🤖 AGENT TESTING SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"📊 Total: {self.results['total_tests']}")
        
        if self.results['total_tests'] > 0:
            success_rate = (self.results['passed'] / self.results['total_tests'] * 100)
            print(f"📈 Success Rate: {success_rate:.1f}%")
        
        print(f"\n🤖 Agent Status:")
        for agent, status in self.results['agent_status'].items():
            emoji = "✅" if status == "WORKING" else "❌"
            print(f"   {emoji} {agent}: {status}")
        
        if self.results['errors']:
            print(f"\n❌ Detailed Errors:")
            for error in self.results['errors']:
                print(f"   • {error}")
        
        print(f"\n⏰ Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)

if __name__ == "__main__":
    tester = AgentFlowTester()
    tester.run_comprehensive_agent_test()
