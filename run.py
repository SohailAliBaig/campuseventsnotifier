#!/usr/bin/env python3
"""
Campus Event Notifier Startup Script
Run this script to start the application with all dependencies
"""

import os
import sys
import subprocess
from pathlib import Path
import uvicorn

def print_header():
    """Print application header"""
    print("\n🚀 Starting Campus Event Notifier 2.0")
    print("=" * 50)
    print(f"✅ Python version: {sys.version.split()[0]}")

def check_requirements():
    """Check if all requirements are installed"""
    try:
        import fastapi
        import sqlalchemy
        import jinja2
        import dotenv
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_environment():
    """Check if environment variables are set"""
    from dotenv import load_dotenv
    
    # Load environment variables from both locations
    project_root = Path(__file__).parent
    env_file = project_root / ".env"
    pkg_env = project_root / "Campus_event_notifier" / ".env"
    
    load_dotenv(dotenv_path=env_file)
    load_dotenv(dotenv_path=pkg_env)
    
    print("✅ Environment variables are configured")
    return True

def initialize_database():
    """Initialize the database"""
    try:
        from Campus_event_notifier.database import Base, engine
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")
        return False

def main():
    """Main entry point"""
    print_header()
    
    if not all([
        check_requirements(),
        check_environment(),
        initialize_database()
    ]):
        print("\n❌ Setup failed. Please fix the errors above and try again.")
        return
    
    print("\n✨ All checks passed! Starting the server...")
    print("=" * 50)
    
    # Start the FastAPI server
    uvicorn.run(
        "Campus_event_notifier.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=["Campus_event_notifier"],
        log_level="info"
    )

if __name__ == "__main__":
    main()