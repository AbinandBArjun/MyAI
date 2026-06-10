from app.services.chat_service import ask_llm

response = ask_llm("What is FastAPI?")

print(response)