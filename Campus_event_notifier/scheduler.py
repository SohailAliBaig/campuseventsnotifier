"""
Event Scheduler Module
Handles automated event notifications and reminders
"""

import schedule
import time
from datetime import datetime, timedelta
from Campus_event_notifier.database import get_db, Event
from Campus_event_notifier.notification import send_event_notification
from sqlalchemy.orm import Session

class EventScheduler:
    def __init__(self):
        self.jobs = []

    def schedule_event_reminders(self, db: Session):
        """
        Schedule reminders for upcoming events
        """
        # Get events in the next 7 days
        today = datetime.now().date()
        next_week = today + timedelta(days=7)

        events = db.query(Event).filter(
            Event.date >= today.strftime("%Y-%m-%d"),
            Event.date <= next_week.strftime("%Y-%m-%d")
        ).all()

        for event in events:
            event_date = datetime.strptime(event.date, "%Y-%m-%d").date()
            days_until = (event_date - today).days

            # Schedule reminder 1 day before event
            if days_until == 1:
                # In a real implementation, you'd store subscriber emails
                # For now, this is a placeholder
                print(f"📅 Reminder scheduled for event: {event.name} on {event.date}")

    def start_scheduler(self):
        """
        Start the background scheduler
        """
        # Schedule daily checks at 9 AM
        schedule.every().day.at("09:00").do(self.daily_reminder_check)

        print("🕒 Event scheduler started")

        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

    def daily_reminder_check(self):
        """
        Daily check for events requiring reminders
        """
        try:
            db = next(get_db())
            self.schedule_event_reminders(db)
            db.close()
        except Exception as e:
            print(f"❌ Scheduler error: {e}")

# Global scheduler instance
scheduler = EventScheduler()

def start_event_scheduler():
    """
    Start the event notification scheduler
    """
    scheduler.start_scheduler()
