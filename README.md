# Clinic FAQ Bot (WhatsApp-style Demo)

A small demo of an FAQ chatbot for a clinic. Patients type questions in a
WhatsApp-style chat, and the bot answers using the clinic's own information,
through Groq's free API.

## How it works

1. **Browser (`templates/index.html`)**: shows a chat screen that looks like
   WhatsApp. When the patient sends a message, the page sends the recent
   conversation to the server.
2. **Server (`app.py`)**: receives the conversation and builds a request for
   Groq. The request contains:
   - **System prompt**: instructions such as "only answer using the clinic
     info", "never diagnose", and "tell emergencies to call emergency services".
   - **Clinic info**: the FAQ text (hours, prices, address, etc.).
   - **Chat history**: the last 10 messages, so follow-up questions make sense.
3. **Groq**: writes a reply based on those instructions. The server sends the
   reply back to the browser, which displays it as a chat bubble.

Think of it like a receptionist who has been handed a clinic information
sheet and told to read only from it.

```
Patient types → index.html → /chat (app.py) → Groq API → reply → chat bubble
```

## Setup

### 1. Get a free Groq API key

Go to https://console.groq.com/keys, create a key, and copy it. It starts
with `gsk_`. Keep it private.

### 2. Create a virtual environment and install packages

**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

**Mac / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Add your API key to `.env`

Create a file named `.env` in the same folder as `app.py`:

```env
GROQ_API_KEY=gsk_paste-your-key-here
```

No quotes, and no spaces around the `=`. The `.env` file is listed in
`.gitignore`, so Git will not upload your key. Never paste the key into
`app.py`, the README, or a chat.

Without a key, the bot runs in demo mode and gives a canned reply.

### 4. Run it

```bash
python app.py
```

Open http://127.0.0.1:5000 in your browser.

## Checking which models your key can use

Groq retires and renames models over time. If you see a `model_not_found`
error, list the models your key can access:

**Windows (PowerShell):**
```powershell
python -c "import os, requests; from dotenv import load_dotenv; load_dotenv(); r = requests.get('https://api.groq.com/openai/v1/models', headers={'Authorization': 'Bearer ' + os.environ['GROQ_API_KEY']}); print(r.status_code); [print(m['id']) for m in r.json().get('data', [])]"
```

**Mac / Linux:**
```bash
curl https://api.groq.com/openai/v1/models -H "Authorization: Bearer $GROQ_API_KEY"
```

Pick a chat model from the list (skip names with `whisper`, `tts`, `guard`,
or `embed`), then set it as `GROQ_MODEL` in `app.py`.

## Customizing for a real clinic

- Replace the text in `CLINIC_INFO` inside `app.py` with your clinic's details.
- Change `CLINIC_NAME` to your clinic's name.
- Edit `SYSTEM_PROMPT` to change the bot's tone or rules.
- Change `GROQ_MODEL` to switch models.

## Troubleshooting

| Problem | Fix |
|---|---|
| Bot says "unavailable" | Check the terminal for a `Groq error` line. A 401 means a bad key. A 404 with `model_not_found` means the model name is out of date; see the section above. |
| Demo mode message appears | `GROQ_API_KEY` is not set in `.env`, or `.env` is not in the same folder as `app.py`. Fix it and restart `app.py`. |
| `NameError: load_dotenv` | Make sure `from dotenv import load_dotenv` and `load_dotenv()` are at the top of `app.py`. |
| `ModuleNotFoundError` | Activate the virtual environment, then run `pip install -r requirements.txt`. |
| Page doesn't load | Make sure the file is at `templates/index.html` (the folder name is exactly `templates`). |
| `.env` shows up in `git status` | Make sure `.gitignore` is in the repo root. If you committed `.env` before, run `git rm --cached .env`, then commit. |

## Limitations

- This is a demo. It is not connected to real WhatsApp.
- To go live on WhatsApp, connect the Twilio WhatsApp Sandbox or the Meta
  WhatsApp Cloud API, and point its webhook at a `/whatsapp` route that calls
  the same `ask_groq()` function.
- The bot is not medical advice. Real clinics should review every answer and
  handle emergencies with staff.
- Free-tier rate limits apply. Heavy use may hit them.