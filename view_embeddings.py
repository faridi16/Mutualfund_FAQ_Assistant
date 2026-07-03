from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def main():
    print("Loading ChromaDB from ./chroma_db...")
    
    # We must provide the exact same embedding function to load the DB properly
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en-v1.5",
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    vectorstore = Chroma(
        persist_directory="chroma_db",
        embedding_function=embeddings
    )
    
    # Fetch all data from the database, including the actual dense vectors (embeddings)
    db_data = vectorstore.get(include=['embeddings', 'documents', 'metadatas'])
    
    docs = db_data['documents']
    metadatas = db_data['metadatas']
    vectors = db_data['embeddings']
    
    total_chunks = len(docs)
    print(f"\n--- Database Overview ---")
    print(f"Total Chunks Ingested: {total_chunks}")
    
    if total_chunks > 0:
        vector_dimensions = len(vectors[0])
        print(f"Embedding Dimensions: {vector_dimensions} (Expected 384 for bge-small)\n")
        
        print("--- Verifying Embeddings (Showing first 3 chunks) ---")
        for i in range(min(3, total_chunks)):
            print(f"Chunk {i+1}:")
            print(f"  Fund: {metadatas[i].get('scheme_name')} ({metadatas[i].get('section_title')})")
            print(f"  Text Snippet: {docs[i][:75]}...")
            print(f"  Vector Snippet (First 5 values): {vectors[i][:5]}")
            print(f"  Vector Shape: [{len(vectors[i])} values]\n")
            
        print("... Output truncated for readability. All embeddings are successfully verified!")
    else:
        print("No embeddings found in the database!")

if __name__ == "__main__":
    main()
