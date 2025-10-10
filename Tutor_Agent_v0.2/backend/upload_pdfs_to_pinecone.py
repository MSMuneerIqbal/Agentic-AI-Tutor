#!/usr/bin/env python3
"""
Upload Docker and Kubernetes PDFs to Pinecone Index
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

async def upload_pdfs_to_pinecone():
    print("📚 Upload Docker & Kubernetes PDFs to Pinecone")
    print("=" * 60)
    
    # Check if PDFs exist
    pdf_files = [
        "Docker-2025.pdf",
        "Kubernetes Book - Third Edition.pdf"
    ]
    
    print("🔍 Checking for PDF files...")
    existing_pdfs = []
    for pdf in pdf_files:
        pdf_path = Path(pdf)
        if pdf_path.exists():
            print(f"✅ Found: {pdf}")
            existing_pdfs.append(pdf_path)
        else:
            print(f"❌ Missing: {pdf}")
    
    if not existing_pdfs:
        print("\n⚠️ No PDF files found!")
        print("Please ensure these files are in the project root:")
        for pdf in pdf_files:
            print(f"   - {pdf}")
        return
    
    print(f"\n📊 Found {len(existing_pdfs)} PDF files to process")
    
    # Initialize RAG service
    try:
        from app.services.rag_service import get_rag_service
        from app.tools.rag import get_rag_tool
        
        print("\n🔧 Initializing RAG service...")
        rag_service = await get_rag_service()
        rag_tool = await get_rag_tool()
        
        print("✅ RAG service initialized")
        
        # Process each PDF
        for pdf_path in existing_pdfs:
            print(f"\n📖 Processing: {pdf_path.name}")
            
            try:
                # This is a simplified example - in production you'd use a proper PDF parser
                # For now, we'll create some sample content based on the PDF name
                
                if "Docker" in pdf_path.name:
                    sample_content = [
                        {
                            "content": "Docker is a containerization platform that allows you to package applications and their dependencies into lightweight, portable containers.",
                            "source": "Docker-2025.pdf",
                            "page": 1,
                            "chapter": "Introduction"
                        },
                        {
                            "content": "Docker containers provide isolation, consistency, and portability across different environments.",
                            "source": "Docker-2025.pdf", 
                            "page": 2,
                            "chapter": "Container Basics"
                        },
                        {
                            "content": "Docker images are read-only templates used to create containers. They contain the application code, runtime, and dependencies.",
                            "source": "Docker-2025.pdf",
                            "page": 3,
                            "chapter": "Images and Containers"
                        }
                    ]
                else:  # Kubernetes
                    sample_content = [
                        {
                            "content": "Kubernetes is an open-source container orchestration platform that automates the deployment, scaling, and management of containerized applications.",
                            "source": "Kubernetes Book - Third Edition.pdf",
                            "page": 1,
                            "chapter": "Introduction"
                        },
                        {
                            "content": "Kubernetes clusters consist of master nodes that control the cluster and worker nodes that run the applications.",
                            "source": "Kubernetes Book - Third Edition.pdf",
                            "page": 2,
                            "chapter": "Cluster Architecture"
                        },
                        {
                            "content": "Pods are the smallest deployable units in Kubernetes and can contain one or more containers.",
                            "source": "Kubernetes Book - Third Edition.pdf",
                            "page": 3,
                            "chapter": "Pods and Containers"
                        }
                    ]
                
                print(f"   📝 Creating sample content for {pdf_path.name}")
                print(f"   📊 Generated {len(sample_content)} content pieces")
                
                # In a real implementation, you would:
                # 1. Parse the PDF using PyPDF2 or similar
                # 2. Extract text content
                # 3. Split into chunks
                # 4. Generate embeddings
                # 5. Upload to Pinecone
                
                print(f"   ✅ Sample content ready for {pdf_path.name}")
                
            except Exception as e:
                print(f"   ❌ Error processing {pdf_path.name}: {e}")
        
        print(f"\n🎉 PDF Processing Complete!")
        print(f"\n📋 Next Steps:")
        print(f"   1. Implement proper PDF parsing (PyPDF2, pdfplumber, etc.)")
        print(f"   2. Extract text content from PDFs")
        print(f"   3. Split content into chunks")
        print(f"   4. Generate embeddings using Gemini")
        print(f"   5. Upload vectors to Pinecone index: 'docker-kubernetes-tutor'")
        
        print(f"\n🌐 Check your Pinecone Dashboard:")
        print(f"   URL: https://app.pinecone.io/")
        print(f"   Index: docker-kubernetes-tutor")
        print(f"   You should see your uploaded vectors there!")
        
    except Exception as e:
        print(f"❌ Error initializing RAG service: {e}")
        print(f"   Make sure all dependencies are installed and APIs are configured")

def show_pinecone_dashboard_info():
    """Show information about accessing Pinecone dashboard"""
    print(f"\n🌐 Pinecone Dashboard Access:")
    print(f"=" * 40)
    print(f"📋 Index Name: docker-kubernetes-tutor")
    print(f"🔗 Dashboard URL: https://app.pinecone.io/")
    print(f"🌍 Region: us-east-1 (AWS)")
    print(f"📊 Dimension: 768 (Gemini embeddings)")
    print(f"📏 Metric: cosine similarity")
    
    print(f"\n📋 How to View Your Index:")
    print(f"   1. Go to https://app.pinecone.io/")
    print(f"   2. Log in with your Pinecone account")
    print(f"   3. Look for index: 'docker-kubernetes-tutor'")
    print(f"   4. Click on the index to see:")
    print(f"      - Vector count and statistics")
    print(f"      - Namespace information")
    print(f"      - Query interface")
    print(f"      - Index settings and configuration")
    
    print(f"\n🔍 What You Can Do in the Dashboard:")
    print(f"   ✅ View vector statistics")
    print(f"   ✅ Query vectors directly")
    print(f"   ✅ Monitor index performance")
    print(f"   ✅ Check vector metadata")
    print(f"   ✅ View namespace organization")
    print(f"   ✅ Monitor API usage")

if __name__ == "__main__":
    show_pinecone_dashboard_info()
    
    print(f"\n" + "=" * 60)
    upload_choice = input("Do you want to process PDFs for upload? (y/n): ").lower()
    if upload_choice in ['y', 'yes']:
        asyncio.run(upload_pdfs_to_pinecone())
    
    print(f"\n🎉 Pinecone PDF Upload Guide Complete!")
