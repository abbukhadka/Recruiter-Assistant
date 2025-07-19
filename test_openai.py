from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

try:
    models = client.models.list()
    print("✅ Key works! Models available:", len(models.data))
except Exception as e:
    print("❌ Key invalid:", e)
