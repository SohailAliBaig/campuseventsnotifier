from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import json
import os

# Database setup
DATABASE_URL = "sqlite:///./campus_events.db"
engine = create_engine(
    DATABASE_URL, 
    connect_args={
        "check_same_thread": False,
        "timeout": 10,  # Reduced timeout
        "cached_statements": True  # Enable statement caching
    },
    pool_size=10,  # Reduced pool size for better resource usage
    max_overflow=2,
    pool_pre_ping=True,
    pool_recycle=1800,  # Reduced recycle time
    pool_timeout=10  # Added pool timeout
)
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
    name = Column(String, nullable=False)  # Changed from title to name
    date = Column(String, nullable=False)  # Changed from DateTime to String
    location = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    @classmethod
    def create_sample_events(cls, db):
        # Add sample events if none exist
        if db.query(cls).count() == 0:
            sample_events = [
                # Tech Events (N-Block)
                {
                    "title": "AI & Machine Learning Workshop",
                    "date": datetime.now() + timedelta(days=5),
                    "location": "N-Block, Computer Lab 3",
                    "description": "Hands-on workshop on AI fundamentals and practical ML applications using Python and TensorFlow."
                },
                {
                    "title": "Cybersecurity Hackathon",
                    "date": datetime.now() + timedelta(days=7),
                    "location": "N-Block, Innovation Hub",
                    "description": "24-hour hackathon focusing on cybersecurity challenges and ethical hacking practices."
                },
                {
                    "title": "Web Development Bootcamp",
                    "date": datetime.now() + timedelta(days=10),
                    "location": "N-Block, Software Center",
                    "description": "Intensive bootcamp covering full-stack web development with modern frameworks."
                },
                
                # Sports Events (Cricket Ground)
                {
                    "title": "Inter-College Cricket Tournament",
                    "date": datetime.now() + timedelta(days=8),
                    "location": "University Cricket Ground",
                    "description": "Annual cricket tournament featuring teams from different colleges competing for the championship."
                },
                {
                    "title": "Sports Meet 2025",
                    "date": datetime.now() + timedelta(days=15),
                    "location": "University Cricket Ground",
                    "description": "Annual sports meet featuring athletics, cricket, football, and other sports competitions."
                },
                
                # Photography Events (A-Block & U-Block OAT)
                {
                    "title": "Photography Workshop",
                    "date": datetime.now() + timedelta(days=6),
                    "location": "A-Block OAT",
                    "description": "Learn professional photography techniques from industry experts. Bring your own camera."
                },
                {
                    "title": "Cultural Photography Contest",
                    "date": datetime.now() + timedelta(days=12),
                    "location": "U-Block OAT",
                    "description": "Theme-based photography competition showcasing campus culture and student life."
                },
                
                # Engineering Events (H-Block)
                {
                    "title": "ECE Project Exhibition",
                    "date": datetime.now() + timedelta(days=9),
                    "location": "H-Block, ECE Labs",
                    "description": "Exhibition of innovative electronics and communication engineering projects by final year students."
                },
                {
                    "title": "EEE Workshop: Renewable Energy",
                    "date": datetime.now() + timedelta(days=11),
                    "location": "H-Block, Power Systems Lab",
                    "description": "Workshop on renewable energy technologies and sustainable power systems."
                },
                {
                    "title": "Chemical Engineering Symposium",
                    "date": datetime.now() + timedelta(days=13),
                    "location": "H-Block, Process Lab",
                    "description": "National symposium on recent advances in chemical engineering and process technology."
                },
                {
                    "title": "Food Tech Innovation Fair",
                    "date": datetime.now() + timedelta(days=14),
                    "location": "H-Block, Food Processing Lab",
                    "description": "Showcase of innovative food products and technologies developed by Food Tech students."
                },
                
                # Library Events
                {
                    "title": "Book Reading Competition",
                    "date": datetime.now() + timedelta(days=4),
                    "location": "Central Library, Reading Hall",
                    "description": "Inter-department book reading and review competition with prizes for best presentations."
                },
                {
                    "title": "Literary Quiz Competition",
                    "date": datetime.now() + timedelta(days=16),
                    "location": "Central Library, Conference Room",
                    "description": "Test your knowledge of literature, authors, and books in this exciting quiz competition."
                },
                {
                    "title": "Research Paper Writing Workshop",
                    "date": datetime.now() + timedelta(days=18),
                    "location": "Central Library, Digital Zone",
                    "description": "Learn effective research paper writing techniques and publication strategies."
                }
            ]
            
            for event_data in sample_events:
                event = cls(**event_data)
                db.add(event)
            
            db.commit()

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
