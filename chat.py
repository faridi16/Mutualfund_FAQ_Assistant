import os
import sys
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate

# Suppress HuggingFace/Chroma warnings
import warnings
warnings.filterwarnings("ignore")

def check_env():
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY environment variable is not set.")
        print("Please set it in your terminal by running:")
        print("export GROQ_API_KEY='your_api_key'")
        print("Or add it to a .env file in this directory.")
        sys.exit(1)

def init_models():
    """Initialize and return the LLM and Vector Database instances."""
    check_env()
    
    # Initialize Groq LLM with the highly capable versatile model
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.0,
        max_tokens=250
    )
    
    # Initialize Vector DB
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )
    
    return llm, vectorstore

def classify_intent(llm, query):
    prompt = f"""Classify the following user query as FACTUAL or ADVISORY.
If the user asks for an opinion, prediction, or investment advice (e.g. "Should I invest?", "Is this a good fund?", "Which fund is best?"), return ADVISORY.
If the user asks for specific data points (e.g. "What is the NAV?", "Who is the fund manager?", "What is the exit load?"), return FACTUAL.
Output ONLY the exact word FACTUAL or ADVISORY. Nothing else.

Query: {query}
Classification:"""
    
    try:
        response = llm.invoke(prompt)
        return response.content.strip().upper()
    except Exception as e:
        if "429" in str(e) or "Too Many Requests" in str(e):
            return "RATE_LIMIT"
        raise e

def generate_answer(llm, vectorstore, query):
    try:
        # Phase 7 Step 1: Semantic Block Top-K Retrieval
        # Increased to k=5 to pull context from multiple funds simultaneously
        docs = vectorstore.similarity_search(query, k=5)
        
        if not docs:
            return "I could not find any relevant information in my database."
            
        # Combine retrieved context and print debug info
        context = ""
        print("\n--- [DEBUG] Vector Database Retrieval ---")
        for i, doc in enumerate(docs):
            chunk_text = doc.page_content
            fund_name = doc.metadata.get('scheme_name')
            print(f"Chunk {i+1} ({fund_name}): {chunk_text[:150]}...")
            context += f"--- Source {i+1} ---\nFund: {fund_name}\nURL: {doc.metadata.get('source_url')}\nText: {chunk_text}\n\n"
        print("-----------------------------------------\n")
            
        primary_url = docs[0].metadata.get("source_url", "https://groww.in/mutual-funds")
        
        # Phase 7 Step 2: Strict Prompt Engineering
        prompt_template = PromptTemplate.from_template("""You are a highly constrained factual assistant for HDFC Mutual Funds.
Answer the user's question using ONLY the provided context below.
You MUST adhere strictly to these rules:
1. Your response MUST be 3 sentences or less.
2. You MUST include exactly one citation link at the end of your answer in the format [Source](URL).
3. Do not invent information. If the answer is not in the context, say "I don't know based on the available context".

Context:
{context}

User Question: {question}
Answer:""")

        formatted_prompt = prompt_template.format(context=context, question=query)
        
        # Phase 7 Step 3: Groq Engine Generation (Deterministic)
        response = llm.invoke(formatted_prompt)
        
        # Phase 7 Step 4: Post-Processing (Footer)
        final_answer = response.content.strip()
        footer = "\n\n*Last updated from sources: 02 Jul 2026*"
        
        # Ensure citation format exists (if LLM missed it, inject it as a fallback)
        if "[Source]" not in final_answer:
            final_answer += f"\n[Source]({primary_url})"
            
        return final_answer + footer
    except Exception as e:
        if "429" in str(e) or "Too Many Requests" in str(e):
            return "⚠️ **Rate Limit Reached**: The Groq API limit (30 requests/min) was exceeded. Please wait a minute and try again!"
        return f"An error occurred: {str(e)}"

def process_query(llm, vectorstore, query):
    """Unified function to handle intent classification, guardrails, and generation."""
    intent = classify_intent(llm, query)
    
    if intent == "RATE_LIMIT":
        return "⚠️ **Rate Limit Reached**: The Groq API limit (30 requests/min) was exceeded. Please wait a minute and try again!"
    
    if "ADVISORY" in intent:
        return "I cannot provide investment advice or opinions on market movements. For educational resources on mutual fund investing, please refer to SEBI guidelines at https://investor.sebi.gov.in/"
        
    return generate_answer(llm, vectorstore, query)

def main():
    print("Loading LLM (Groq Llama-3.3-70b-versatile) and Vector Database...")
    llm, vectorstore = init_models()
    
    print("\n=======================================================")
    print("Mutual Fund FAQ Assistant initialized! Type 'exit' to quit.")
    print("=======================================================\n")
    
    while True:
        try:
            query = input("User: ")
            if query.lower() in ['exit', 'quit']:
                break
            if not query.strip():
                continue
                
            answer = process_query(llm, vectorstore, query)
            print(f"\nAssistant: {answer}\n")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\nError: {e}\n")

if __name__ == "__main__":
    main()
