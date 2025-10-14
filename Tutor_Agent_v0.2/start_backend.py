#!/usr/bin/env python3
"""Backend startup script with proper Python path."""

import os
import sys
import subprocess
from pathlib import Path

def start_backend():
    """Start the backend server with proper configuration."""
    
    # Get the project root directory
    project_root = Path(__file__).parent
    backend_dir = project_root / "backend"
    
    # Set environment variables
    env = os.environ.copy()
    env["PYTHONPATH"] = str(backend_dir)
    
    print("🚀 Starting Tutor GPT Backend Server...")
    print(f"📁 Project Root: {project_root}")
    print(f"📁 Backend Directory: {backend_dir}")
    print(f"🐍 Python Path: {env['PYTHONPATH']}")
    print("=" * 50)
    
    # Change to backend directory and start server
    os.chdir(backend_dir)
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ]
        
        subprocess.run(cmd, env=env, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_backend()
