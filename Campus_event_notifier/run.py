#!/usr/bin/env python3
"""
Campus Event Notifier Startup Script
Run this script to start the application with all dependencies
"""

import os
import sys
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

def check_requirements():
    """Check if all requirements are installed"""
    try:

        import uvicorn
        import sqlalchemy
        import google.generativeai as genai
        import passlib
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
def check_environment():
    """Check if environment variables are set"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  No .env file found. Creating from template...")
        template_file = Path(".env.example")
        if template_file.exists():
            import shutil
            shutil.copy(template_file, env_file)
            print("✅ Created .env file from template")
            print("⚠️  Please edit .env file with your actual API keys and credentials")
        else:
            print("❌ .env.example file not found")
            return False

    # Check for required environment variables
    required_vars = ["GEMINI_API_KEY", "SECRET_KEY"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Setting default values for missing variables")
        if "GEMINI_API_KEY" in missing_vars:
            os.environ["GEMINI_API_KEY"] = "dummy_key"
        if "SECRET_KEY" in missing_vars:
            os.environ["SECRET_KEY"] = "dummy_secret_key"
        print("✅ Environment variables configured with defaults")
        return True

    print("✅ Environment variables are configured")
    return True

def setup_database():
    """Initialize the database"""
    try:
        from Campus_event_notifier.database import migrate_events_from_json
        migrate_events_from_json()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Starting Campus Event Notifier 2.0")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)

    print(f"✅ Python version: {sys.version.split()[0]}")

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check environment
    if not check_environment():
        sys.exit(1)

    # Setup database
    if not setup_database():
        sys.exit(1)

    print("=" * 50)
    print("🎉 All checks passed! Starting the application...")
    print("📱 The application will be available at: http://localhost:8000")
    print("🔐 Login page: http://localhost:8000/login")
    print("🤖 AI Chat: http://localhost:8000/chat")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("=" * 50)

    # Start the application
    try:
        import uvicorn
        print("🚀 Starting server with uvicorn...")
        uvicorn.run(
            "main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except Exception as e:
        print(f"❌ Failed to start application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
