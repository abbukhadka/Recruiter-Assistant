import streamlit as st
import uuid
from utils import create_documents, push_to_pinecone, query_similar, summarize_docs
import asyncio

################
import torch
##################


############################################################
from collections import defaultdict

def aggregate_resume_scores(results):
    grouped_scores = defaultdict(list)
    for doc, score in results:
        resume_name = doc.metadata.get("name", "Unknown Resume")
        grouped_scores[resume_name].append(score)

    aggregates = {}
    for resume, scores in grouped_scores.items():
        avg_score = sum(scores) / len(scores)
        aggregates[resume] = avg_score
    return aggregates

#####################################################################

try:
    asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


def main():
    st.set_page_config(page_title="Recruiter Assistant", page_icon="Recruiter Assistant")
    st.title(" Recruiter Assistant - Resume Screening Assistance")
    st.subheader("Upload resumes and I’ll help you shortlist the best candidates.")

    # --- Input Section ---
    job_description = st.text_area(" Enter the JOB DESCRIPTION here:", key="job_desc")
    document_count = st.number_input(" Number of resumes to return:", min_value=1, max_value=50, value=5, step=1)
    pdf_files = st.file_uploader("Upload resumes (PDF only):", type=["pdf"], accept_multiple_files=True)

    if st.button("Help me with the analysis"):
        if not job_description.strip():
            st.error(" Please paste the job description.")
            return
        if not pdf_files:
            st.error(" Please upload at least one resume (PDF).")
            return

        # --- Start Processing ---
        st.session_state["unique_id"] = uuid.uuid4().hex
        st.info(f"Session ID: `{st.session_state['unique_id']}`")

        with st.spinner("⏳ Processing resumes..."):
            # 1. Convert PDFs to chunked documents
            docs = create_documents(pdf_files, st.session_state["unique_id"])
            st.write(f" **Resumes processed**: {len(pdf_files)}")

            # 2. Push documents to Pinecone
            push_to_pinecone(docs)

            ###########################
            torch.mps.empty_cache()
            #################################
            st.success(" Resumes have been added to the database.")

            # 3. Query similar resumes


            ########################################################################################

        #     results = query_similar(job_description, int(document_count), st.session_state["unique_id"])

        # if not results:
        #     st.warning(" No relevant resumes found.")
        #     return

        # # --- Display Results ---
        # st.write("---")
        # st.write(f"###  Top {len(results)} Relevant Resumes")
        # for idx, (doc, score) in enumerate(results, start=1):
        #     st.subheader(f" {idx}. {doc.metadata.get('name', 'Unknown')}")
        #     with st.expander("Show details "):
        #         st.write(f"**Similarity Score**: `{score:.4f}`")
        #         #summary = summarize_docs([doc])[0]
        #         summary = summarize_docs(doc)
        #         st.write(f"**Summary**:\n{summary}")



        ################################################################  

            #results = query_similar(job_description, int(document_count), st.session_state["unique_id"])
            results = query_similar(job_description, int(document_count) * 5, st.session_state["unique_id"])


            ###############################################

            torch.mps.empty_cache()

            ##############################################

        # if not results:
        #     st.warning(" No relevant resumes found.")
        #     return

        # # Calculate average similarity score per resume
        # resume_scores = aggregate_resume_scores(results)

        # st.write("---")
        # st.write(f"###  Similarity Scores for all matched resumes")

        # # Sort resumes by similarity score
        # sorted_resumes = sorted(resume_scores.items(), key=lambda x: x[1], reverse=True)

        # for idx, (resume_name, avg_score) in enumerate(sorted_resumes, start=1):
        #     st.subheader(f" {idx}. {resume_name}")
        #     st.write(f"**Average Similarity Score:** `{avg_score:.4f}`")

        #     # Show summary for first chunk of this resume
        #     first_doc = next(doc for doc, score in results if doc.metadata.get("name") == resume_name)
        #     with st.expander("Show summary "):
        #         summary = summarize_docs(first_doc)
        #         st.write(f"**Summary**:\n{summary}")







        if not results:
            st.warning(" No relevant resumes found.")
            return

        # Step 1: Sort all chunks by score (best first)
        results.sort(key=lambda x: x[1], reverse=True)

        # Step 2: Pick top N unique resumes
        top_resumes = {}
        for doc, score in results:
            resume_name = doc.metadata.get("name", "Unknown Resume")
            if resume_name not in top_resumes:
                top_resumes[resume_name] = score
            if len(top_resumes) >= int(document_count):
                break

        # Step 3: Display the top N resumes
        st.write("---")
        st.write(f"### TOP {len(top_resumes)}  RELEVANT RESUMES ")

        for idx, (resume_name, score) in enumerate(top_resumes.items(), start=1):
            st.subheader(f" {idx}. {resume_name}")
            st.write(f"**Best Similarity Score:** `{score:.4f}`")

            # Show summary of best chunk
            top_doc = next(doc for doc, sc in results if doc.metadata.get("name") == resume_name)
            with st.expander("Show summary 👀"):
                summary = summarize_docs(top_doc)
                st.write(f"**Summary**:\n{summary}")




    
 
 #################################################################################
        st.success(" Done! Hope this saved you hours of screening work.")

# --- Run App ---
if __name__ == "__main__":
    if "unique_id" not in st.session_state:
        st.session_state["unique_id"] = ""
    main()
