import streamlit as st
import uuid
import asyncio
from langchain_core.documents import Document
import streamlit.components.v1 as components

# These are mock functions for demonstration. Replace them with your actual utils.
def create_documents(files, session_id):
    docs = []
    for file in files:
        docs.append(Document(page_content=f"Content of {file.name}", metadata={"name": file.name, "source": file.name, "unique_id": session_id}))
    return docs

def push_to_pinecone(docs):
    st.session_state['mock_db'] = docs
    pass

def query_similar(query, count, session_id):
    mock_db = st.session_state.get('mock_db', [])
    relevant_docs = [doc for doc in mock_db if doc.metadata.get("unique_id") == session_id]
    results = []
    if relevant_docs:
        for i in range(count * 5):
            doc = relevant_docs[i % len(relevant_docs)]
            results.append((doc, 0.95 - i*0.015))
    return results[:count*5]

def summarize_docs(doc):
    return f"This is a brief summary of the key skills and experiences found in the resume for {doc.metadata.get('name', 'Unknown')}."

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

def apply_styling():
    """
    Injects CSS for general styling, including a definitive fix for notification text color.
    """
    st.markdown("""
        <style>
            /* Base styles for background and default text */
            [data-testid="stAppViewContainer"] {
                background-color: #F0F2F6;
                color: #212529;
            }
            
            /* Headers and Labels */
            h1, h2, h3, label[data-baseweb="form-control-label"] {
                font-family: 'Verdana', sans-serif;
                color: #212529;
            }
            h1 { font-weight: 700; color: #1E2A3A; }

            /* Inline code blocks */
            code {
                color: #D93B6A;
                background-color: #FCE4EC;
                padding: 3px 5px;
                border-radius: 4px;
            }
            
    


            /* Button styling */
            div.stButton > button {
                background-color: #D93B6A;
                color: white !important;
                border-radius: 25px;
                border: 2px solid #C2335D;
                padding: 10px 24px;
                font-weight: bold;
                transition: all 0.3s ease;
            }
            div.stButton > button:hover {
                background-color: #C2335D;
            }
        </style>
    """, unsafe_allow_html=True)

    # 2. JavaScript to find and fix notification text color
    # This script watches for pop-up notifications and forces their text to be black.
    js_code = """
    <script>
    const forceBlackText = (element) => {
        // Find the specific inner div that contains the text content.
        const textElement = element.querySelector('div[data-baseweb="notification"] div[role="alert"] div');
        if (textElement) {
            textElement.style.color = 'black';
        }
    };

    const observer = new MutationObserver((mutations) => {
        mutations.forEach(mutation => {
            mutation.addedNodes.forEach(node => {
                if (node.nodeType === 1 && node.hasAttribute('data-testid') && node.getAttribute('data-testid') === 'stNotification') {
                    forceBlackText(node);
                }
            });
        });
    });

    observer.observe(document.body, { childList: true, subtree: true });

    // Also apply to any notifications that might already be on the page
    document.querySelectorAll('[data-testid="stNotification"]').forEach(forceBlackText);
    </script>
    """
    components.html(js_code, height=0)


def main():
    st.set_page_config(
        page_title="Recruiter Assistant",
        page_icon="🤖",
        layout="centered"
    )
    # Apply all styling (CSS and JavaScript fix)
    apply_styling()

    st.image("aqore_logo.png", width=120)
    st.title("Recruiter Assistant - Resume Screening Assistance")
    st.subheader("Upload resumes and I’ll help you shortlist the best candidates.")

    job_description = st.text_area("Enter the JOB DESCRIPTION here:", key="job_desc")
    document_count = st.number_input("Number of resumes to return:", min_value=1, max_value=50, value=5, step=1)
    pdf_files = st.file_uploader("Upload resumes (PDF only):", type=["pdf"], accept_multiple_files=True)

    if st.button("Help me with the analysis"):
        if not job_description.strip():
            st.error("Please paste the job description.")
            return
        if not pdf_files:
            st.error("Please upload at least one resume (PDF).")
            return

        st.session_state["unique_id"] = uuid.uuid4().hex
        st.info(f"Session ID: `{st.session_state['unique_id']}`")

        with st.spinner("⏳ Processing resumes..."):
            docs = create_documents(pdf_files, st.session_state["unique_id"])
            st.write(f"**Resumes processed**: {len(pdf_files)}")
            
            push_to_pinecone(docs)
            st.success("Resumes have been added to the database.")
            
            results = query_similar(job_description, int(document_count), st.session_state["unique_id"])

        if not results:
            st.warning("No relevant resumes found.")
            return

        results.sort(key=lambda x: x[1], reverse=True)
        top_resumes = {}
        for doc, score in results:
            resume_name = doc.metadata.get("name", "Unknown Resume")
            if resume_name not in top_resumes:
                top_resumes[resume_name] = (doc, score)
            if len(top_resumes) >= int(document_count):
                break

        st.write("---")
        st.header(f"Top {len(top_resumes)} Relevant Resumes")

        for idx, (resume_name, (top_doc, score)) in enumerate(top_resumes.items(), start=1):
            st.subheader(f"{idx}. {resume_name}")
            st.write(f"**Best Similarity Score:** `{score:.4f}`")
            with st.expander("Show summary 👀"):
                summary = summarize_docs(top_doc)
                st.write(f"**Summary**:\n{summary}")
        
        st.success("Done! Hope this saved you hours of screening work.")

if __name__ == "__main__":
    if "unique_id" not in st.session_state:
        st.session_state = {}
    main()