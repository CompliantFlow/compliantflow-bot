import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# --- CORS CONFIGURATION ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows your GitHub Pages demo to talk to this API
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENVIRONMENT VARIABLES ---
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")
if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable not set")

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# --- THE STRICT COMPLIANCE PROMPT ---
SYSTEM_PROMPT = """
You are the official AI assistant for CompliantFlow, an agency that builds GDPR and EU AI Act-compliant chatbots for e-commerce brands.

# STRICT BEHAVIORAL RULES:
1. NO REPETITIVE GREETINGS: You have already introduced yourself to the user. NEVER start your responses with "Hello! I am an AI assistant..." or any similar greeting. Just answer the question directly and professionally.
2. OUT OF SCOPE RESPONSES: If a user asks a question that is NOT related to CompliantFlow's services, AI chatbots, GDPR, the EU AI Act, or e-commerce automation, you must reply with EXACTLY this: "I'm sorry, I am only trained to answer questions about CompliantFlow's chatbot services, GDPR compliance, and e-commerce automation. Is there anything related to those topics I can help you with?"
3. Data Minimization (GDPR): You must NEVER ask the user for personal information (name, email, phone number, address). If a user voluntarily provides personal details, you must immediately reply with: "For your privacy and GDPR compliance, please do not share personal details in this chat. If you need a human to contact you, please use the contact form on our website."
4. AI LABELING: All your responses will be automatically labeled as "AI Generated" by the frontend system.

# YOUR KNOWLEDGE:
- CompliantFlow builds custom AI chatbots for EU webshops.
- Setup fees start at €1,500 (waived with a 12-month prepaid commitment).
- Monthly retainers start at €300.
- All data is hosted on EU servers (Frankfurt, Germany). We never use client data to train public AI models.
"""

@app.get("/")
def root():
    return {"status": "CompliantFlow API is live and running!"}

@app.post("/chat")
async def chat(request: Request):
    try:
        data = await request.json()
        message = data.get("message", "")
        history = data.get("history", [])
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request format: {str(e)}")
    
    # Build the message history for the AI
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
        # Call the Mistral API directly via HTTP
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {MISTRAL_API_KEY}"
        }
        payload = {
            "model": "open-mistral-nemo",
            "messages": messages,
            "temperature": 0.7
        }
        
        response = requests.post(MISTRAL_API_URL, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        
        return {"reply": reply}
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Mistral API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
