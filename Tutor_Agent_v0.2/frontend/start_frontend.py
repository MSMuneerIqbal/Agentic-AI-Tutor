#!/usr/bin/env python3
"""
Simple frontend startup script for Tutor GPT Frontend
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Start the frontend server."""
    # Get the frontend directory
    frontend_dir = Path(__file__).parent
    
    print("🎨 Starting Tutor GPT Frontend Server...")
    print(f"📁 Frontend directory: {frontend_dir}")
    
    # Change to frontend directory
    os.chdir(frontend_dir)
    
    try:
        # Start Next.js development server
        cmd = ["npm", "run", "dev"]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print("🌐 Frontend will be available at: http://localhost:3000 (or 3001 if 3000 is busy)")
        print("🔗 Backend API: http://localhost:8000")
        print("\n" + "="*50)
        
        # Start the server
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 Frontend server stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
