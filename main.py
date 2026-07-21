import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

app = FastAPI()

# 1. SECURITY: We load the API key from the server's environment variables.
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set")

# Initialize the Mistral client
client = MistralClient(api_key=api_key)

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

class ChatRequest(BaseModel):
    message: str
    history: list = []

@app.post("/chat")
async def chat(request: ChatRequest):
    # Build the message history
    messages = [ChatMessage(role="system", content=SYSTEM_PROMPT)]
    
    for msg in request.history:
        messages.append(ChatMessage(role=msg["role"], content=msg["content"]))
        
    messages.append(ChatMessage(role="user", content=request.message))

    try:
        # Call the Mistral API
        chat_response = client.chat(
            model="open-mistral-nemo",
            messages=messages,
        )
        return {"reply": chat_response.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
