from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow all connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "Server is awake and running!"}

@app.post("/chat")
def chat():
    # This is a fake response just to test the connection
    return {"reply": "Success! Your frontend is talking to your backend."}
