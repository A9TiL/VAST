from abc import ABC, abstractmethod
from typing import List,Dict,Any

class VectorRepository(ABC):
    '''Abstract interface defining standard database operations.'''
    
    @abstractmethod
    def index_chunks(self,chunks:List[Dict[str,Any]], embeddings: List[List[float]]):
        """Must accept text chunks and their mathematical vectors to store them."""
        pass
    
    @abstractmethod
    def search(self, query_embedding: List[float], k: int) -> List[Dict[str, Any]]:
        """Must accept a query vector and return the top 'k' closest matches."""
        pass