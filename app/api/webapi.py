"""FastAPI app exposing the chat agent over HTTP."""
from fastapi import FastAPI
from pydantic import BaseModel

from app.api.chat import ollama_chat

app = FastAPI()


class ChatRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"reply": "Hello world"}


@app.get("/intro")
def chat_bot_demo():
    """Kept from the original code as a quick manual smoke-test endpoint
    (hardcoded message, GET so you can hit it from a browser)."""
    return {"reply": ollama_chat("Hey")}


@app.post("/chat")
def chat_bot(request: ChatRequest):
    """Real endpoint: POST {"message": "..."} and get the agent's reply.
    Added because a hardcoded GET endpoint isn't usable for a real chatbot."""
    return {"reply": ollama_chat(request.message)}