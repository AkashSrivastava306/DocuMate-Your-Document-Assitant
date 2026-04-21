import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import json
import re

# 1️⃣ Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

if not groq_api_key:
    raise ValueError("GROQ_API_KEY not set")

# 2️⃣ Initialize Groq LLM
llm = ChatGroq(
    groq_api_key=groq_api_key,
    model="llama3-8b-8192",
    temperature=0
)


# -------------------------------
# Utility: Extract JSON from LLM response
# -------------------------------
def extract_json_from_text(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return None


# -------------------------------
# Extract factual claims from chunk
# -------------------------------
def extract_facts(chunk):
    prompt = f"""
You are a fact-checking assistant. 
Given the following text chunk, identify statements that can be verified objectively.

Return ONLY JSON:
{{
    "fact": "<fact or null>"
}}

Text:
\"\"\"{chunk}\"\"\"
"""
    response = llm.invoke(prompt)
    claim = extract_json_from_text(response.content)
    return claim


# -------------------------------
# Extract facts from all chunks
# -------------------------------
def extract_facts_from_chunks(chunks):
    all_facts = []

    for chunk in chunks:
        fact = extract_facts(chunk)

        fact_value = fact.get("fact") if isinstance(fact, dict) else None

        if fact_value in [None, "null"]:
            continue

        all_facts.append(fact_value)

    return all_facts


# -------------------------------
# Fact-check a single claim
# -------------------------------
def fact_check_claim(claim: str) -> str:
    try:
        from langchain_community.tools import DuckDuckGoSearchRun
        search = DuckDuckGoSearchRun()

        search_results = search.run(claim)

        prompt = f"""
        Fact-check this statement: '{claim}'
        this search result:'{search_results}'
        Return:
        - True or False
        - Corrected info (if false)
        - Reference links
        """

        return llm.invoke(prompt).content

    except Exception as e:
        return f"Search unavailable. Error: {str(e)}"


# -------------------------------
# Fact-check multiple claims
# -------------------------------
def fact_check_claims(claims: list) -> list:
    if not claims:
        return ["No claims to fact-check"]

    results = []

    for claim in claims:
        result = fact_check_claim(claim)
        results.append(result)

    return results


# -------------------------------
# Grammar & mistake detection
# -------------------------------
def finding_mistake(text):
    prompt = f"""
    You are a grammar correction assistant.
    Return ONLY JSON:
    {{
    "mistake": "...",
    "type": "...",
    "correction": "..."
    }}

    Text:
    \"\"\"{text}\"\"\"
    """
    response = llm.invoke(prompt)
    return extract_json_from_text(response.content)


def checking_grammar_chunks(chunks):
    results = []

    for i, chunk in enumerate(chunks):
        result = finding_mistake(chunk)

        if result is None:
            result = {"mistake": None, "type": None, "correction": None}

        results.append({
            "chunk_index": i,
            "text": chunk,
            "result": result
        })

    return results
