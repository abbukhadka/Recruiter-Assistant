from pinecone import Pinecone
import os

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "recruiter"

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=PINECONE_API_KEY)

# ✅ List indexes
print(pc.list_indexes())

# ✅ Delete index if exists
if INDEX_NAME in [index["name"] for index in pc.list_indexes()]:
    pc.delete_index(INDEX_NAME)

# ✅ Create new index (Gemini 768-dim)
pc.create_index(
    name=INDEX_NAME,
    dimension=768,
    metric="cosine"
)
