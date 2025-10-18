# Campus Event Notifier 2.0 🎉

A modern, AI-powered campus event notification system with user authentication and intelligent chatbot assistance.

## ✨ Features

### 🔐 User Authentication
- Secure user registration and login
- Session-based authentication with JWT
- Protected dashboard for authenticated users
- Password hashing with bcrypt

### 🤖 AI Chatbot Assistant
- OpenAI-powered chatbot for event inquiries
- Context-aware responses about campus events
- Real-time chat interface with modern UI
- Quick question suggestions for common queries

### 🎨 Modern UI/UX
- Responsive design that works on all devices
- Beautiful gradient backgrounds and animations
- Smooth transitions and hover effects
- Professional navigation and layout
- Dark/light theme support

### 📱 Event Management
- Display upcoming campus events
- Smart notification system
- Event categorization and filtering
- Real-time event updates

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for chatbot functionality)
- Gmail account (for email notifications)

### Installation

1. **Clone and Setup**
   ```bash
   cd Campus_event_notifier
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your configuration:
   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   SECRET_KEY=your_super_secret_jwt_key_change_in_production
   EMAIL_USERNAME=your_email@gmail.com
   EMAIL_PASSWORD=your_app_password
   ```

   **Get your free Gemini API key:**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy it to your `.env` file

4. **Database Setup**
   ```bash
   python -c "from database import migrate_events_from_json; migrate_events_from_json()"
   ```

5. **Run the Application**
   ```bash
   python main.py
   ```

6. **Access the Application**
   - Open your browser and go to `http://localhost:8000`
   - Register a new account or login
   - Explore the dashboard and chat with the AI assistant!

## 📁 Project Structure

```
Campus_event_notifier/
├── main.py                 # Main FastAPI application
├── database.py            # Database models and configuration
├── auth.py               # Authentication logic
├── chatbot.py            # AI chatbot implementation
├── notification.py       # Email notification system
├── scheduler.py          # Event scheduling (for future use)
├── requirements.txt      # Python dependencies
├── .env.example         # Environment variables template
├── db.json              # Event data (legacy)
├── subscribers.txt      # Email subscribers (legacy)
├── campus_events.db     # SQLite database (created automatically)
├── TODO.md              # Development progress tracking
├── README.md            # This file
├── static/              # CSS, JS, and other static files
│   └── style.css
└── templates/           # HTML templates
    ├── index.html       # Home page
    ├── login.html      # Login page
    ├── register.html   # Registration page
    ├── dashboard.html  # User dashboard
    └── chat.html       # AI chat interface
```

## 🔧 Configuration

### OpenAI Setup
1. Go to [OpenAI Platform](https://platform.openai.com/)
2. Create an API key
3. Add it to your `.env` file

### Email Setup
1. Enable 2-factor authentication on your Gmail account
2. Generate an [App Password](https://support.google.com/accounts/answer/185833)
3. Use the app password (not your regular password) in the `.env` file

### JWT Secret
- Change the `SECRET_KEY` in `.env` to a secure random string
- Never commit the actual `.env` file to version control

## 🎯 Usage

### For Students
1. **Register**: Create an account with your details
2. **Explore Events**: Browse upcoming campus events on the dashboard
3. **Get Notifications**: Subscribe to receive email alerts
4. **Chat with AI**: Ask questions about events using natural language
5. **Stay Updated**: Get personalized event recommendations

### For Administrators
- Add events to `db.json` or directly to the database
- Monitor user registrations and activity
- Configure notification preferences
- Customize chatbot responses

## 🤖 AI Chatbot Commands

The AI assistant can help with:
- "What events are happening this week?"
- "Tell me about tech events"
- "Show me cultural activities"
- "What's happening tomorrow?"
- "Are there any sports events?"

## 🎨 Customization

### Styling
- Modify `static/style.css` for visual changes
- Responsive design breakpoints are included
- CSS variables can be added for easy theming

### Templates
- Edit HTML templates in the `templates/` directory
- All templates use Jinja2 syntax
- Bootstrap icons are included via CDN

### Adding Events
Events can be added by:
1. Editing `db.json` and running the migration script
2. Directly inserting into the SQLite database
3. Creating an admin interface (future feature)

## 🔒 Security Features

- Password hashing with bcrypt
- JWT-based authentication
- Session management
- Protected routes
- Input validation
- CSRF protection

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers (1200px+)
- Tablets (768px - 1199px)
- Mobile phones (320px - 767px)

## 🚀 Deployment

### Local Development
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Deployment
1. Set environment variables
2. Use a production WSGI server like Gunicorn
3. Set up a reverse proxy (Nginx)
4. Enable HTTPS
5. Configure proper firewall rules

## 🐛 Troubleshooting

### Common Issues

1. **OpenAI API Errors**
   - Check your API key in `.env`
   - Ensure you have sufficient credits
   - Verify internet connection

2. **Email Notifications Not Working**
   - Check Gmail app password
   - Verify SMTP settings
   - Check spam folder

3. **Database Connection Issues**
   - Ensure SQLite database file exists
   - Check file permissions
   - Verify database URL in configuration

4. **Authentication Problems**
   - Clear browser cookies
   - Check JWT secret key
   - Verify password hashing

### Getting Help
- Check the browser console for JavaScript errors
- Review the FastAPI server logs
- Ensure all dependencies are installed correctly

## 📈 Future Enhancements

- [ ] Admin panel for event management
- [ ] Event creation and editing interface
- [ ] User profiles and preferences
- [ ] Social features (event sharing, reviews)
- [ ] Mobile app development
- [ ] Advanced AI features (event recommendations)
- [ ] Integration with calendar applications
- [ ] Multi-language support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI for the GPT API
- FastAPI for the web framework
- Font Awesome for icons
- All contributors and supporters

---

**Made with ❤️ for the campus community**

For questions or support, please contact the development team or create an issue in the repository.
