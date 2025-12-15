#!/usr/bin/env python3
"""
KAI Arena - Setup Script
"""

import os
import sys
from app import app, db
from config import Config

def setup_database():
    """Initialize the database"""
    with app.app_context():
        db.create_all()
        print("[OK] Database created successfully")
        
        # Create upload directories
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs('static/uploads', exist_ok=True)
        print("[OK] Upload directories created")

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import flask
        import flask_sqlalchemy
        import werkzeug
        import jwt
        import dotenv
        print("[OK] All dependencies are installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def main():
    print("=" * 50)
    print("KAI Arena - Setup")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup database
    try:
        setup_database()
    except Exception as e:
        print(f"[ERROR] Error setting up database: {e}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("Setup completed successfully!")
    print("\nTo run the application:")
    print("1. Activate virtual environment")
    print("2. Run: python app.py")
    print("3. Open: http://localhost:5000")
    print("\nDefault admin account:")
    print("Username: admin")
    print("Password: admin123")
    print("=" * 50)

if __name__ == "__main__":
    main()