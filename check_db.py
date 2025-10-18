#!/usr/bin/env python3
"""
Check database tables and contents
"""

import sqlite3
import os

def check_database():
    """Check if database exists and has required tables"""
    db_path = "campus_events.db"

    if not os.path.exists(db_path):
        print(f"❌ Database file '{db_path}' not found")
        return False

    print(f"✅ Database file '{db_path}' found")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print(f"📋 Tables in database: {[table[0] for table in tables]}")

    required_tables = ['users', 'events', 'chat_messages']
    missing_tables = []

    for table in required_tables:
        if (table,) not in tables:
            missing_tables.append(table)

    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False

    print("✅ All required tables exist")

    # Check events table
    cursor.execute("SELECT COUNT(*) FROM events")
    event_count = cursor.fetchone()[0]
    print(f"📅 Events in database: {event_count}")

    # Check users table
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"👥 Users in database: {user_count}")

    # Show sample events
    cursor.execute("SELECT name, date, location FROM events LIMIT 3")
    sample_events = cursor.fetchall()
    if sample_events:
        print("📅 Sample events:")
        for event in sample_events:
            print(f"  - {event[0]} ({event[1]}) at {event[2]}")

    conn.close()
    return True

if __name__ == "__main__":
    check_database()
