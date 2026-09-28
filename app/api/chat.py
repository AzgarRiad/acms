"""
Core Gemini chat loop.

Sends the conversation + tools to Gemini. If Gemini requests a tool call,
the tool is executed locally and the result is sent back to Gemini.

This repeats until Gemini returns a final text response.
"""

from google import genai
from google.genai import types
import os
from dotenv import load_dotenv

load_dotenv()

from app.agent.conversation_store import load_conversation, save_conversation
from app.agent.tools import (
    get_product_info,
    add_order,
    get_products,
    AVAILABLE_TOOLS,
)


GEMINI_MODEL_NAME = "gemini-3.5-flash-lite"

client = genai.Client(api_key=os.getenv("GENAI_API_KEY"))
#client = genai.Client(api_key="AQ.Ab8RN6LKMr1vQMZBeO3hwb61P38Oqb9sV-9d--pxjWgCMPgTU")

def gemini_chat(user_input: str) -> str:

    messages = load_conversation()

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
                    client=client,
                    callable=get_product_info,
                ),
                types.FunctionDeclaration.from_callable(
                    client=client,
                    callable=add_order,
                ),
                types.FunctionDeclaration.from_callable(
                    client=client,
                    callable=get_products,
                ),
            ]
        )
    ]

    config = types.GenerateContentConfig(
        system_instruction=(
            """You are a helpful assistant for a store.
            When the user asks about a product's price or availability,
            call the get_product_info tool instead of guessing, prices are in BDT.
            Carefully place the order, ask user name, product quantity so that the backend system can handle orders"""
        ),
        tools=tools,

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

        messages.append(response.candidates[0].content)

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
                    )
                )

            messages.append(
                types.Content(
                    role="user",
                    parts=function_response_parts,
                )
            )

            continue

        save_conversation(messages)

        return response.text

