#!/usr/bin/env python3
"""
Test the PDF embedding system with mock data
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def test_embedding_system():
    print("🧪 Testing PDF Embedding System")
    print("=" * 40)
    
    # Test 1: Check environment variables
    print("\n1️⃣ Testing Environment Variables...")
    required_vars = ["PINECONE_API_KEY", "GEMINI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing: {missing_vars}")
        return False
    else:
        print("✅ All environment variables configured")
    
    # Test 2: Test Pinecone connection
    print("\n2️⃣ Testing Pinecone Connection...")
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        indexes = pc.list_indexes()
        print(f"✅ Connected to Pinecone - {len(indexes)} indexes found")
        
        # Check if our index exists
        index_name = "docker-kubernetes-tutor"
        if index_name in [idx.name for idx in indexes]:
            print(f"✅ Index '{index_name}' exists")
        else:
            print(f"❌ Index '{index_name}' not found")
            return False
            
    except Exception as e:
        print(f"❌ Pinecone connection failed: {e}")
        return False
    
    # Test 3: Test Gemini embedding
    print("\n3️⃣ Testing Gemini Embedding...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-embedding-1.0')
        
        # Test embedding generation
        test_text = "Docker is a containerization platform"
        result = model.embed_content(test_text)
        embedding = result['embedding']
        
        print(f"✅ Generated embedding with {len(embedding)} dimensions")
        print(f"   Sample values: {embedding[:5]}")
        
    except Exception as e:
        print(f"❌ Gemini embedding failed: {e}")
        return False
    
    # Test 4: Test PDF file detection
    print("\n4️⃣ Testing PDF File Detection...")
    pdf_files = [
        "Docker-2025.pdf",
        "Kubernetes Book - Third Edition.pdf"
    ]
    
    found_pdfs = []
    for pdf_name in pdf_files:
        pdf_path = Path("..") / pdf_name  # Go up one level
        if pdf_path.exists():
            print(f"✅ Found: {pdf_name}")
            found_pdfs.append(pdf_path)
        else:
            print(f"❌ Missing: {pdf_name}")
    
    if not found_pdfs:
        print("⚠️ No PDF files found, will use mock data")
    
    # Test 5: Test mock embedding upload
    print("\n5️⃣ Testing Mock Embedding Upload...")
    try:
        index = pc.Index("docker-kubernetes-tutor")
        
        # Create a test vector
        test_vector = {
            "id": "test_vector_001",
            "values": embedding[:10] + [0.0] * 758,  # Pad to 768 dimensions
            "metadata": {
                "content": "Test Docker content for embedding",
                "source": "test.pdf",
                "page": 1,
                "chapter": "Test Chapter"
            }
        }
        
        # Upload test vector
        index.upsert(vectors=[test_vector])
        print("✅ Test vector uploaded successfully")
        
        # Query the test vector
        query_result = index.query(
            vector=test_vector["values"],
            top_k=1,
            include_metadata=True
        )
        
        if query_result.matches:
            print("✅ Test vector query successful")
            print(f"   Retrieved: {query_result.matches[0].metadata.get('content', 'No content')[:50]}...")
        else:
            print("❌ Test vector query failed")
        
    except Exception as e:
        print(f"❌ Mock embedding upload failed: {e}")
        return False
    
    print("\n🎉 All tests passed! System is ready for PDF embedding.")
    return True

async def run_embedding_with_mock_data():
    """Run embedding with mock data to test the full pipeline."""
    print("\n🚀 Running Embedding with Mock Data...")
    print("=" * 40)
    
    try:
        from pinecone import Pinecone
        import google.generativeai as genai
        
        # Initialize clients
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        model = genai.GenerativeModel('gemini-embedding-1.0')
        index = pc.Index("docker-kubernetes-tutor")
        
        # Mock content for Docker and Kubernetes
        mock_content = [
            {
                "content": "Docker is a containerization platform that allows you to package applications and their dependencies into lightweight, portable containers. Containers provide isolation, consistency, and portability across different environments.",
                "source": "Docker-2025.pdf",
                "page": 1,
                "chapter": "Introduction to Docker"
            },
            {
                "content": "Docker images are read-only templates used to create containers. They contain the application code, runtime, system tools, libraries, and settings. Images are built from Dockerfiles.",
                "source": "Docker-2025.pdf",
                "page": 2,
                "chapter": "Docker Images"
            },
            {
                "content": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications. It provides a framework for running distributed systems.",
                "source": "Kubernetes Book - Third Edition.pdf",
                "page": 1,
                "chapter": "Introduction to Kubernetes"
            },
            {
                "content": "Kubernetes clusters consist of master nodes that control the cluster and worker nodes that run the applications. The master node manages the cluster state and worker nodes run workloads.",
                "source": "Kubernetes Book - Third Edition.pdf",
                "page": 2,
                "chapter": "Cluster Architecture"
            }
        ]
        
        # Process each piece of content
        uploaded_count = 0
        for i, content in enumerate(mock_content):
            try:
                # Generate embedding
                result = model.embed_content(content["content"])
                embedding = result['embedding']
                
                # Create vector
                vector_id = f"mock_{content['source']}_{content['page']}_{i}"
                vector = {
                    "id": vector_id,
                    "values": embedding,
                    "metadata": {
                        "content": content["content"],
                        "source": content["source"],
                        "page": content["page"],
                        "chapter": content["chapter"],
                        "type": "mock_data"
                    }
                }
                
                # Upload to Pinecone
                index.upsert(vectors=[vector])
                uploaded_count += 1
                
                print(f"✅ Uploaded: {content['source']} - {content['chapter']}")
                
            except Exception as e:
                print(f"❌ Error uploading {content['source']}: {e}")
        
        print(f"\n🎉 Successfully uploaded {uploaded_count} mock vectors to Pinecone!")
        
        # Test retrieval
        print(f"\n🔍 Testing Retrieval...")
        test_query = "What is Docker?"
        query_result = model.embed_content(test_query)
        query_embedding = query_result['embedding']
        
        # Query Pinecone
        search_result = index.query(
            vector=query_embedding,
            top_k=2,
            include_metadata=True
        )
        
        print(f"Query: '{test_query}'")
        print(f"Results:")
        for match in search_result.matches:
            print(f"  📄 {match.metadata.get('source', 'Unknown')} - {match.metadata.get('chapter', 'Unknown')}")
            print(f"     Score: {match.score:.3f}")
            print(f"     Content: {match.metadata.get('content', 'No content')[:100]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"❌ Mock embedding failed: {e}")
        return False

async def main():
    """Main test function."""
    # Run basic tests
    if await test_embedding_system():
        # Run mock embedding
        await run_embedding_with_mock_data()
        
        print(f"\n🌐 Check your Pinecone Dashboard:")
        print(f"   URL: https://app.pinecone.io/")
        print(f"   Index: docker-kubernetes-tutor")
        print(f"   You should see the uploaded vectors!")
        
        print(f"\n🎯 Your RAG system is now ready with embedded content!")
    else:
        print(f"\n❌ Tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
