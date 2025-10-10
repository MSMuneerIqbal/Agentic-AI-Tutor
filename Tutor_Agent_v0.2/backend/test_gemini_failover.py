#!/usr/bin/env python3
"""
Test script for Gemini API Manager with Multiple API Keys and Failover
"""

import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.gemini_manager import get_gemini_manager

async def test_gemini_failover():
    """Test the Gemini API manager with failover functionality."""
    print("🚀 Testing Gemini API Manager with Multiple API Keys and Failover")
    print("=" * 70)
    
    # Get the Gemini manager
    manager = get_gemini_manager()
    
    # Show current configuration
    print("\n📊 Current Configuration:")
    config = manager.get_current_config()
    print(f"   Current API Key: {config['api_key'][:20]}...")
    print(f"   Current Model: {config['model']}")
    print(f"   Total API Keys: {len(manager.api_keys)}")
    print(f"   Available Keys: {len(manager.get_available_keys())}")
    
    # Test content generation
    print("\n🧠 Testing Content Generation:")
    test_prompts = [
        "What is Docker?",
        "Explain Kubernetes pods in simple terms",
        "How do you create a Docker container?"
    ]
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n   Test {i}: {prompt}")
        try:
            response = await manager.generate_content_with_failover(prompt)
            if response:
                print(f"   ✅ Success: {response[:100]}...")
            else:
                print("   ❌ Failed to generate content")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Test embedding generation
    print("\n🔗 Testing Embedding Generation:")
    test_texts = [
        "Docker is a containerization platform",
        "Kubernetes is an orchestration system",
        "Microservices architecture patterns"
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n   Test {i}: {text}")
        try:
            embedding = await manager.generate_embedding_with_failover(text)
            if embedding:
                print(f"   ✅ Success: Generated {len(embedding)}-dimensional embedding")
            else:
                print("   ❌ Failed to generate embedding")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show usage report
    print("\n📈 Usage Report:")
    report = manager.get_usage_report()
    print(f"   Current Key Index: {report['current_key_index']}")
    print(f"   Current Model Index: {report['current_model_index']}")
    print(f"   Available Keys: {report['available_keys']}/{report['total_keys']}")
    print(f"   Failed Keys: {report['failed_keys']}")
    
    print("\n   Key Statistics:")
    for key_short, stats in report['key_stats'].items():
        status = "❌ FAILED" if stats['is_failed'] else "✅ ACTIVE"
        print(f"   {key_short}: {status}")
        print(f"      Requests: {stats['requests']}, Tokens: {stats['tokens']}, Errors: {stats['errors']}")
        if stats['quota_exceeded']:
            print(f"      ⚠️  QUOTA EXCEEDED")
    
    print("\n🎉 Gemini API Manager Test Complete!")
    return True

async def test_rag_integration():
    """Test RAG integration with the new Gemini manager."""
    print("\n🔍 Testing RAG Integration with Gemini Manager")
    print("=" * 50)
    
    try:
        from app.tools.rag import RAGTool
        
        rag_tool = RAGTool()
        
        # Test embedding generation
        test_text = "Docker containers and Kubernetes orchestration"
        print(f"\n   Testing embedding for: {test_text}")
        
        embedding = await rag_tool.generate_embedding(test_text)
        if embedding:
            print(f"   ✅ Success: Generated {len(embedding)}-dimensional embedding")
        else:
            print("   ❌ Failed to generate embedding")
        
        # Test content query
        print(f"\n   Testing content query for: Docker basics")
        results = await rag_tool.query_content("Docker basics", "tutor", max_results=3)
        
        if results:
            print(f"   ✅ Success: Found {len(results)} results")
            for i, result in enumerate(results[:2], 1):
                print(f"      {i}. {result.content[:80]}...")
        else:
            print("   ❌ No results found")
            
    except Exception as e:
        print(f"   ❌ RAG Integration Error: {e}")
    
    return True

async def main():
    """Main test function."""
    try:
        print("🧪 Starting Gemini API Manager Tests")
        print("=" * 70)
        
        # Test basic functionality
        await test_gemini_failover()
        
        # Test RAG integration
        await test_rag_integration()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    asyncio.run(main())
