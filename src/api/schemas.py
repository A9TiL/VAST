from pydantic import BaseModel
from typing import List,Dict,Any

class SearchRequest(BaseModel):
    query : str
    top_k : int = 3
    
class SearchResultItem(BaseModel):
    id:str
    text :str
    metadata : Dict[str,Any]
    distance : float
    
class SearchResponse(BaseModel):
    query:str
    results:List[SearchResultItem]
    execution_time_ms : float
    
    
class IndexResponse(BaseModel):
    message :str
    documents_processed : int
    total_database_items : int
    