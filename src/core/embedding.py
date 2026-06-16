from sentence_transformers import SentenceTransformer
from typing import List,Dict,Union
import numpy as np

class EmbeddingService :
    '''
        A singleton wrapper for the local ScentenceTransformer model to guarentee that it is loaded exactly once during the application lifecycle.
    '''
        
    _instance = None
    _model = None
    
    def __new__(cls) :
        if cls._instance is None :
            print(f"[System] Initializing VAST Embedding Engine (all-MiliLM-L6-v2)...")
            print(f"[System] This may take a moment on first run to download the weights.")
            cls._instance = super(EmbeddingService,cls).__new__(cls)
            cls._model = SentenceTransformer("all-MiniLM-L6-v2")
        return cls._instance
    
    def generate_embeddings(self,texts:Union[str,List[str]]) -> np.ndarray :
        """
        Transforms raw text strings into 384-dimensional dense vectors.
        """
            
        return self._model.encode(texts)
    
    
if __name__ == "__main__":
    
    embedder1 = EmbeddingService()
    embedder2 = EmbeddingService()
    
    print("\n--- Architecture Test ---")
    print(f"Are both embedders the exact same object in memory? {embedder1 is embedder2}")
    
    
    print("\n--- Vector Math Test ---")
    sample_text = "The Traveling Salesperson Problem can be optimized using Branch and Bound."
    vector = embedder1.generate_embeddings(sample_text)
    
    print(f"Vector Mathematical Shape: {vector.shape}")
    print(f"First 5 dimensions out of 384: \n{vector[:5]}")