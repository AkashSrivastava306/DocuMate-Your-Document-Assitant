import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from docx import Document

# ✅ Load API keys from .env
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# ✅ Initialize Groq LLM
llm = ChatGroq(model="llama3-70b-8192", api_key=groq_api_key)

def read_docx(file_path):
    """Extract text from a Word doc."""
    doc = Document(file_path)
    text = []
    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text.strip())
    return "\n".join(text)

def analyze_doc_with_llm(doc_text):
    """Ask LLM to return structured JSON analysis."""
    prompt = f"""
    You are an AI document assistant.
    Analyze the document below and respond in **valid JSON only** with the following keys:
    - doc_type: (string) type of document (e.g., report, proposal, resume)
    - expected_sections: (list of strings) ideal sections for this doc type
    - present_sections: (list of strings) sections already found
    - missing_sections: (list of strings) sections not present
    - expanded_bullets: (list of strings) bullet points rewritten as full paragraphs
    - drafts_for_missing: (dict) keys = missing section names, values = draft text

    Document Content:
    {doc_text}
    """
    response = llm.invoke(prompt)
    content = response.content

    # Ensure valid JSON
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # If model outputs extra text, try to extract JSON only
        try:
            json_str = content[content.find("{"):content.rfind("}")+1]
            return json.loads(json_str)
        except:
            return {"error": "Invalid JSON from LLM", "raw_output": content}

def process_document(input_file):
    # Step 1: Read input
    doc_text = read_docx(input_file)

    # Step 2: Ask Groq LLM
    analysis = analyze_doc_with_llm(doc_text)

    # Step 3: Print JSON
    print("\n📄 AI Suggestions (JSON):\n")
    print(json.dumps(analysis, indent=2))

    return analysis


# Example Usage
if __name__ == "__main__":
    process_document("project.docx")
