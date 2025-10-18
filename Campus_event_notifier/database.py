from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json
import os

# Database setup
DATABASE_URL = "sqlite:///./campus_events.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# User model for authentication
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    created_at = Column(DateTime, default=datetime.utcnow)

# Event model
class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    date = Column(String, nullable=False)  # Store as string for simplicity
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# Chat message model for chatbot history
class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        return db
    finally:
        db.close()

# Migration function to import existing events from db.json
def migrate_events_from_json():
    """Import events from db.json to database, adding new ones if they don't exist"""
    db = SessionLocal()
    try:
        # Load events from JSON
        db_json_path = os.path.join(os.path.dirname(__file__), "db.json")
        if os.path.exists(db_json_path):
            with open(db_json_path, "r") as f:
                events_data = json.load(f)

            # Get existing event names
            existing_names = {event.name for event in db.query(Event).all()}

            # Import new events
            added_count = 0
            for event_data in events_data:
                if event_data["name"] not in existing_names:
                    event = Event(
                        name=event_data["name"],
                        date=event_data["date"],
                        location=event_data["location"],
                        description=event_data["description"]
                    )
                    db.add(event)
                    added_count += 1

            # Update existing events' dates to future if they are in 2024
            updated_count = 0
            for event in db.query(Event).all():
                if event.date.startswith('2024'):
                    event.date = event.date.replace('2024', '2025')
                    updated_count += 1

            if updated_count > 0:
                db.commit()
                print(f"Updated {updated_count} events' dates to 2025")

            if added_count > 0:
                db.commit()
                print(f"Successfully added {added_count} new events from db.json to database")
            else:
                print("No new events to add")
    except Exception as e:
        print(f"Error migrating events: {e}")
    finally:
        db.close()

# Initialize database with migration
migrate_events_from_json()
