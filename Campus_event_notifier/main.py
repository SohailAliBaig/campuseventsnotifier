from fastapi import FastAPI, Request, Form, Depends, HTTPException, Query, Body
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import json
from dotenv import load_dotenv
import os
from pathlib import Path
from datetime import datetime, timedelta

# Import local modules (use package-less imports so module path resolution stays simple)
from Campus_event_notifier.database import get_db, Event, User
from Campus_event_notifier.auth import authenticate_user, create_access_token, get_current_active_user, create_user, SECRET_KEY, ALGORITHM
from Campus_event_notifier.notification import send_notification
from Campus_event_notifier.agent import ask_agentic_ai
from Campus_event_notifier.chatbot import get_chatbot_response
from jose import jwt as jose_jwt

# Load environment variables from both project root and package .env (if present)
project_root = Path(__file__).parent.parent
pkg_env = Path(__file__).parent / ".env"
root_env = project_root / ".env"
# Load root first, then package (package can override root if required)
load_dotenv(dotenv_path=root_env)
load_dotenv(dotenv_path=pkg_env)

# Debug: print both .env paths and current GEMINI_API_KEY (masked) at startup
try:
    print(f"root .env path: {root_env} (exists={root_env.exists()})")
    print(f"package .env path: {pkg_env} (exists={pkg_env.exists()})")
    import os
    gem = os.getenv("GEMINI_API_KEY")
    print("GEMINI_API_KEY (repr):", repr(gem))
except Exception:
    pass

app = FastAPI(title="Campus Event Notifier", version="2.0")

# Set up CORS middleware first
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files with optimized caching
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware

# Add Gzip compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Mount static files
static_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(
    directory=str(static_path),
    html=True,
    check_dir=True
), name="static")

# Set up templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))

# Cache for events data
from fastapi.concurrency import run_in_threadpool
from cachetools import TTLCache
import asyncio

# Cache events for 5 minutes
events_cache = TTLCache(maxsize=100, ttl=300)

# Basic route for home page
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # Try to get events from cache first
    cache_key = 'upcoming_events'
    cached_events = events_cache.get(cache_key)
    
    if cached_events is not None:
        return templates.TemplateResponse(
            "index.html",
            {"request": request, "events_by_category": cached_events}
        )
    
    # Get events from database
    def get_events():
        current_time = datetime.now()
        # Since date is stored as string, we need to filter differently
        all_events = db.query(Event).order_by(Event.date).limit(20).all()
        # Filter events that are upcoming (assuming date strings are in future)
        upcoming_events = []
        for event in all_events:
            try:
                if isinstance(event.date, str):
                    event_datetime = datetime.strptime(event.date, "%Y-%m-%d %H:%M:%S.%f")
                else:
                    event_datetime = event.date
                if event_datetime >= current_time:
                    upcoming_events.append(event)
            except:
                # If date parsing fails, include the event anyway
                upcoming_events.append(event)
        return upcoming_events
    
    # Run database query in thread pool
    events = await run_in_threadpool(get_events)

    # Use a dictionary for faster category lookup
    category_map = {
        'n-block': 'Tech Events',
        'cricket ground': 'Sports Events',
        'oat': 'Cultural & Photography Events',
        'h-block': 'Engineering Events',
        'library': 'Academic Events'
    }

    def get_event_category(location):
        location = location.lower()
        for key, category in category_map.items():
            if key in location:
                return category
        return 'Other Events'

    # Group events by category
    events_by_category = {}
    for event in events:
        category = get_event_category(event.location)
        if category not in events_by_category:
            events_by_category[category] = []

        # Parse date string to datetime for formatting
        try:
            if isinstance(event.date, str):
                event_date = datetime.strptime(event.date, "%Y-%m-%d %H:%M:%S.%f")
            else:
                event_date = event.date
            formatted_date = event_date.strftime("%B %d, %Y")
        except:
            formatted_date = event.date  # fallback to raw date

        events_by_category[category].append({
            "name": event.name,
            "date": formatted_date,
            "location": event.location,
            "description": event.description,
            "category": category
        })
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request,
            "events_by_category": events_by_category
        }
    )

# Login routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

# Register routes
@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Subscribe endpoint
@app.post("/subscribe")
async def subscribe(request: Request, form_data: dict = Body(...)):
    try:
        email = form_data.get("email")
        if not email:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Email is required",
                    "success": False
                }
            )
            
        # Quick validation before proceeding
        from email_validator import validate_email, EmailNotValidError
        try:
            validate_email(email)
        except EmailNotValidError:
            return JSONResponse(
                status_code=400,
                content={
                    "message": "Invalid email address",
                    "success": False
                }
            )
        
        print(f"📝 Processing subscription for: {email}")
        
        # Save subscriber to file
        subscriber_file = Path(__file__).parent / "subscribers.txt"
        with open(subscriber_file, "a") as f:
            f.write(f"{email}\n")
        print(f"✅ Saved subscriber to {subscriber_file}")
        
        # Send welcome email
        subject = "Welcome to Campus Events!"
        message = f"""
Dear Subscriber,

Thank you for subscribing to Campus Events! 🎉

You'll now receive notifications about:
• New campus events
• Event updates and changes
• Upcoming event reminders

Stay tuned for exciting events happening on campus!

Best regards,
The Campus Events Team
"""
        
        from Campus_event_notifier.notification import send_notification
        email_sent = send_notification(email, subject, message)
        
        if not email_sent:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "Subscribed successfully, but email notification failed",
                    "success": True,
                    "email_sent": False
                }
            )
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Subscribed successfully!",
                "success": True,
                "email_sent": True
            }
        )
    except Exception as e:
        print(f"❌ Error in subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def is_database_empty(db: Session) -> bool:
    """Check if the events table is empty"""
    return db.query(Event).count() == 0

# Agentic AI endpoint (JSON)
@app.post("/agent")
async def agent_endpoint(prompt: str = Body(..., embed=True)):
    response = ask_agentic_ai(prompt)
    return {"response": response}

# Authentication routes
@app.get("/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.get("/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        user = create_user(db, email, password, name)
        access_token = create_access_token(data={"sub": user.email})
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie("access_token")
    return response
    import traceback
    traceback.print_exc()

# Load events from database
def load_events(db: Session):
    events = db.query(Event).all()
    return [
        {
            "name": event.name,
            "date": event.date,
            "location": event.location,
            "description": event.description
        }
        for event in events
    ]

# Home page: display events + subscription form
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    events = load_events(db)
    return templates.TemplateResponse("index.html", {"request": request, "events": events})

# Authentication Routes
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@app.post("/auth/login")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Incorrect email or password"}
        )

    access_token = create_access_token(data={"sub": user.email})
    response = RedirectResponse(url="/dashboard", status_code=302)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response

@app.post("/auth/register")
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    username: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    try:
        create_user(db, email, password, username, full_name)
        # Send welcome notification
        send_notification(email, "Welcome!", "You have successfully registered for Campus Event Notifier!")
        return RedirectResponse(url="/login", status_code=302)
    except HTTPException as e:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": e.detail}
        )

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie(key="access_token")
    return response

# Protected Routes
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    events = load_events(db)
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "events": events, "user": current_user}
    )

# Helper: optional user from access_token cookie (does not raise)
def _get_user_from_request(request: Request, db: Session):
    token = request.cookies.get("access_token")
    if not token:
        return None
    if token.startswith("Bearer "):
        token = token.split(" ", 1)[1]
    try:
        payload = jose_jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
        user = db.query(User).filter(User.email == email).first()
        return user
    except Exception:
        return None

# Chat Routes
@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, question: str = Query(None), db: Session = Depends(get_db)):
    try:
        user = _get_user_from_request(request, db)
        return templates.TemplateResponse("chat.html", {"request": request, "user": user, "initial_question": question})
    except Exception as e:
        # Log and render template with an error message instead of raising 401
        print(f"⚠️ Error while serving /chat: {e}")
        return templates.TemplateResponse("chat.html", {"request": request, "user": None, "initial_question": question, "error": "Authentication not required to view this page."})

# POST route used by the HTML form (returns rendered page)
@app.post("/chat", response_class=HTMLResponse)
async def chat_form(request: Request, message: str = Form(...), db: Session = Depends(get_db)):
    user = _get_user_from_request(request, db)
    # Prefer chatbot logic if available, else fallback to agent
    try:
        # if get_chatbot_response is async, await it; if not, call directly
        resp = get_chatbot_response(message, db)
        if hasattr(resp, "__await__"):
            ai_response = await resp
        else:
            ai_response = resp
    except Exception:
        ai_response = ask_agentic_ai(message)

    # If the chatbot/agent returned an error string starting with 'Error:', show a friendly message
    if isinstance(ai_response, str) and ai_response.startswith("Error:"):
        friendly = "The AI assistant is not available right now. Please ensure GEMINI_API_KEY is configured."
        return templates.TemplateResponse("chat.html", {"request": request, "ai_response": friendly, "user_message": message, "user": user, "error_detail": ai_response})

    return templates.TemplateResponse("chat.html", {"request": request, "ai_response": ai_response, "user_message": message, "user": user})

# API route for async/JS clients (returns JSON)
@app.post("/api/chat")
async def chat_api(request: Request, message: str = Form(...), db: Session = Depends(get_db)):
    try:
        resp = get_chatbot_response(message, db)
        if hasattr(resp, "__await__"):
            ai_response = await resp
        else:
            ai_response = resp
    except Exception:
        ai_response = ask_agentic_ai(message)
    if isinstance(ai_response, str) and ai_response.startswith("Error:"):
        # Return 503 with a helpful message and the raw detail in a separate field
        return JSONResponse(status_code=503, content={"error": "AI assistant unavailable. Please configure GEMINI_API_KEY.", "detail": ai_response})
    return JSONResponse({"response": ai_response})

# Subscribe user for notifications (updated for authenticated users)
@app.post("/subscribe")
async def subscribe(
    request: Request,
    email: str = Form(...),
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    # Send welcome notification
    send_notification(email, "Welcome!", "You will now receive event notifications from Campus Event Smart Notifier.")
    return {"message": f"Subscribed {email} successfully!"}

# Test endpoint to check if static files are working
@app.get("/test-static")
async def test_static():
    return {"message": "Static files should be accessible at /static/style.css"}


@app.get("/debug/gemini")
async def debug_gemini():
    """Return masked GEMINI_API_KEY presence for debugging."""
    import os
    val = os.getenv("GEMINI_API_KEY")
    if not val:
        return {"gemini_present": False, "value_masked": None}
    v = val.strip('"').strip("'")
    masked = v[:4] + "..." + v[-4:] if len(v) > 8 else "****"
    return {"gemini_present": True, "value_masked": masked}
