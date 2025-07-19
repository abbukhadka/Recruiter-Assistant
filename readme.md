# Recruiter Assistant — AI-Powered Resume Screening

Recruiter Assistant is a **Streamlit web app** designed to automate and simplify resume screening for HR professionals and recruiters. Upload resumes in PDF format and provide a job description, and the app will analyze and rank candidates based on **semantic similarity** and **AI summarization** saving you hours of manual screening!

---

## **Features**
- Upload multiple PDF resumes at once  
- Extract text and chunk resumes intelligently  
- Use embeddings (via HuggingFace or Google Gemini) for vector search  
- Store and query resume embeddings in **Pinecone vector database**  
- Find top relevant resumes based on job description similarity  
- Summarize resumes using **Google Gemini generative AI**  
- Display top matched resumes with similarity scores and summaries  
- Built with **Streamlit** for fast and interactive UI  

---


## **Technologies Used**
- **Python 3.8+**
- **Streamlit** (frontend UI)
- **LangChain** (text splitting, embeddings, and chains)
- **Pinecone** (vector database for similarity search)
- **Google Gemini AI** (embeddings & summarization)
- **HuggingFace Embeddings** (optional alternative)
- **PyPDF** (PDF text extraction)
- **dotenv** (manage environment variables)

---

## **Getting Started**

### **Prerequisites**
- Python **3.8 or newer**  
- **Pinecone account & API key**  
- **Google Cloud API key** with access to Gemini (or HuggingFace token if using HF embeddings)  
- **OpenAI API key** (optional, for OpenAI summarization)  

---

## **Installation**

### **1. Clone the repository**


### **2.  Create and activate a Conda environment**
```bash
conda create -n recruiter_assistant python=3.13 -y
conda activate recruiter_assistant
```


### **3. Install dependencies**
Create a ``requirements.txt`` file with the following content:
```bash
langchain
langchain-openai
streamlit
openai
tiktoken
python-dotenv
unstructured
langchain-pinecone
pypdf
sentence_transformers
langchain-huggingface
langchain-google-genai
langchain-community
langchain-core
```


Then run:
```bash
pip install -r requirements.txt
```


### **4. Set up environment variables**
Create a .env file in the root directory:
```bash
OPENAI_API_KEY="your-openai-key"
HUGGINGFACEHUB_API_TOKEN="your-huggingface-token"
PINECONE_API_KEY="your-pinecone-key"
PINECONE_ENV="us-east-1"  # or your Pinecone environment
INDEX_NAME="recruiter"
GOOGLE_API_KEY="your-google-api-key"
```

(You can use .env.example as a template.)

### **Usage**
```bash
streamlit run app.py
```

## **Steps**:

- Paste your Job Description in the text area

- Upload one or more PDF resumes

- Specify how many top resumes you want to see

- Click "Help me with the analysis"

- View ranked resumes with similarity scores and summaries


## **Project Structure**:
```base
.
├── app.py                  # Streamlit frontend app
├── utils.py                # Core utility functions: PDF extraction, embedding, Pinecone, summarization
├── pinecone_emb.py         # Script to create and manage Pinecone index
├── change.py               # Updated utils with Google Gemini embeddings & Pinecone v3
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not committed)
├── .env.example            # Example env file
├── Docs/                   # Folder to store resumes (PDFs)
├── README.md               # This README file
└── test_openai.py          # Simple test script for OpenAI API
```










