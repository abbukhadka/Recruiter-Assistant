import os
import uuid
import asyncio
from typing import List
from dotenv import load_dotenv
from pypdf import PdfReader

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain.chains.summarize import load_summarize_chain

from pinecone import Pinecone as PineconeClient
from langchain_pinecone import PineconeVectorStore

# Load environment variables
load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
INDEX_NAME = os.getenv("PINECONE_INDEX", "recruiter")

# Initialize Pinecone
pc = PineconeClient(api_key=PINECONE_API_KEY)


# --------- PDF → Text ---------
def extract_pdf_text(pdf_file) -> str:
    reader = PdfReader(pdf_file)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


# --------- Build Documents with Chunking ---------
def create_documents(pdf_files: List, unique_id: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    docs = []
    for pdf in pdf_files:
        text = extract_pdf_text(pdf)
        for chunk in splitter.split_text(text):
            docs.append(Document(
                page_content=chunk,
                metadata={
                    "name": getattr(pdf, "name", "uploaded_resume.pdf"),
                    "size": getattr(pdf, "size", None),
                    "unique_id": unique_id
                }
            ))
    return docs


# --------- Embeddings (consistent for push & query) ---------
def get_embeddings():
    return HuggingFaceEmbeddings(model_name="BAAI/bge-large-en-v1.5")
    # Or switch to Gemini:
    # return GoogleGenerativeAIEmbeddings(model="models/embedding-001", api_key=GOOGLE_API_KEY)


# --------- Initialize Vector Store ---------
def get_vectorstore() -> PineconeVectorStore:
    return PineconeVectorStore.from_existing_index(
        index_name=INDEX_NAME,
        embedding=get_embeddings()
    )


# --------- Push Documents to Pinecone ---------
def push_to_pinecone(docs: List[Document]):
    vectorstore = get_vectorstore()

    #  Debug before pushing
    print(f"✅ Pushing {len(docs)} documents...")
    for d in docs[:3]:
        print("📄", d.metadata)

    vectorstore.add_documents(docs)
    print("✅ Documents successfully pushed to Pinecone.")


# --------- Query Similar Documents ---------
def query_similar(query: str, k: int, unique_id: str):
    vectorstore = get_vectorstore()
    results = vectorstore.similarity_search_with_score(
        query,
        k=k,
        filter={"unique_id": unique_id}
    )

    if not results:
        print("⚠️ No results found. Check unique_id or embeddings.")
    else:
        print(f" Found {len(results)} similar docs:")
        for doc, score in results:
            print(f" - {doc.metadata['name']} | score={score}")

    return results


# --------- Summarization ---------
def summarize_docs(current_doc: Document) -> str:
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0,
        max_output_tokens=1024,
        api_key=GOOGLE_API_KEY
    )
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    async def run_chain():
        return await chain.arun([current_doc])

    return asyncio.run(run_chain())