from ai_client import ask_ai
 
prompt = "Geef me 3 virale video ideeën voor YouTube."
 
result = ask_ai(prompt, "openai")
 
print("\n=== AI TEST RESULTAAT ===\n")
print(result)