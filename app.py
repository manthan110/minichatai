from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import requests
import os
from tavily import TavilyClient

load_dotenv()

app = Flask(__name__, static_folder="static")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("Groq API key not found. Check your .env file")

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
if not TAVILY_API_KEY:
    print("Warning: TAVILY_API_KEY not found in .env")

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

    api_messages = conversation_history[-6:] 
    
    search_triggers = ["today", "weather", "current", "latest", "news", "price", "who won"]
    needs_search = any(trigger in user_message.lower() for trigger in search_triggers)

    search_results = ""

    if needs_search:
        print("🔍 Web search triggered...") 
        try:
            tavily = TavilyClient(api_key=TAVILY_API_KEY)
            response = tavily.search(query=user_message, search_depth="basic", max_results=3)
            
            for res in response.get('results', []):
                search_results += f"Source: {res['title']}\nInfo: {res['content']}\n\n"
        except Exception as e:
            print(f"Tavily Search failed: {e}")
    else:
        print("⚡ Skipping web search to save credits.")

    augmented_prompt = f"""
    You are MiniChatAI. Use the following real-time web search results to answer the user's query if they are relevant. If not, just answer normally.
    
    Web Search Results:
    {search_results}
    
    User Query: {user_message}
    """
    
    api_messages[-1]["content"] = augmented_prompt

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.3-70b-versatile",
                "messages": api_messages
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