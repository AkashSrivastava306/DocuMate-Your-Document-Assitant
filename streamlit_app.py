import streamlit as st
from pathlib import Path
import os
import html

# Import backend functions
from rag import load_document, split_docs, process_file_summarization, process_file_extraction, build_qa
from formatandstyling import formatting_pipeline
from content_sugesstion import process_document
from fact_pipeline import fact_check_claims, extract_facts_from_chunks, checking_grammar_chunks

st.set_page_config(page_title="DocuMate", layout="wide")
st.title("📄 DocuMate - Your Document Assistant")

# Upload file
uploaded_file = st.file_uploader("Upload a PDF or Word document", type=["pdf", "docx"])

if uploaded_file:
    # Ensure temp folder exists
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)

    file_path = temp_dir / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success(f"Uploaded {uploaded_file.name} successfully!")

    # -------------------
    # Build QA chain once
    # -------------------
    if "qa_chain" not in st.session_state:
        docs = load_document(file_path)
        split_documents = split_docs(docs)
        qa_chain = build_qa(split_documents)
        st.session_state.qa_chain = qa_chain
        st.success("QA chain is ready!")

    # Tabs for all features
    tabs = st.tabs([
        "QA with Docs",
        "Summarization",
        "Extraction",
        "Formatting & Styling",
        "Spelling & Grammar Check",
        "Fact Check",
        "Content Suggestion"
    ])

    # ------------------- QA with Docs -------------------
    with tabs[0]:
        st.subheader("Chat with Document")

        if "chat_history" not in st.session_state:
            st.session_state.chat_history = []

        chat_display = st.empty()  # Container for all chat bubbles

        # Function to safely render messages
        def render_chat_message(msg, role="ai"):
            safe_text = html.escape(msg)
            lines = [line.strip() for line in safe_text.split("\n") if line.strip()]
            if role == "ai" and len(lines) > 1:
                safe_text = "<br>".join([f"{i+1}. {line}" for i, line in enumerate(lines)])
            else:
                safe_text = "<br>".join(lines)

            if role == "user":
                bubble_html = f"""
                <div style='text-align: right; margin:5px;'>
                    <span style='background-color:#0d6efd; color:white; padding:8px 12px; border-radius:15px; display:inline-block; max-width:70%; word-wrap:break-word;'>
                        {safe_text}
                    </span>
                </div>
                """
            else:
                bubble_html = f"""
                <div style='text-align: left; margin:5px;'>
                    <span style='background-color:#e9ecef; color:black; padding:8px 12px; border-radius:15px; display:inline-block; max-width:70%; word-wrap:break-word;'>
                        {safe_text}
                    </span>
                </div>
                """
            return bubble_html

        # Render chat history
        def render_chat():
            html_content = ""
            for msg in st.session_state.chat_history:
                html_content += render_chat_message(msg['content'], msg['role'])
            chat_display.markdown(html_content, unsafe_allow_html=True)

            # Auto-scroll
            st.markdown(
                """
                <script>
                var chatContainers = window.parent.document.querySelectorAll('[data-testid="stMarkdownContainer"]');
                if(chatContainers.length > 0) {
                    chatContainers[chatContainers.length-1].scrollIntoView({behavior: 'smooth', block: 'end'});
                }
                </script>
                """,
                unsafe_allow_html=True
            )

        # Initial render
        render_chat()

        # Chat input
        user_input = st.text_input("Type your question here:", key="chat_input")
        if st.button("Send") and user_input:
            answer = st.session_state.qa_chain.run(user_input)
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "ai", "content": answer})
            render_chat()

    # ------------------- Summarization -------------------
    with tabs[1]:
        st.subheader("Document Summary")
        if st.button("Generate Summary"):
            summary = process_file_summarization(file_path)
            st.write(summary)

    # ------------------- Extraction -------------------
    with tabs[2]:
        st.subheader("Extracted Tables / Key Metrics / Entities")
        if st.button("Extract Data"):
            extracted_data = process_file_extraction(file_path)
            st.write(extracted_data)

    # ------------------- Formatting & Styling -------------------
    with tabs[3]:
        st.subheader("Apply Formatting & Template")
        if st.button("Format Document"):
            formatted_file = formatting_pipeline(file_path)
            st.success("Document formatted!")
            st.download_button(
                "Download Formatted Document",
                formatted_file.read_bytes(),
                file_name=f"formatted_{uploaded_file.name}"
            )

    # ------------------- Spelling & Grammar Check -------------------
    with tabs[4]:
        st.subheader("Check Spelling & Grammar")
        if st.button("Check Spelling & Grammar"):
            docs = load_document(file_path)
            chunks = split_docs(docs)
            grammar_corrections = checking_grammar_chunks(chunks)
            st.write(grammar_corrections)

    # ------------------- Fact Check -------------------
    with tabs[5]:
        st.subheader("Fact Check Document")
        if st.button("Check Facts"):
            docs = load_document(file_path)
            chunks = split_docs(docs)
            facts = extract_facts_from_chunks(chunks)
            fact_results = fact_check_claims(facts)
            st.write(fact_results)

    # ------------------- Content Suggestion -------------------
    with tabs[6]:
        st.subheader("Content Recommendation / Suggestion")
        if st.button("Get Suggestions"):
            suggestions = process_document(file_path)
            st.write(suggestions)
