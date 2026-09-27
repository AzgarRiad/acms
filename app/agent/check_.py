from app.api.chat import ollama_chat
def main(user_input = "What is the price of RTX 5070 ti?"):
    response = ollama_chat(user_input=user_input)
    print(response)

if __name__ == "__main__":
    main()