from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredPowerPointLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.chains.summarize import load_summarize_chain
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import os

#loading llm env groq
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

#llm
llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    groq_api_key=GROQ_API_KEY
)

# data ingestion 
def load_document(file_path):
    if str(file_path).endswith(".pdf"):
        loader = PyPDFLoader(file_path)
    elif str(file_path).endswith(".docx"):
        loader = Docx2txtLoader(file_path)
    elif str(file_path).endswith(".pptx"):
        loader = UnstructuredPowerPointLoader(file_path)
    else:
        raise ValueError("Unsupported format")
    
    docs = loader.load()
    return docs

# text splitting
def split_docs(docs, chunk_size=1000, chunk_overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_documents(docs)

#embedding model
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

#making of indexing vector store 
def build_qa(docs):
    # Create embeddings + vector store
    vectorstore = FAISS.from_documents(docs, embedding_model)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # QA chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=retriever,
        chain_type="stuff"
    )
    return qa_chain


# FUNCTION FOR SUMMARIZATION
def build_summarization_chain():
    return load_summarize_chain(llm, chain_type="map_reduce")

#function for extracting import information from docs

def extract_facts_and_points(doc_text: str) -> str:
    """
    Extracts key facts, important fields, and critical insights from any document (pdf, doc, ppt, notes, etc.).
    """
    
    prompt = f"""
    You are an expert information extractor.  
    Your task is to carefully read the following document text and extract:
    - Key facts (with context)
    - Important fields, numbers, names, dates, definitions, or rules
    - Main points and insights
    - Relevant quotes or excerpts
    - Key takeaways
    - if any fact and figure are available in doc do return this also with context and fields
    - Action items (if any)
    
    The document may be:
    - A project repo or technical document
    - SOP or policy
    - Notes or a knowledge document
    - A presentation (PPT converted text)
    - Or any other kind of unstructured content
    
    Document Text:
    \"\"\"{doc_text}\"\"\"

    Now provide the extracted information in a **clear bullet point list**. 
    If something is unclear, make a note of it instead of guessing.
    """

    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else response

def qa_with_docs(file_path: str):
    # Load document
    docs = load_document(file_path)
    split_documents = split_docs(docs)

    # QA
    qa_chain = build_qa(split_documents)
    return qa_chain

    #answer = qa_chain.invoke({"query": query})
    #answer_text = answer if isinstance(answer, str) else answer.get("result")
    #print(f"QA Answer: {answer if isinstance(answer, str) else answer.get('result')}")
    #return{
     #   "qa": answer_text
    #}
# Full processing pipeline
def process_file_summarization(file_path):
    # Load + split
    docs = load_document(file_path)
    split_documents = split_docs(docs)

    # Summarization
    summarization_chain = build_summarization_chain()
    summary = summarization_chain.run(split_documents)
    print(f"Summary: {summary}")
    return{
        "summary": summary
    }

def process_file_extraction(file_path):
    # Load + split
    docs = load_document(file_path)
    # Fact extraction
    full_text = " ".join([doc.page_content for doc in docs])
    extracted_info = extract_facts_and_points(full_text)
    print(f"Extracted Information:\n{extracted_info}")
    return {
        "facts": extracted_info
    }
