# Campus Event Notifier — Gemini setup

This project uses Google Gemini (via `google-generativeai`) as the AI provider.

If you want the chat/agent features to work, set a valid `GEMINI_API_KEY` in one of the following ways:

1) Preferred: Put it into the root `.env` file (project root: `./.env`) as a plain value (no surrounding quotes):

GEMINI_API_KEY=your_real_api_key_here

Example (PowerShell session only):

$env:GEMINI_API_KEY="ya29.A0ARrdaM..."

Example (persist across sessions using `setx`, then open a new PowerShell window):

setx GEMINI_API_KEY "ya29.A0ARrdaM..."

2) Alternative: Edit the root `.env` file directly. Open `./.env` and add or replace the line:

GEMINI_API_KEY=your_real_api_key_here

Important notes:
- Do NOT put extra surrounding double-quotes in the value. The app strips quotes, but it's clearer to avoid them.
- There are two `.env` files in the workspace:
  - `./.env` (project root) — recommended place for your key
  - `Campus_event_notifier/.env` (package) — should not contain an empty `GEMINI_API_KEY=` line. If it does, it may mask a root key during some loads. We've commented out the empty line in the package `.env` to avoid confusion.

Testing the running server

After setting the key (or editing `.env`) you can verify what the running process sees:

# Check the debug endpoint (returns masked key)
curl http://127.0.0.1:8000/debug/gemini

# Test chat API (sends a form field `message`)
curl -X POST -F "message=Hello" http://127.0.0.1:8000/api/chat

If you see errors like "API key not valid" from the Gemini SDK, the key is incorrect or revoked. Double-check you've pasted the correct key and that it has the right permissions.

If you prefer I can (with your go-ahead):
- Remove or rename the package `.env` entirely
- Add an interactive test that validates the key without invoking a full chat

