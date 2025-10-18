#!/usr/bin/env python3
"""
Test user registration
"""

from Campus_event_notifier.database import get_db, User
from Campus_event_notifier.auth import create_user
from sqlalchemy.orm import Session

def test_register():
    """Test user registration"""
    db = get_db()
    try:
        # Test data
        email = "test@example.com"
        password = "testpass123"
        username = "testuser"
        full_name = "Test User"

        print("Testing user registration...")

        # Check if user already exists
        existing = db.query(User).filter(User.email == email).first()
        if existing:
            print("User already exists, deleting...")
            db.delete(existing)
            db.commit()

        # Create user
        user = create_user(db, email, password, username, full_name)
        print(f"✅ User created: {user.email}, {user.username}")

        # Verify user in database
        db_user = db.query(User).filter(User.email == email).first()
        if db_user:
            print(f"✅ User found in database: {db_user.email}")
        else:
            print("❌ User not found in database")

        # Clean up
        db.delete(user)
        db.commit()
        print("✅ Test user deleted")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    test_register()
