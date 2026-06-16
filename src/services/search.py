import time
from src.core.embedding import EmbeddingService
from src.repository.chromadb_repo import ChromaDBRepository

def start_interactive_search():
    print("\n" + "="*60)
    print("🧠 VAST SEMANTIC SEARCH ENGINE ONLINE")
    print("Type 'exit' or 'quit' to shut down the engine.")
    print("="*60)
    
    print("\n[System] Booting up Machine Learning Models...")
    embedder = EmbeddingService()
    repo = ChromaDBRepository()
    
    K_RESULTS = 3
    
    while True:
        query = input("\nEnter your search query: ").strip()
        
        if query.lower() in ['exit','quit']:
            print("[System] Shutting down VAST engine. Goodbyee!")
            break
        if not query:
            continue
        
        print("\n[Processing] Calculating dense vectors and scanning databse...")
        start_time = time.time()
        
        quer_vector = embedder.generate_embeddings(query)
        
        results = repo.search(query_embedding=quer_vector.tolist(),k=K_RESULTS)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        print(f"Search completedin {execution_time:.2f} ms.")
        print("-"*60)
        
        for rank,result in enumerate(results,start=1):
            score = result['distance']
            doc_name = result['metadata'].get('source_file','Unknown')
            print(f"\n RANK {rank} | Distance Score : {score:.4f} | Source : {doc_name}")
            print(f"\nTEXT : {result['text']}")
        print("\n" + "-"*60)
        
if __name__ == "__main__":
    start_interactive_search()