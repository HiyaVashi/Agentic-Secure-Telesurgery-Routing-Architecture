from models.ollama import get_llm

llm = get_llm()

response = llm.invoke("Introduce yourself in one sentence.")

print(response.content)