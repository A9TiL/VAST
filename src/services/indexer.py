from src.services.ingestion import DocumentDiscovery
from src.core.chunker import SemanticChunker
from src.core.embedding import EmbeddingService
from src.repository.chromadb_repo import ChromaDBRepository
from config.settings import CHUNK_SIZE,CHUNK_OVERLAP

def run_indexing_pipeline():
    print("\n" + "="*50)
    print("INITIALIZING VAST INDEXING PIPELINE")
    print("="*50)
    
    #  Ingestion
    print(f"\n[Phase 1] Discovering and Extracting Documents...")
    discoverer = DocumentDiscovery()
    raw_docs = discoverer.extract_raw_documents()
    
    if not raw_docs :
        print("[Error] No documents found in primaray_repo. Exiting pipeline.")
        return
    
    # chunking
    print(f"\n[Phase 2] Applying the Semantic chunker to the documents...")
    chunker = SemanticChunker(max_chunk_size=1000,overlap_size=200)
    all_chunks = []
    
    for doc in raw_docs :
        document_chunks = chunker.chunk_text(
            text= doc["raw_text"],
            source_metadata={"source_file" : doc["source_file"]}
        )
        all_chunks.extend(document_chunks)
        
        
    for i, chunk in enumerate(all_chunks):
        # To create an ID 
        filename = chunk["metadata"]["source_file"]
        chunk["chunk_id"] = f"{filename}_chunk_{i}"
        
    print(f"[Phase 2] Successfully generated {len(all_chunks)} semantic chunks.")
        
    # Embedding
    print(f"[Phase 3] Generating Dense Vector Enbeddings...")
    
    embedder = EmbeddingService()
    
    chunk_texts = [chunk["text"] for chunk in all_chunks]
    
    embeddings = embedder.generate_embeddings(chunk_texts)
    
    print(f"[Phase 3] Mathematical transformation complete . Matrix Shape: {embeddings.shape}")
    
    #Database Storage
    print("\n[Phase 4] Committing to ChromaDB Storage...")
    repo = ChromaDBRepository()
    
    repo.index_chunks(chunks=all_chunks, embeddings=embeddings.tolist())
    
    final_count = repo.collection.count()
    
    print("\n" + "="*50)
    print("PIPELINE EXECUTION COMPLETE")
    print(f"{repo.collection.count()} total items are now secured in the database.")
    print("="*50 + "\n")
    
    return{
        "documents_processed" : len(raw_docs),
        "total_database_items" : final_count
    }
    
if __name__ == "__main__":
    run_indexing_pipeline()