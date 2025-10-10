#!/usr/bin/env python3
"""
Check Pinecone Index Status and Details
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def check_pinecone_index():
    print("🔍 Pinecone Index Status Check")
    print("=" * 50)
    
    # Get API key
    api_key = os.getenv("PINECONE_API_KEY")
    if not api_key:
        print("❌ PINECONE_API_KEY not found in environment variables")
        return
    
    print(f"✅ Pinecone API Key: {api_key[:10]}...{api_key[-10:]}")
    
    try:
        from pinecone import Pinecone
        
        # Initialize Pinecone client
        pc = Pinecone(api_key=api_key)
        
        # Get index name from our configuration
        index_name = "docker-kubernetes-tutor"
        print(f"\n📋 Index Name: {index_name}")
        
        # List all indexes
        print("\n📊 All Indexes in Your Account:")
        indexes = pc.list_indexes()
        
        if not indexes:
            print("   No indexes found in your account")
        else:
            for idx in indexes:
                status = "✅ EXISTS" if idx.name == index_name else "   Other"
                print(f"   {status} - {idx.name}")
        
        # Check if our specific index exists
        print(f"\n🎯 Checking Index: {index_name}")
        
        if index_name in [idx.name for idx in indexes]:
            print(f"✅ Index '{index_name}' EXISTS in your Pinecone account!")
            
            # Get index details
            try:
                index = pc.Index(index_name)
                stats = index.describe_index_stats()
                
                print(f"\n📈 Index Statistics:")
                print(f"   Total Vectors: {stats.total_vector_count}")
                print(f"   Dimension: {stats.dimension}")
                print(f"   Index Fullness: {stats.index_fullness}")
                
                if stats.namespaces:
                    print(f"   Namespaces: {list(stats.namespaces.keys())}")
                    for ns, details in stats.namespaces.items():
                        print(f"     - {ns}: {details.vector_count} vectors")
                else:
                    print("   Namespaces: default (no custom namespaces)")
                    
            except Exception as e:
                print(f"⚠️ Could not get index details: {e}")
                
        else:
            print(f"❌ Index '{index_name}' NOT FOUND in your Pinecone account")
            print(f"\n🔧 To create the index, run your RAG service or use the setup script")
        
        # Show dashboard URL
        print(f"\n🌐 Pinecone Dashboard:")
        print(f"   URL: https://app.pinecone.io/")
        print(f"   Look for index: '{index_name}'")
        print(f"   Region: us-east-1 (AWS)")
        
        # Show how to find it in dashboard
        print(f"\n📋 How to Find Your Index in Pinecone Dashboard:")
        print(f"   1. Go to https://app.pinecone.io/")
        print(f"   2. Log in with your Pinecone account")
        print(f"   3. Look for the index named: '{index_name}'")
        print(f"   4. Click on it to see details, statistics, and vector data")
        print(f"   5. You can also query vectors directly from the dashboard")
        
    except ImportError:
        print("❌ Pinecone package not installed")
        print("   Run: uv add pinecone-client")
    except Exception as e:
        print(f"❌ Error connecting to Pinecone: {e}")
        print(f"   Check your API key and internet connection")

def create_index_if_needed():
    """Create the index if it doesn't exist"""
    print(f"\n🔧 Creating Index if Needed...")
    
    try:
        from pinecone import Pinecone, ServerlessSpec
        
        api_key = os.getenv("PINECONE_API_KEY")
        pc = Pinecone(api_key=api_key)
        
        index_name = "docker-kubernetes-tutor"
        
        # Check if index exists
        existing_indexes = pc.list_indexes()
        if index_name in [idx.name for idx in existing_indexes]:
            print(f"✅ Index '{index_name}' already exists")
            return
        
        # Create index
        print(f"🚀 Creating index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=768,  # Gemini embedding dimension
            metric="cosine",
            spec=ServerlessSpec(
                cloud="aws",
                region="us-east-1"
            )
        )
        
        print(f"✅ Index '{index_name}' created successfully!")
        print(f"   Dimension: 768")
        print(f"   Metric: cosine")
        print(f"   Cloud: AWS us-east-1")
        
    except Exception as e:
        print(f"❌ Failed to create index: {e}")

if __name__ == "__main__":
    check_pinecone_index()
    
    # Ask if user wants to create index
    print(f"\n" + "=" * 50)
    create_choice = input("Do you want to create the index if it doesn't exist? (y/n): ").lower()
    if create_choice in ['y', 'yes']:
        create_index_if_needed()
    
    print(f"\n🎉 Pinecone Index Check Complete!")
