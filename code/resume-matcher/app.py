import json

import streamlit as st
from docx import Document
from pypdf import PdfReader

from llm_client import LLMClient

st.set_page_config(page_title="Resume Matcher", page_icon="📄", layout="centered")


@st.cache_resource
def get_client():
    return LLMClient()


def extract_text(uploaded):
    name = uploaded.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(uploaded)
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(uploaded)
        return "\n".join(p.text for p in doc.paragraphs)
    return uploaded.read().decode("utf-8", errors="ignore")


st.title("📄 Resume-to-Job Matcher")
st.caption("Powered by an LLM (Gemini). Upload or paste a resume, add a job description, get a match report.")

st.subheader("1. Resume")
tab_upload, tab_paste = st.tabs(["Upload file", "Paste text"])
resume_text = ""

with tab_upload:
    file = st.file_uploader("PDF, DOCX or TXT", type=["pdf", "docx", "txt"])
    if file:
        resume_text = extract_text(file)
        with st.expander("Preview extracted text"):
            st.text(resume_text[:1500])

with tab_paste:
    pasted = st.text_area("Paste your resume here", height=200)
    if pasted.strip():
        resume_text = pasted

st.subheader("2. Job description")
job_text = st.text_area("Paste the job description here", height=200)

if st.button("Analyze", type="primary"):
    if not resume_text.strip() or not job_text.strip():
        st.warning("Please provide both a resume and a job description.")
    else:
        try:
            with st.spinner("Analyzing with the LLM..."):
                result = get_client().analyze(resume_text, job_text)
        except Exception as e:
            st.error(f"Something went wrong: {e}")
        else:
            st.divider()
            st.subheader("Result")
            score = int(result["match_score"])
            st.metric("Match score", f"{score}/100")
            st.progress(min(max(score, 0), 100) / 100)
            st.write(result["candidate_summary"])

            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**✅ Matched skills**")
                for s in result["matched_skills"]:
                    st.write(f"- {s}")
            with col2:
                st.markdown("**❌ Missing skills**")
                for s in result["missing_skills"]:
                    st.write(f"- {s}")

            st.markdown("**💪 Strengths**")
            for s in result["strengths"]:
                st.write(f"- {s}")

            st.markdown("**💡 Suggestions**")
            for i, s in enumerate(result["suggestions"], 1):
                st.write(f"{i}. {s}")

            st.download_button(
                "Download JSON",
                json.dumps(result, indent=2),
                file_name="match_result.json",
                mime="application/json",
            )