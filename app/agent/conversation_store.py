"""
Handles loading and saving the conversation history to a local JSON file.
Creates the data directory / file with a default system prompt the first
time the app runs, so nothing crashes on a fresh checkout.
"""
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
CONVERSATION_FILE = BASE_DIR / "data" / "conversation.json"

DEFAULT_SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        """You are a helpful assistant for a store.
        When the user asks about a product's price or availability, 
        call the get_product_info tool instead of guessing."""
    ),
}


def load_conversation():
    """Load conversation history, creating a fresh one with a system
    prompt if the file doesn't exist yet or is empty/corrupted."""
    CONVERSATION_FILE.parent.mkdir(parents=True, exist_ok=True)

    if not CONVERSATION_FILE.exists():
        conversation = [DEFAULT_SYSTEM_PROMPT.copy()]
        save_conversation(conversation)
        return conversation

    try:
        with open(CONVERSATION_FILE, "r", encoding="utf-8") as f:
            conversation = json.load(f)
    except (json.JSONDecodeError, ValueError):
        conversation = [DEFAULT_SYSTEM_PROMPT.copy()]

    if not conversation or conversation[0].get("role") != "system":
        conversation.insert(0, DEFAULT_SYSTEM_PROMPT.copy())

    return conversation


def save_conversation(conversation):
    """Persist the conversation list to disk as JSON."""
    CONVERSATION_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONVERSATION_FILE, "w", encoding="utf-8") as f:
        json.dump(conversation, f, indent=2)
