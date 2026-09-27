"""
Core chat loop: sends the conversation + tools to Ollama, and if the model
requests a tool call, runs it locally and feeds the result back in before
asking the model again - repeating until it gives a final text answer with
no more tool calls.
"""
import json
import ollama 
from app.agent.conversation_store import load_conversation, save_conversation
from app.agent.tools import get_product_info, add_order, get_products, AVAILABLE_TOOLS

LOCAL_MODEL_NAME = "fredrezones55/Gemma-4-Uncensored-HauhauCS-Aggressive:e4b"

def ollama_chat(user_input: str) -> str:    #For running llm locally
    messages = load_conversation()
    messages.append({"role": "user", "content": user_input})

    while True:
        response = ollama.chat(
            model=LOCAL_MODEL_NAME,
            messages=messages,
            think=False,
            tools=[get_product_info,
                   add_order,
                   get_products],
            options={"num_ctx": 8000},
        )
        messages.append(response.message.model_dump())

        if response.message.tool_calls:
            for call in response.message.tool_calls:
                tool_name = call.function.name
                arguments = call.function.arguments

                tool_function = AVAILABLE_TOOLS.get(tool_name)
                if tool_function is None:
                    result = json.dumps({"error": f"Unknown tool '{tool_name}'"})
                else:
                    try:
                        result = tool_function(**arguments)
                    except Exception as exc:
                        result = json.dumps({"error": str(exc)})

                messages.append(
                    {
                        "role": "tool",
                        "tool_name": tool_name,
                        "content": json.dumps(result),
                    }
                )
            continue
        save_conversation(messages)
        return response.message.content