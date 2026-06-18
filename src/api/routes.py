import time
from fastapi import APIRouter,HTTPException
from src.core.embedding import EmbeddingService
from src.repository.chromadb_repo import ChromaDBRepository
from src.api.schemas import SearchRequest,SearchResponse,IndexResponse
from src.services.indexer import run_indexing_pipeline

router =  APIRouter()

embedder = EmbeddingService()
repo = ChromaDBRepository()

@router.post("/search",response_model=SearchResponse)
def perform_semantic_search(request:SearchRequest):
    """Takes a JSON search request, embeds it, and queries the vault."""
    
    try:
        start_time = time.time()
        
        query_vector = embedder.generate_embeddings(request.query)
        
        results = repo.search(query_embedding=query_vector.tolist(),k=request.top_k)
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000
        
        return SearchResponse(
            query  = request.query,
            results = results,
            execution_time_ms = execution_time
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
@router.post("/index", response_model=IndexResponse)
def trigger_indexing_pipeline():
    """Triggers the VAST engine to scan, chunk, embed, and store new documents."""
    try:
        
        stats = run_indexing_pipeline()
        
        if not stats:
            raise HTTPException(status_code=404, detail="No documents found in primary_repo.")
            
        return IndexResponse(
            message="Successfully executed indexing pipeline.",
            documents_processed=stats["documents_processed"],
            total_database_items=stats["total_database_items"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))