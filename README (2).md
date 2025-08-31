# DocuMate - Intelligent Document Assistant

DocuMate is an AI-powered Document Intelligence Copilot built with **Streamlit**.  
It provides multiple enterprise-ready features like document chat, summarization, extraction, grammar & spelling check, formatting suggestions, fact-checking, and content recommendations.

---

## 🚀 Features

- **Chat with Documents** – Upload documents (PDF/DOCX/TXT) and interact via a conversational interface.
- **Summarization** – Generate concise summaries of long documents.
- **Information Extraction** – Pull out specific details from structured/unstructured text.
- **Spelling & Grammar Check** – Automatically detect and suggest corrections.
- **Formatting & Styling Consistency** – Ensure consistent headings, fonts, and document style.
- **Fact Verification** – Validate claims within the document against external knowledge.
- **Content Recommendations** – Suggest missing sections, improve flow, and refine tone.

---

## 🛠️ Tech Stack

- **Frontend/UI** – [Streamlit](https://streamlit.io/)
- **Backend/Logic** – Python (Custom ML/NLP pipelines)
- **LLM Integration** – OpenAI/Groq/Custom models (plug & play)
- **Data Handling** – PyPDF2, python-docx, Pandas
- **Deployment** – Azure / Localhost

---

## 📂 Project Structure

```
├── app.py                   # Main Streamlit app
├── rag/                     # RAG pipelines for document loading & splitting
├── summarization.py         # Summarization pipeline
├── extraction.py            # Information extraction pipeline
├── grammar_check.py         # Grammar & spelling correction pipeline
├── formatting.py            # Formatting and styling checks
├── fact_check.py            # Fact verification pipeline
├── content_suggestion.py    # Content recommendation pipeline
└── README.md                # Project documentation
```

---

## ⚡ Installation

1. Clone the repository  
```bash
git clone https://github.com/your-username/documate.git
cd documate
```

2. Create virtual environment & install dependencies  
```bash
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Run the Streamlit app  
```bash
streamlit run app.py
```

---

## 📖 Usage

1. Launch the app using the command above.  
2. Upload a document (PDF, DOCX, TXT).  
3. Select a feature tab:  
   - **Chat with Document** → Ask questions about the doc.  
   - **Summarization** → Get a summary of the doc.  
   - **Extraction** → Pull out entities, dates, numbers, etc.  
   - **Formatting & Style** → Ensure formatting consistency.  
   - **Fact Check** → Validate claims.  
   - **Content Recommendation** → Suggestions for improvement.  

---

## 🎯 POC Value

This project demonstrates how **Generative AI + RAG pipelines** can be combined for enterprise use cases like:  
- Automating knowledge retrieval  
- Enhancing productivity in document-heavy workflows  
- Reducing manual effort in proofreading, fact-checking, and compliance  

Perfect for **resume showcase, enterprise demo, and portfolio projects**.

---

## 👨‍💻 Author

**Akash Srivastava**  
Machine Learning Engineer | NLP Enthusiast  
(Feel free to update LinkedIn/GitHub links here)

---

## 📜 License

This project is licensed under the MIT License.
