#!/usr/bin/env python3
"""
Test all 6 agents: Orchestrator, Assessment, Tutor, Quiz, Feedback, Planning
Run this to verify the complete agent flow works end-to-end.
"""

import asyncio
import json
import requests
import websockets
from datetime import datetime

async def test_complete_agent_flow():
    """Test the complete agent flow from signup to tutoring."""
    
    print("🤖 TESTING ALL 6 AGENTS - COMPLETE FLOW")
    print("=" * 50)
    
    # Step 1: Create session
    print("\n1️⃣ Creating session...")
    session_response = requests.post(
        "http://localhost:8000/api/v1/sessions/start",
        json={"user_email": "test_agent_flow@example.com"}
    )
    
    if session_response.status_code != 200:
        print(f"❌ Session creation failed: {session_response.text}")
        return
    
    session_id = session_response.json()["session_id"]
    print(f"✅ Session created: {session_id}")
    
    # Step 2: Test WebSocket connection and agent flow
    print("\n2️⃣ Testing WebSocket agent communication...")
    
    try:
        async with websockets.connect(f"ws://localhost:8000/ws/sessions/{session_id}") as websocket:
            print("✅ WebSocket connected")
            
            # Test different agent interactions
            test_messages = [
                "hello",  # Should trigger Orchestrator
                "I want to take an assessment",  # Should trigger Assessment
                "explain Docker containers",  # Should trigger Tutor
                "give me a quiz",  # Should trigger Quiz
                "how am I doing?",  # Should trigger Feedback
                "create a study plan",  # Should trigger Planning
            ]
            
            agent_names = ["Orchestrator", "Assessment", "Tutor", "Quiz", "Feedback", "Planning"]
            
            for i, message in enumerate(test_messages):
                print(f"\n🔹 Testing {agent_names[i]} Agent:")
                print(f"   Sending: '{message}'")
                
                # Send message
                await websocket.send(json.dumps({
                    "message": message,
                    "type": "user_message",
                    "timestamp": datetime.utcnow().isoformat()
                }))
                
                # Receive response
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    
                    if data.get("type") == "agent_message":
                        agent_type = data.get("agent", "unknown")
                        response_text = data.get("text", "")[:100] + "..." if len(data.get("text", "")) > 100 else data.get("text", "")
                        print(f"   ✅ {agent_type} Agent responded: {response_text}")
                    else:
                        print(f"   ⚠️  Unexpected response type: {data.get('type')}")
                        
                except asyncio.TimeoutError:
                    print(f"   ❌ Timeout waiting for {agent_names[i]} response")
                except Exception as e:
                    print(f"   ❌ Error: {e}")
                
                # Small delay between tests
                await asyncio.sleep(1)
                
    except Exception as e:
        print(f"❌ WebSocket connection failed: {e}")
        return
    
    # Step 3: Test RAG endpoints
    print("\n3️⃣ Testing RAG Agent endpoints...")
    
    rag_tests = [
        {
            "endpoint": "/api/v1/rag/content",
            "data": {"query": "Docker basics", "agent_type": "tutor"},
            "name": "Content Generation"
        },
        {
            "endpoint": "/api/v1/rag/lesson", 
            "data": {"topic": "Kubernetes", "learning_style": "visual"},
            "name": "Lesson Generation"
        },
        {
            "endpoint": "/api/v1/rag/topic",
            "data": {"topic": "Container orchestration", "depth": "intermediate"},
            "name": "Topic Research"
        }
    ]
    
    for test in rag_tests:
        try:
            response = requests.post(f"http://localhost:8000{test['endpoint']}", json=test["data"])
            if response.status_code == 200:
                data = response.json()
                content_count = len(data.get("rag_content", []))
                print(f"   ✅ {test['name']}: {content_count} results")
            else:
                print(f"   ❌ {test['name']}: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"   ❌ {test['name']}: {e}")
    
    # Step 4: Test other endpoints
    print("\n4️⃣ Testing other agent endpoints...")
    
    # Test session retrieval
    try:
        session_data = requests.get(f"http://localhost:8000/api/v1/sessions/{session_id}")
        if session_data.status_code == 200:
            print("   ✅ Session retrieval working")
        else:
            print(f"   ❌ Session retrieval failed: {session_data.status_code}")
    except Exception as e:
        print(f"   ❌ Session retrieval error: {e}")
    
    # Test authentication
    try:
        auth_response = requests.post(
            "http://localhost:8000/api/v1/auth/register",
            json={"name": "Agent Tester", "email": "agent@test.com", "password": "test123"}
        )
        if auth_response.status_code == 200:
            print("   ✅ Authentication working")
        else:
            print(f"   ❌ Authentication failed: {auth_response.status_code}")
    except Exception as e:
        print(f"   ❌ Authentication error: {e}")
    
    print("\n🎯 AGENT FLOW TEST COMPLETE!")
    print("=" * 50)
    print("If you see ✅ marks above, your agents are working!")
    print("If you see ❌ marks, those agents need fixing.")

if __name__ == "__main__":
    print("Starting agent flow test...")
    asyncio.run(test_complete_agent_flow())
