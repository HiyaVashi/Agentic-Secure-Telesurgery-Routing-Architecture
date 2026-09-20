# from langchain_google_genai import ChatGoogleGenerativeAI
# from config import GOOGLE_API_KEY

# def get_gemini_llm():
#     return ChatGoogleGenerativeAI(
#         model="gemini-3.5-flash",
#         google_api_key=GOOGLE_API_KEY,
#         temperature=0.2,
#     )

# def get_llm():
#     return get_gemini_llm()

from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

load_dotenv()

def get_llm():
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        api_key=os.getenv("GROQ_API_KEY"),
        temperature=0.2
    )