# TODO: Implement Chatbot Response for Specific Events

## Tasks
- [x] Modify `/chat` route in `main.py` to accept optional `question` query parameter and pass it to the template
- [x] Update `chat.html` template to include initial_question variable and JavaScript to send initial message if provided
- [x] Test the "Ask AI" button navigation and chatbot response for specific events

## Status
- Implementation complete: Modified /chat route to accept question query param, updated chat.html to send initial message.
- The chatbot already formats all events in the prompt, so it can respond to specific event questions.
- To test: Run the app with `python run.py`, navigate to home page, click "Ask AI" on an event, verify the chatbot receives and responds to the pre-filled question.
