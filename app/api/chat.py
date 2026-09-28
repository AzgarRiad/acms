"""
Core Gemini chat loop.

Sends the conversation + tools to Gemini. If Gemini requests a tool call,
the tool is executed locally and the result is sent back to Gemini.
This repeats until Gemini returns a final text response.
"""

from google import genai
from google.genai import types

from app.agent.conversation_store import load_conversation, save_conversation
from app.agent.tools import (
    get_product_info,
    add_order,
    get_products,
    AVAILABLE_TOOLS,
)


GEMINI_MODEL_NAME = "gemini-2.5-flash"

client = genai.Client()


def gemini_chat(user_input: str) -> str:
    messages = load_conversation()

    # Add new user message using Gemini's native role structure
    messages.append(
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=user_input)
            ],
        )
    )

    tools = [
        types.Tool(
            function_declarations=[
                types.FunctionDeclaration.from_callable(
                    callable=get_product_info
                ),
                types.FunctionDeclaration.from_callable(
                    callable=add_order
                ),
                types.FunctionDeclaration.from_callable(
                    callable=get_products
                ),
            ]
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=(
            """You are a helpful assistant for a store.
            When the user asks about a product's price or availability,
            call the get_product_info tool instead of guessing."""
        ),
        tools=tools,

        # We execute tools ourselves.
        automatic_function_calling=types.AutomaticFunctionCallingConfig(
            disable=True
        ),
    )

    while True:
        response = client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=messages,
            config=config,
        )

        # Store Gemini's complete model response.
        messages.append(response.candidates[0].content)

        # Check for tool calls
        if response.function_calls:

            function_response_parts = []

            for call in response.function_calls:

                tool_name = call.name
                arguments = call.args

                tool_function = AVAILABLE_TOOLS.get(tool_name)

                if tool_function is None:
                    result = {
                        "error": f"Unknown tool '{tool_name}'"
                    }

                else:
                    try:
                        result = tool_function(**arguments)

                    except Exception as exc:
                        result = {
                            "error": str(exc)
                        }

                function_response_parts.append(
                    types.Part.from_function_response(
                        name=tool_name,
                        response={
                            "result": result
                        },
                        id=call.id,
                    )
                )

            # Gemini function responses are sent as a user Content.
            messages.append(
                types.Content(
                    role="user",
                    parts=function_response_parts,
                )
            )

            continue

        # No tool calls -> final answer
        save_conversation(messages)

        return response.text