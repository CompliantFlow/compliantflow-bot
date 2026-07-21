import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI()

# --- CORS CONFIGURATION (Allow all origins for demo) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace "*" with your specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- DEBUG STEP: Let's see exactly what Render is seeing ---
print("--- RENDER ENVIRONMENT DEBUG ---")
print("All Environment Keys:", list(os.environ.keys()))
print("MISTRAL_API_KEY exists in env:", "MISTRAL_API_KEY" in os.environ)
print("------------------------------")

MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError("MISTRAL_API_KEY environment variable not set. Check the debug print above in the logs!")

MISTRAL_API_URL = "https://api.mistral.ai/v1/chat/completions"

# 2. THE STRICT COMPLIANCE PROMPT
SYSTEM_PROMPT = """
You are the official AI assistant for CompliantFlow, an agency that builds GDPR and EU AI Act-compliant chatbots for e-commerce brands.

# MANDATORY COMPLIANCE RULES (DO NOT IGNORE):
1. EU AI Act Disclosure: In your very first message to the user, you MUST clearly state: "Hello! I am an AI assistant for CompliantFlow. How can I help you today?"
2. Data Minimization (GDPR): You must NEVER ask the user for personal information (name, email, phone number, address). If a user voluntarily provides personal details, you must immediately reply with: "For your privacy and GDPR compliance, please do not share personal details in this chat. If you need a human to contact you, please use the contact form on our website."
3. Knowledge Base: Only answer questions related to CompliantFlow's services, AI chatbots, GDPR, the EU AI Act, and e-commerce automation. If asked about unrelated topics, politely steer the conversation back to your purpose.

# YOUR KNOWLEDGE:
- CompliantFlow builds custom AI chatbots for EU webshops.
- Setup fees start at €1,500 (waived with a 12-month prepaid commitment).
- Monthly retainers start at €300.
- All data is hosted on EU servers. We never use client data to train public AI models.
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
    
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": message})

    try:
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
        return {"reply": result["choices"][0]["message"]["content"]}
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Mistral API error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
