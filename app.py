from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import requests
import os

load_dotenv()

app = Flask(__name__, static_folder="static")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("OpenRouter API key not found. Check your .env file")

conversation_history = []

@app.route("/")
def index():
    return send_from_directory("static", "index.html")

@app.route("/chat", methods=["POST"])
def chat():
    global conversation_history

    data = request.get_json()
    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"response": "Empty message"}), 400

    conversation_history.append({
        "role": "user",
        "content": user_message
    })

    messages = conversation_history[-6:]

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "http://localhost:5000",
                "X-Title": "MiniChatAI"
            },
            json={
                "model": "google/gemma-3-27b-it:free",
                "messages": messages
            },
            timeout=30
        )

        if response.status_code == 429:
            return jsonify({
                "response": "Rate limit reached. Please wait a minute and try again."
            })

        if response.status_code != 200:
            print(f"OpenRouter Error {response.status_code}: {response.text}") 
            return jsonify({
                "response": "AI service error. Try again later."
         })

        result = response.json()

        if "choices" in result:
            ai_reply = result["choices"][0]["message"]["content"]
        else:
            ai_reply = "Error: Unable to get response from AI."

        conversation_history.append({
            "role": "assistant",
            "content": ai_reply
        })

        return jsonify({"response": ai_reply})

    except requests.exceptions.Timeout:
        return jsonify({
            "response": "The AI is taking too long to respond. Please try again."
        })

    except Exception as e:
        return jsonify({
            "response": "Unexpected server error."
        })

@app.route("/reset", methods=["POST"])
def reset():
    global conversation_history
    conversation_history = []
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)