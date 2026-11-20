import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template

load_dotenv()
app = Flask(__name__)

# ---- Settings ----
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_MODEL = "openai/gpt-oss-120b"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

CLINIC_NAME = "Sunrise Family Clinic"

# ---- The clinic's FAQ knowledge ----
CLINIC_INFO = """
Clinic name: Family Clinic
Address: 12 Nile Street, Egypt
Phone: +20 100 000 0000
Opening hours: Saturday to Thursday 9:00 AM to 9:00 PM. Friday 4:00 PM to 9:00 PM.
Services: General medicine, pediatrics, dental cleaning, blood and urine lab tests, vaccinations.
Booking: Reply with your name, preferred day, and the service you need, or call the phone number.
Prices: General medicine consultation 300 EGP. Pediatric consultation 250 EGP. Dental cleaning 400 EGP.
Lab results: Ready within 24 hours. Collect them at reception.
Cancellation: Please cancel at least 3 hours before your appointment.
Insurance: We accept Allianz and AXA. Please bring your insurance card.
"""

SYSTEM_PROMPT = f"""
You are the WhatsApp assistant for {CLINIC_NAME}.
Answer ONLY using the clinic information below.
If the answer is not in the information, say you don't know and suggest calling the clinic.
Never diagnose illnesses or recommend medicines.
If the user describes an emergency (chest pain, trouble breathing, heavy bleeding,
unconsciousness, etc.), tell them to call emergency services immediately.
Keep replies short, friendly, and under 60 words.
Reply in the same language the user writes in (English or Arabic).

CLINIC INFORMATION:
{CLINIC_INFO}
"""


def ask_groq(history):
    # Demo mode: works without a key so you can test the UI
    if not GROQ_API_KEY:
        return ("(Demo mode: no API key set. Our clinic is open "
                "Saturday to Thursday, 9 AM to 9 PM.)")

    # Groq uses the OpenAI format: system prompt first, then the chat
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        role = "assistant" if msg["role"] == "bot" else "user"
        messages.append({"role": role, "content": msg["text"]})

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    body = {
        "model": GROQ_MODEL,
        "messages": messages,
        "temperature": 0.3,  # lower = more consistent, factual answers
    }

    try:
        resp = requests.post(GROQ_URL, headers=headers, json=body, timeout=30)
    except requests.RequestException:
        return "Sorry, I can't reach the assistant right now. Please try again."

    if resp.status_code != 200:
        print("Groq error:", resp.status_code, resp.text)
        return "Sorry, the assistant is unavailable right now. Please call the clinic."

    try:
        return resp.json()["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError):
        return "Sorry, I couldn't come up with an answer. Please call the clinic."

@app.route("/")
def index():
    return render_template("index.html", clinic=CLINIC_NAME)


@app.route("/chat", methods=["POST"])
def chat():
    history = (request.get_json() or {}).get("history", [])[-10:]  # keep last 10 messages
    if not history or history[-1]["role"] != "user" or not history[-1]["text"].strip():
        return jsonify(error="Send a message first."), 400
    return jsonify(reply=ask_groq(history))


if __name__ == "__main__":
    app.run(debug=True)