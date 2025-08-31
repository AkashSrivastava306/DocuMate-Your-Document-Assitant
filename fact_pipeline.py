import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from rag import load_document,split_docs
import json
import re

# 1️⃣ Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# 2️⃣ Initialize Groq LLM
llm = ChatGroq(
    api_key=groq_api_key,
    model="llama3-8b-8192",
    temperature=0
)

# Document loading and splitting
document = load_document("project.docx")
chunks = split_docs(document)


def extract_json_from_text(text):
    """
    Extracts JSON object from a text string.
    Returns a Python dict if successful, else None.
    """
    try:
        # Use regex to find JSON object
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            json_str = match.group(0)
            return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    return None
def extract_facts(chunk):
    prompt = f"""
    You are a fact-checking assistant. 
    Given the following text chunk, identify statements that can be verified objectively as true or false. 
    Do NOT include subjective opinions, marketing phrases, or vague descriptions. 
    Only extract statements that claim measurable, factual, or historical information.
    If no verifiable fact or claim is present, return null.
    Return your answer strictly in JSON format with the following schema:
    {{
    "fact": "<a verifiable fact or claim from the text, or null if none found>"
    }}
    Text chunk:
    \"\"\"{chunk}\"\"\"
    """
    response = llm.invoke(prompt)
    claim = extract_json_from_text(response.content)
    return claim
# 3️⃣ Initialize Web Search tool
search = DuckDuckGoSearchRun()
# 6️⃣ Fact-check a single claim
def fact_check_claim(claim: str) -> str:
    # 1. Perform web search
    search_results = search.run(claim)

    # 2. Ask LLM to summarize truthfulness + provide references
    prompt = f"""
    Fact-check the following statement: "{claim}"
    Based on this search result: "{search_results}"
    Return a short summary indicating:
    - True/False
    - Corrected information if False
    - Provide reference link(s)
    """
    response = llm.invoke(prompt).content
    return response


def extract_facts_from_chunks(chunks):
    all_facts = []
    for chunk in chunks:
        fact = extract_facts(chunk)
        # Get the fact value
        fact_value = fact.get("fact") if fact else None
        # Skip nulls
        if fact_value in [None, "null"]:
            continue
        # Append only the fact string
        all_facts.append(fact_value)
    return all_facts
all_facts = extract_facts_from_chunks(chunks)
#print("All verifiable facts extracted:")
#print(all_facts)


def fact_check_claims(claims: list) -> list:
    if claims is None or len(claims) == 0:
        return f"No claims to fact-check."
    results = []
    for claim in claims:
        result = fact_check_claim(claim)
        results.append(result)
    return results

results = fact_check_claims(all_facts)
#print("Fact-checking results:")
#print(results)


def finding_mistake(text):
    prompt = f"""
You are a grammar correction and spelling proofreading assistant.
Given the following text, identify **all spelling, grammar, and punctuation mistakes**.

Requirements:
1. Return ONLY a JSON object with the following fields:
{{
    "mistake": "<the mistake found, as a string or list of strings, or null if none>",
    "type": "<type of mistake: spelling, grammar, punctuation, or null>",
    "correction": "<the correction for each mistake, as string or list of strings, or null>"
}}
2. Do NOT include any explanations, notes, or extra text outside JSON.
3. If no mistakes are found, all fields should be null.

Text:
\"\"\"{text}\"\"\"
"""
    response = llm.invoke(prompt)
    # Parse the JSON string to dict
    return extract_json_from_text(response.content)

def checking_grammar_chunks(chunks):
    results = []

    for i, chunk in enumerate(chunks):
        result = finding_mistake(chunk)

        # Ensure JSON fields exist
        if result is None:
            result = {"mistake": None, "type": None, "correction": None}

        results.append({
            "chunk_index": i,
            "text": chunk,
            "result": result
        })

    return results

# Example usage
all_chunk_results = checking_grammar_chunks(chunks)

# Print results per chunk
for r in all_chunk_results:
    print(r)