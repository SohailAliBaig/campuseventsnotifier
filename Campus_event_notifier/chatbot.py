import google.generativeai as genai
import json
from datetime import datetime, timedelta
from typing import List, Dict
from sqlalchemy.orm import Session
from Campus_event_notifier.database import Event, get_db
import os
import traceback
from dotenv import load_dotenv
from pathlib import Path

def _get_gemini_key():
    # Load both root and package .env files and return a cleaned key
    project_root = Path(__file__).parent.parent
    pkg_env = Path(__file__).parent / ".env"
    root_env = project_root / ".env"
    # Load root first; only use non-empty keys
    load_dotenv(dotenv_path=root_env)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        k = key.strip('"').strip("'").strip()
        if k:
            return k

    # Try package .env next
    load_dotenv(dotenv_path=pkg_env)
    key = os.getenv("GEMINI_API_KEY")
    if key:
        k = key.strip('"').strip("'").strip()
        if k:
            return k

    return None

class EventChatbot:
    def __init__(self):
        self.system_prompt = """
        You are an AI assistant for a Campus Event Notifier system. Your role is to help students
        discover and learn about upcoming campus events. You should be friendly, informative, and
        engaging while providing accurate information about events.

        When users ask about events, you should:
        1. Provide specific details about event names, dates, locations, and descriptions
        2. Help users find events based on their interests or time preferences
        3. Suggest relevant events based on their queries
        4. Be conversational and ask follow-up questions to better understand their needs

        Always be helpful, accurate, and maintain a positive tone. If you don't have information
        about a specific event, politely let them know and suggest alternatives.
        """

    def get_upcoming_events(self, db: Session, limit: int = 10) -> List[Dict]:
        """Get upcoming events from database"""
        today = datetime.now().date()
        events = db.query(Event).filter(
            Event.date >= today.strftime("%Y-%m-%d")
        ).order_by(Event.date).limit(limit).all()

        return [
            {
                "name": event.name,
                "date": event.date,
                "location": event.location,
                "description": event.description
            }
            for event in events
        ]

    def format_events_for_prompt(self, events: List[Dict]) -> str:
        """Format events list for AI prompt"""
        if not events:
            return "No upcoming events found."

        formatted = "Here are the upcoming campus events:\n\n"
        for i, event in enumerate(events, 1):
            formatted += f"{i}. **{event['name']}**\n"
            formatted += f"   - Date: {event['date']}\n"
            formatted += f"   - Location: {event['location']}\n"
            formatted += f"   - Description: {event['description']}\n\n"

        return formatted

    async def get_chat_response(self, user_message: str, db: Session) -> str:
        """Generate AI response based on user message and event data"""
        try:
            # Get upcoming events
            events = self.get_upcoming_events(db)

            # Create context-aware prompt
            events_context = self.format_events_for_prompt(events)

            prompt = f"""
            {self.system_prompt}

            Current events information:
            {events_context}

            User question: {user_message}

            Please provide a helpful, accurate response about the campus events based on the user's question.
            If they're asking about specific types of events or time periods, help them find relevant information.
            """

            # Call Google Gemini API (configure with runtime key)
            gem_key = _get_gemini_key()
            if not gem_key:
                print("⚠️ GEMINI_API_KEY missing when attempting to call Gemini")
                return "Error: GEMINI API key not configured on server."
            genai.configure(api_key=gem_key)
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content(prompt)
            if hasattr(response, 'text'):
                return response.text.strip()
            return str(response).strip()

        except Exception as e:
            # Log detailed traceback for debugging
            print(f"Error in chatbot: {e}")
            traceback.print_exc()
            # Return a user-friendly error message; rely on Gemini only
            return "I'm sorry, I'm having trouble accessing the event information right now. Please try again later or contact support if the problem persists."

    def get_event_suggestions(self, user_interests: str, db: Session) -> List[Dict]:
        """Get event suggestions based on user interests"""
        events = self.get_upcoming_events(db, limit=20)

        # Simple keyword matching for interests
        interests = user_interests.lower().split()

        scored_events = []
        for event in events:
            score = 0
            event_text = f"{event['name']} {event['description']}".lower()

            for interest in interests:
                if interest in event_text:
                    score += 1

            if score > 0:
                scored_events.append((event, score))

        # Sort by relevance score
        scored_events.sort(key=lambda x: x[1], reverse=True)

        return [event for event, score in scored_events[:5]]

# Global chatbot instance
chatbot = EventChatbot()

async def get_chatbot_response(user_message: str, db: Session) -> str:
    """Helper function to get chatbot response"""
    return await chatbot.get_chat_response(user_message, db)
