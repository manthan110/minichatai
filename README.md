# MiniChatAI - Context-Aware Full-Stack AI Assistant

## 📌 Project Abstract
MiniChatAI is a highly responsive, full-stack conversational AI application designed to provide intelligent, real-time assistance. It features a custom Retrieval-Augmented Generation (RAG) pipeline that dynamically fetches live web data to augment the AI's knowledge base. The application actively maintains conversational context and renders complex technical outputs natively, ensuring a seamless user experience for both general inquiries and complex developer tasks.

## Key Features
* **Intelligent Web Search (RAG):** Employs keyword-based intent routing to trigger the Tavily Search API, fetching real-time facts only when necessary to conserve API credits.
* **Dynamic UI Rendering:** Intercepts raw Markdown from the LLM and compiles it into styled HTML, featuring readable tables, lists, and color-coded code blocks (Tokyo Night Dark theme).
* **Contextual Memory:** The backend actively manages dialogue history arrays, enabling the AI to retain conversational context across multiple interactions without token-limit bloat.
* **Robust Error Handling:** Safely catches API timeouts and rate-limit exceptions, gracefully passing structured, user-friendly error messages to the frontend UI.

## 🛠️ Technology Stack
* **Frontend:** HTML5, CSS3, Vanilla JavaScript, `marked.js` (Markdown parsing), `highlight.js` (Syntax highlighting)
* **Backend:** Python, Flask (REST API routing), `python-dotenv` (Environment management)
* **AI & APIs:** Groq API (Inference Engine), `LLaMA-3.3-70b-versatile` (Core LLM), Tavily Search API (Real-time Web Search)
