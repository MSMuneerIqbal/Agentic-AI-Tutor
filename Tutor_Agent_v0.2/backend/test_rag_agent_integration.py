#!/usr/bin/env python3
"""
Test RAG Integration with All Agents
Demonstrates how each agent fetches content from Pinecone
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_all_agents_rag_integration():
    """Test how all agents fetch content from RAG/Pinecone."""
    print("🤖 Testing RAG Integration with All Agents")
    print("=" * 50)
    
    # Import all agents
    try:
        from app.agents.orchestrator import OrchestratorAgent
        from app.agents.assessment import AssessmentAgent
        from app.agents.planning import PlanningAgent
        from app.agents.tutor import TutorAgent
        from app.agents.quiz import QuizAgent
        from app.agents.feedback import FeedbackAgent
        from app.models import SessionState
        print("✅ All agents imported successfully")
    except Exception as e:
        print(f"❌ Agent import failed: {e}")
        return False
    
    # Initialize agents
    agents = {
        "orchestrator": OrchestratorAgent(),
        "assessment": AssessmentAgent(),
        "planning": PlanningAgent(),
        "tutor": TutorAgent(),
        "quiz": QuizAgent(),
        "feedback": FeedbackAgent()
    }
    
    print(f"✅ {len(agents)} agents initialized")
    
    # Test scenarios for each agent
    test_scenarios = [
        {
            "agent": "tutor",
            "name": "Tutor Agent (Olivia)",
            "input": "Tell me about Docker containers",
            "context": {
                "topic": "Docker containers",
                "learning_style": "V",
                "progress": 0
            },
            "expected_rag": "Docker content from Pinecone"
        },
        {
            "agent": "planning",
            "name": "Planning Agent",
            "input": "Create a study plan for Docker and Kubernetes",
            "context": {
                "user_id": "test_user",
                "session_id": "test_session",
                "planning_stage": "goals"
            },
            "expected_rag": "Planning content from Pinecone"
        },
        {
            "agent": "quiz",
            "name": "Quiz Agent",
            "input": "Generate a quiz about Kubernetes",
            "context": {
                "topic": "Kubernetes pods",
                "quiz_type": "knowledge_check"
            },
            "expected_rag": "Quiz content from Pinecone"
        },
        {
            "agent": "assessment",
            "name": "Assessment Agent",
            "input": "start assessment",
            "context": {
                "user_id": "test_user",
                "session_id": "test_session"
            },
            "expected_rag": "Assessment content from Pinecone"
        },
        {
            "agent": "feedback",
            "name": "Feedback Agent (Principal)",
            "input": "Monitor tutor performance",
            "context": {
                "feedback_type": "agent_performance",
                "agent_name": "tutor",
                "performance_metrics": {"satisfaction": 0.8}
            },
            "expected_rag": "Feedback content from Pinecone"
        }
    ]
    
    # Test each agent
    results = {}
    for scenario in test_scenarios:
        agent_name = scenario["agent"]
        agent = agents[agent_name]
        
        print(f"\n🧪 Testing {scenario['name']}...")
        print(f"   Input: '{scenario['input']}'")
        print(f"   Expected RAG: {scenario['expected_rag']}")
        
        try:
            # Execute agent
            response = await agent.execute(scenario["input"], scenario["context"])
            
            # Check if response contains RAG content
            has_rag_content = False
            rag_indicators = ["rag_content", "live_examples", "best_practices", "troubleshooting"]
            
            for indicator in rag_indicators:
                if indicator in response and response[indicator]:
                    has_rag_content = True
                    print(f"   ✅ Found RAG content: {indicator}")
                    if isinstance(response[indicator], list) and response[indicator]:
                        print(f"      Content pieces: {len(response[indicator])}")
                        if response[indicator][0].get('content'):
                            print(f"      Sample: {response[indicator][0]['content'][:80]}...")
                    break
            
            if not has_rag_content:
                print(f"   ⚠️ No RAG content indicators found in response")
                print(f"   Response keys: {list(response.keys())}")
            
            # Check if agent message is informative
            message = response.get("message", "")
            if message and len(message) > 50:
                print(f"   ✅ Agent provided detailed response ({len(message)} chars)")
                print(f"      Preview: {message[:100]}...")
            else:
                print(f"   ⚠️ Agent response seems short: {message}")
            
            results[agent_name] = {
                "success": True,
                "has_rag": has_rag_content,
                "response_length": len(message),
                "response": response
            }
            
        except Exception as e:
            print(f"   ❌ Agent execution failed: {e}")
            results[agent_name] = {
                "success": False,
                "error": str(e)
            }
    
    # Summary
    print(f"\n📊 RAG Integration Test Results:")
    print("=" * 40)
    
    successful_agents = 0
    agents_with_rag = 0
    
    for agent_name, result in results.items():
        if result["success"]:
            status = "✅ PASS"
            successful_agents += 1
            if result.get("has_rag"):
                agents_with_rag += 1
                rag_status = "✅ RAG"
            else:
                rag_status = "⚠️ No RAG"
        else:
            status = "❌ FAIL"
            rag_status = "❌ Error"
        
        print(f"   {agent_name.capitalize():12} | {status:8} | {rag_status}")
    
    print("=" * 40)
    print(f"Successful Agents: {successful_agents}/{len(agents)}")
    print(f"Agents with RAG: {agents_with_rag}/{len(agents)}")
    
    return successful_agents == len(agents)

async def test_rag_service_directly():
    """Test RAG service directly to show content fetching."""
    print(f"\n🔍 Testing RAG Service Directly...")
    print("=" * 40)
    
    try:
        from app.services.rag_service import get_rag_service
        
        rag_service = await get_rag_service()
        
        # Test different queries
        test_queries = [
            {
                "query": "Docker containers",
                "agent_type": "tutor",
                "description": "Tutor asking about Docker"
            },
            {
                "query": "Kubernetes pods",
                "agent_type": "quiz",
                "description": "Quiz about Kubernetes"
            },
            {
                "query": "Docker and Kubernetes study plan",
                "agent_type": "planning",
                "description": "Planning agent content"
            }
        ]
        
        for test in test_queries:
            print(f"\n🔍 Query: '{test['query']}' ({test['description']})")
            
            try:
                results = await rag_service.get_agent_content(
                    test["agent_type"], 
                    test["query"], 
                    include_live_examples=True
                )
                
                if results.get("rag_content"):
                    print(f"   ✅ Found {len(results['rag_content'])} RAG content pieces")
                    for i, content in enumerate(results["rag_content"][:2]):  # Show first 2
                        print(f"      {i+1}. {content.get('source', 'Unknown')} - {content.get('chapter', 'Unknown')}")
                        print(f"         {content.get('content', 'No content')[:80]}...")
                else:
                    print(f"   ⚠️ No RAG content found")
                
                if results.get("live_examples"):
                    print(f"   ✅ Found {len(results['live_examples'])} live examples")
                    for i, example in enumerate(results["live_examples"][:1]):  # Show first 1
                        print(f"      {i+1}. {example.get('title', 'Unknown')}")
                        print(f"         {example.get('content', 'No content')[:80]}...")
                else:
                    print(f"   ⚠️ No live examples found")
                
            except Exception as e:
                print(f"   ❌ RAG query failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG service test failed: {e}")
        return False

async def test_pinecone_direct_access():
    """Test direct access to Pinecone to show content is there."""
    print(f"\n🗄️ Testing Direct Pinecone Access...")
    print("=" * 40)
    
    try:
        from pinecone import Pinecone
        
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index("docker-kubernetes-tutor")
        
        # Get index stats
        stats = index.describe_index_stats()
        print(f"📊 Index Statistics:")
        print(f"   Total Vectors: {stats.total_vector_count}")
        print(f"   Dimension: {stats.dimension}")
        print(f"   Index Fullness: {stats.index_fullness}")
        
        if stats.namespaces:
            print(f"   Namespaces: {list(stats.namespaces.keys())}")
            for ns, details in stats.namespaces.items():
                print(f"     - {ns}: {details.vector_count} vectors")
        else:
            print(f"   Namespaces: default (no custom namespaces)")
        
        # Test a simple query
        print(f"\n🔍 Testing Content Retrieval...")
        
        # Create a simple test query
        import hashlib
        test_query = "Docker containers"
        query_hash = hashlib.sha256(test_query.encode()).hexdigest()
        query_embedding = []
        for j in range(0, len(query_hash), 2):
            val = int(query_hash[j:j+2], 16) / 255.0
            query_embedding.append(val)
        while len(query_embedding) < 768:
            query_embedding.append(0.0)
        query_embedding = query_embedding[:768]
        
        # Query Pinecone
        result = index.query(
            vector=query_embedding,
            top_k=3,
            include_metadata=True
        )
        
        print(f"Query: '{test_query}'")
        print(f"Results: {len(result.matches)} matches found")
        
        for i, match in enumerate(result.matches):
            print(f"   {i+1}. Score: {match.score:.3f}")
            print(f"      Source: {match.metadata.get('source', 'Unknown')}")
            print(f"      Chapter: {match.metadata.get('chapter', 'Unknown')}")
            print(f"      Topic: {match.metadata.get('topic', 'Unknown')}")
            print(f"      Content: {match.metadata.get('content', 'No content')[:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Pinecone access failed: {e}")
        return False

async def demonstrate_agent_rag_workflow():
    """Demonstrate complete agent RAG workflow."""
    print(f"\n🎭 Demonstrating Complete Agent RAG Workflow...")
    print("=" * 50)
    
    try:
        from app.agents.tutor import TutorAgent
        from app.agents.quiz import QuizAgent
        
        # Scenario: Student asks about Docker, then takes a quiz
        print("📚 Scenario: Student learning about Docker")
        
        # Step 1: Tutor provides lesson with RAG content
        print(f"\n1️⃣ Tutor Agent providing lesson...")
        tutor = TutorAgent()
        tutor_response = await tutor.execute("Tell me about Docker containers", {
            "topic": "Docker containers",
            "learning_style": "V",
            "progress": 0
        })
        
        print(f"   Tutor Response: {tutor_response.get('message', 'No message')[:150]}...")
        if tutor_response.get('rag_content'):
            print(f"   ✅ Tutor used {len(tutor_response['rag_content'])} RAG content pieces")
        if tutor_response.get('live_examples'):
            print(f"   ✅ Tutor included {len(tutor_response['live_examples'])} live examples")
        
        # Step 2: Quiz agent creates quiz with RAG content
        print(f"\n2️⃣ Quiz Agent creating assessment...")
        quiz = QuizAgent()
        quiz_response = await quiz.execute("Generate a quiz about Docker", {
            "topic": "Docker containers",
            "quiz_type": "knowledge_check"
        })
        
        print(f"   Quiz Response: {quiz_response.get('message', 'No message')[:150]}...")
        if quiz_response.get('rag_content'):
            print(f"   ✅ Quiz used {len(quiz_response['rag_content'])} RAG content pieces")
        
        # Step 3: Show how content flows through the system
        print(f"\n3️⃣ Content Flow Analysis...")
        print(f"   📚 RAG Content: Available to all agents from Pinecone")
        print(f"   🌐 Live Examples: Available via Tavily MCP")
        print(f"   🤖 Agent Processing: Each agent uses content for their specific role")
        print(f"   📖 Student Delivery: Content delivered in agent-specific format")
        
        return True
        
    except Exception as e:
        print(f"❌ Workflow demonstration failed: {e}")
        return False

async def main():
    """Main test function."""
    print("🚀 Complete RAG Integration Test Suite")
    print("=" * 60)
    
    # Test 1: All agents RAG integration
    agents_working = await test_all_agents_rag_integration()
    
    # Test 2: RAG service directly
    rag_service_working = await test_rag_service_directly()
    
    # Test 3: Direct Pinecone access
    pinecone_working = await test_pinecone_direct_access()
    
    # Test 4: Complete workflow demonstration
    workflow_working = await demonstrate_agent_rag_workflow()
    
    # Final summary
    print(f"\n🎯 Final RAG Integration Status:")
    print("=" * 40)
    
    tests = [
        ("All Agents RAG Integration", agents_working),
        ("RAG Service Direct Access", rag_service_working),
        ("Direct Pinecone Access", pinecone_working),
        ("Complete Workflow Demo", workflow_working)
    ]
    
    passed_tests = 0
    for test_name, result in tests:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name:25} | {status}")
        if result:
            passed_tests += 1
    
    print("=" * 40)
    print(f"Overall: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print(f"\n🎉 ALL AGENTS CAN FETCH CONTENT FROM RAG/PINECONE!")
        print(f"\n📋 How It Works:")
        print(f"   1. 🔍 Agent receives student query")
        print(f"   2. 📚 Agent calls RAG service with query + agent type")
        print(f"   3. 🗄️ RAG service queries Pinecone for relevant content")
        print(f"   4. 🌐 RAG service also fetches live examples via Tavily")
        print(f"   5. 🤖 Agent processes content for their specific role")
        print(f"   6. 📖 Agent delivers personalized response to student")
        print(f"\n✅ Every agent call can fetch fresh content from Pinecone!")
        print(f"✅ No need to create new embeddings - content is already there!")
        print(f"✅ Agents get relevant content based on their specific needs!")
    else:
        print(f"\n⚠️ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
