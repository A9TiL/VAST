import chromadb 
from typing import List,Dict,Any
from src.repository.base import VectorRepository
from config.settings import CHROMA_DB_DIR , COLLECTION_NAME

class ChromaDBRepository(VectorRepository):
    '''
    Concrete implementation of the vector database using local ChromaDB.
    '''
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
        
        self.collection = self.client.get_or_create_collection(
            name = COLLECTION_NAME,
            metadata = {"hnsw:space":"cosine"}
        )
        
    def index_chunks(self, chunks: List[Dict[str, Any]], embeddings: List[List[float]]):
        '''
            Indexes text chunks and their vectors into ChromaDB.
        '''
        
        if not chunks :
            print(f"[Warning] No chunks provided for indexing.")
            return
        
        ids = [chunk["chunk_id"] for chunk in chunks]
        texts = [chunk["text"] for chunk in chunks]
        medadatas = [chunk["metadata"] for chunk in chunks]
        
        self.collection.upsert(
            ids = ids,
            embeddings= embeddings,
            documents= texts,
            metadatas= medadatas
        )
        
        print(f"[Database] Successfully indexed {len(ids)} chunks in t0 ChromaDB.")
        
    def search(self, query_embedding: List[float], k: int) -> List[Dict[str, Any]]:
        
        """Queries the vector database and returns the top \'k\' closest chunks based on cosine similarity."""
        
        raw_results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results = k
        )
        
        formatted_results = []
        
        if not raw_results['ids'] or not raw_results['ids'][0]:
            return formatted_results
        
        for i in range(len(raw_results['ids'][0])):
            formatted_results.append(
                {
                    "id": raw_results['ids'][0][i],
                    "text":raw_results['documents'][0][i],
                    "metadata":raw_results['metadatas'][0][i],
                    "distance":raw_results['distances'][0][i]
                }
            )
            return formatted_results
        
    
if __name__ == "__main__":
    print("[System] Connecting to local ChromaDB...")
    repo = ChromaDBRepository()
    print(f"[Success] Database initialized! Total indexed items: {repo.collection.count()}")