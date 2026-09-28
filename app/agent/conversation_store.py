"""
Stores Gemini conversation history.

The conversation contains only Gemini-compatible roles:
    user
    model

System instruction is kept separately.
"""

import json
from pathlib import Path

from google.genai import types


BASE_DIR = Path(__file__).resolve().parent.parent.parent

CONVERSATION_FILE = BASE_DIR / "data" / "conversation.json"


SYSTEM_INSTRUCTION = """You are a helpful assistant for a store.
When the user asks about a product's price or availability,
call the get_product_info tool instead of guessing."""


def load_conversation():
    """Load conversation history as Gemini Content objects."""

    CONVERSATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not CONVERSATION_FILE.exists():
        return []

    try:
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

    except (json.JSONDecodeError, ValueError):
        return []

    messages = []

    for message in data:
        messages.append(
            types.Content(
                role=message["role"],
                parts=[
                    types.Part.from_text(
                        text=part["text"]
                    )
                    for part in message["parts"]
                    if "text" in part
                ],
            )
        )

    return messages


def save_conversation(messages):
    """Save Gemini Content objects to JSON."""

    CONVERSATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    data = []

    for message in messages:

        parts = []

        for part in message.parts:

            if part.text is not None:
                parts.append({
                    "text": part.text
                })

            elif part.function_call is not None:
                parts.append({
                    "function_call": {
                        "name": part.function_call.name,
                        "args": part.function_call.args,
                        "id": part.function_call.id,
                    }
                })

            elif part.function_response is not None:
                parts.append({
                    "function_response": {
                        "name": part.function_response.name,
                        "response": part.function_response.response,
                        "id": part.function_response.id,
                    }
                })

        data.append({
            "role": message.role,
            "parts": parts,
        })

    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)