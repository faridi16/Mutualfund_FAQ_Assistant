import os
import glob
import json
from langchain.schema import Document
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def main():
    # 1. Initialize Embeddings
    print("Initializing BGE-small embeddings...")
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    # 2. Setup Vector Database
    persist_directory = "chroma_db"
    docs = []
    
    # 3. Read Parsed JSON Blocks
    json_files = glob.glob("data/parsed/*.json")
    for filepath in json_files:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        scheme_id = data.get("scheme_id")
        scheme_name = data.get("scheme_name")
        source_url = data.get("source_url")
        nav_date = data.get("nav_date")
        
        for block in data.get("text_blocks", []):
            section = block.get("section_title")
            text = block.get("text")
            
            # Create a Langchain Document representing this exact semantic chunk
            doc = Document(
                page_content=text,
                metadata={
                    "scheme_id": scheme_id,
                    "scheme_name": scheme_name,
                    "source_url": source_url,
                    "nav_date": nav_date,
                    "section_title": section
                }
            )
            docs.append(doc)
            
    print(f"Loaded {len(docs)} perfectly semantic chunks (Documents).")
    
    # 4. Ingest into Chroma
    print("Ingesting into ChromaDB (computing vectors)...")
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    vectorstore.persist()
    print(f"Success! Vector database persisted to ./{persist_directory}/")
    
    # 5. Quick Test Query
    print("\n--- Testing Vector DB ---")
    query = "What is the exit load for HDFC Gold ETF?"
    print(f"Query: {query}")
    results = vectorstore.similarity_search(query, k=2)
    for i, res in enumerate(results):
        print(f"\nResult {i+1}:")
        print(f"Fund: {res.metadata.get('scheme_name')} ({res.metadata.get('section_title')})")
        print(f"URL: {res.metadata.get('source_url')}")
        print(f"Text: {res.page_content}")

if __name__ == "__main__":
    main()
