#!/usr/bin/env python3
"""
Startup script for the Medical Chatbot 2.0 Streamlit Frontend
Handles environment setup and frontend startup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import requests
        import pandas
        from streamlit_chat import message
        print("✅ All required frontend dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install dependencies with: pip install -r requirements.txt")
        return False

def check_backend_connection():
    """Check if backend is running"""
    try:
        import requests
        response = requests.get("http://localhost:8000/docs", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and accessible")
            return True
        else:
            print("⚠️  Backend is running but may have issues")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        print("Please start the backend server first with: python start_server.py")
        return False

def start_frontend():
    """Start the Streamlit frontend"""
    print("\n🚀 Starting Medical Chatbot 2.0 Streamlit Frontend...")
    print("=" * 60)
    
    # Check prerequisites
    if not check_dependencies():
        return False
    
    if not check_backend_connection():
        print("\n💡 To start the backend:")
        print("   cd ../backend")
        print("   python start_server.py")
        print("\n   Or use: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
        return False
    
    print("\n📋 Frontend Configuration:")
    print(f"  - URL: http://localhost:8502")
    print(f"  - Backend: http://localhost:8000")
    print(f"  - Auto-reload: True")
    
    print("\n🎯 Features:")
    print("  - Modern ChatGPT-style UI")
    print("  - Dual bot interface (Exam & Patient)")
    print("  - Real-time chat with feedback")
    print("  - Session management")
    print("  - Topic selection")
    
    print("\n" + "=" * 60)
    
    try:
        # Start Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8502",
            "--server.address", "localhost",
            "--server.headless", "true",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start frontend: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("🏥 Medical Chatbot 2.0 - Streamlit Frontend")
    print("=" * 60)
    print("📝 Note: Make sure the backend is running before starting the frontend")
    print("=" * 60)
    
    # Change to the frontend2.0 directory
    frontend_dir = Path(__file__).parent
    os.chdir(frontend_dir)
    
    # Start the frontend
    start_frontend()

if __name__ == "__main__":
    main() 