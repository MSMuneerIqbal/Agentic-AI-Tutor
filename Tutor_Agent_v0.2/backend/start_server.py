#!/usr/bin/env python3
"""
Simple server startup script for Tutor GPT Backend
This ensures the backend starts from the correct directory
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    """Start the backend server."""
    # Get the backend directory
    backend_dir = Path(__file__).parent
    
    print("🚀 Starting Tutor GPT Backend Server...")
    print(f"📁 Backend directory: {backend_dir}")
    
    # Change to backend directory
    os.chdir(backend_dir)
    
    # Set Python path to include current directory
    env = os.environ.copy()
    env['PYTHONPATH'] = str(backend_dir)
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ]
        
        print(f"🔧 Running command: {' '.join(cmd)}")
        print("🌐 Server will be available at: http://localhost:8000")
        print("📚 API docs will be available at: http://localhost:8000/docs")
        print("💚 Health check: http://localhost:8000/healthz")
        print("\n" + "="*50)
        
        # Start the server
        subprocess.run(cmd, env=env)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
