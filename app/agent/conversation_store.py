"""
Stores Gemini conversation history.

Conversation roles are Gemini-native:
    user
    model

The system instruction is kept separately and is NOT stored
as a conversation message.
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

    CONVERSATION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if not CONVERSATION_FILE.exists():
        return []

    try:
        with open(
            CONVERSATION_FILE,
            "r",
            encoding="utf-8",
        ) as f:
            data = json.load(f)

    except (json.JSONDecodeError, ValueError):
        return []

    messages = []

    for message in data:

        parts = []

        for part in message.get("parts", []):

            # Text part
            if "text" in part:

                parts.append(
                    types.Part.from_text(
                        text=part["text"]
                    )
                )

            # Function call
            elif "function_call" in part:

                function_call = part["function_call"]

                parts.append(
                    types.Part(
                        function_call=types.FunctionCall(
                            name=function_call["name"],
                            args=function_call.get("args", {}),
                        )
                    )
                )

            # Function response
            elif "function_response" in part:

                function_response = part["function_response"]

                parts.append(
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=function_response["name"],
                            response=function_response.get(
                                "response",
                                {}
                            ),
                        )
                    )
                )

        messages.append(
            types.Content(
                role=message["role"],
                parts=parts,
            )
        )

    return messages


def save_conversation(messages):
    """Save Gemini Content objects to JSON."""

    CONVERSATION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = []

    for message in messages:

        parts = []

        for part in message.parts:

            # Normal text
            if part.text is not None:

                parts.append({
                    "text": part.text
                })

            # Gemini function call
            elif part.function_call is not None:

                parts.append({
                    "function_call": {
                        "name": part.function_call.name,
                        "args": part.function_call.args,
                    }
                })

            # Gemini function response
            elif part.function_response is not None:

                parts.append({
                    "function_response": {
                        "name": part.function_response.name,
                        "response": part.function_response.response,
                    }
                })

        data.append({
            "role": message.role,
            "parts": parts,
        })

    with open(
        CONVERSATION_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            data,
            f,
            indent=2,
            ensure_ascii=False,
        )
