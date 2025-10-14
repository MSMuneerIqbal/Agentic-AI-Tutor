#!/usr/bin/env python3
"""
Test all 6 agents directly: Orchestrator, Assessment, Tutor, Quiz, Feedback, Planning
Run this to test each agent's prompts and responses.
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.agents.orchestrator import OrchestratorAgent
from app.agents.assessment import AssessmentAgent
from app.agents.tutor import TutorAgent
from app.agents.quiz import QuizAgent
from app.agents.feedback import FeedbackAgent
from app.agents.planning import PlanningAgent

async def test_agent(agent, agent_name, test_inputs):
    """Test a single agent with multiple inputs."""
    print(f"\n🤖 TESTING {agent_name.upper()} AGENT")
    print("=" * 50)
    
    for i, input_text in enumerate(test_inputs, 1):
        print(f"\n{i}. Input: '{input_text}'")
        
        try:
            # Create context for agent
            context = {
                "state": "testing",
                "user_profile": {"name": "Test User", "email": "test@example.com"},
                "topic": "Docker",
                "learning_style": "visual",
                "progress": {"topics_completed": [], "quiz_scores": [], "time_spent": 0},
                "session_id": "test-session",
                "user_id": "test-user"
            }
            
            # Execute agent
            response = await agent._execute(input_text, context)
            
            # Display response
            if isinstance(response, dict):
                message = response.get("message", response.get("response", "No message"))
                action = response.get("action", "No action")
                next_state = response.get("next_state", "No state change")
                
                print(f"   ✅ Response: {message[:100]}{'...' if len(message) > 100 else ''}")
                print(f"   📋 Action: {action}")
                print(f"   🔄 Next State: {next_state}")
            else:
                print(f"   ✅ Response: {str(response)[:100]}{'...' if len(str(response)) > 100 else ''}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
    
    print(f"\n✅ {agent_name} Agent testing complete!")

async def main():
    """Test all 6 agents."""
    print("🤖 TESTING ALL 6 AGENTS DIRECTLY")
    print("=" * 60)
    
    # Initialize all agents
    agents = {
        "Orchestrator": OrchestratorAgent(),
        "Assessment": AssessmentAgent(), 
        "Tutor": TutorAgent(),
        "Quiz": QuizAgent(),
        "Feedback": FeedbackAgent(),
        "Planning": PlanningAgent()
    }
    
    # Test inputs for each agent
    test_inputs = {
        "Orchestrator": [
            "Hello, I'm new here",
            "I want to start learning",
            "What should I do next?",
            "Help me understand my options"
        ],
        "Assessment": [
            "I want to take an assessment",
            "What's my learning style?",
            "Tell me about VARK assessment",
            "I prefer visual learning"
        ],
        "Tutor": [
            "Explain Docker containers",
            "How does Kubernetes work?",
            "What is containerization?",
            "Show me Docker commands"
        ],
        "Quiz": [
            "Give me a quiz on Docker",
            "Test my knowledge",
            "Create a practice question",
            "Quiz me on containers"
        ],
        "Feedback": [
            "How am I doing?",
            "Show my progress",
            "What should I improve?",
            "Give me feedback"
        ],
        "Planning": [
            "Create a study plan",
            "Plan my learning path",
            "What should I learn next?",
            "Schedule my studies"
        ]
    }
    
    # Test each agent
    for agent_name, agent in agents.items():
        await test_agent(agent, agent_name, test_inputs[agent_name])
        await asyncio.sleep(1)  # Small delay between agents
    
    print("\n🎯 ALL AGENTS TESTED!")
    print("=" * 60)
    print("✅ If you see responses above, your agents are working!")
    print("❌ If you see errors, those agents need fixing.")

if __name__ == "__main__":
    print("Starting 6-agent test...")
    asyncio.run(main())
