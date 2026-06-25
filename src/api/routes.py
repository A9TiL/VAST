import time
from fastapi import APIRouter,HTTPException , UploadFile , File
from src.core.embedding import EmbeddingService
from src.repository.chromadb_repo import ChromaDBRepository
from src.api.schemas import SearchRequest,SearchResponse,IndexResponse,SystemStatsResponse,AskRequest, AskResponse
from src.services.indexer import run_indexing_pipeline
from  src.core.llm import LLMService
import os
from config.settings import PRIMARY_REPO_DIR
from pathlib import Path
import shutil
from fastapi.responses import FileResponse

router =  APIRouter()

embedder = EmbeddingService()
repo = ChromaDBRepository()
llm = LLMService()

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
    
@router.get("/stats",response_model=SystemStatsResponse)
def get_database_statistics():
    """Returns the real-time data inventory and health metrics from ChromaDB"""
    
    try :
        telemetry = repo.get_system_telemetry()
        return SystemStatsResponse(
            status = "healthy",
            total_chunks = telemetry["total_chunks"],
            indexed_files = telemetry["indexed_files"]
        )
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    
@router.get("/view/{filename}")
async def view_raw_file(filename:str):
    """Securely serves files while completely blocking path traversal."""

    base_dir = Path(PRIMARY_REPO_DIR).resolve()
    
    file_path = (base_dir/filename).resolve()
    
    print(f"DEBUG: Looking for file at -> {file_path}", flush=True)
    
    if not file_path.is_relative_to(base_dir):
        raise HTTPException(status_code=403,detail="Access Denied : Suspecious path traversal detected.")
    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404,detail="File not found in the vault.")
    
    return FileResponse(path=file_path,filename=filename)

@router.post("/ask",response_model=AskResponse)
def ask_vast_engine(request:AskRequest):
    """Full RAG Pipeline. Retrives context from ChromaDB and generates an AI answer."""
    
    try:
        start_time = time.time()
        
        query_vector = embedder.generate_embeddings(request.query)
        results = repo.search(query_embedding=query_vector.tolist(),k=7)
        
        if not results:
            return AskResponse(
                query = request.query,
                answer = "I'm sorry , but I don't have any documents in my vault to answer about this topic.",
                sources = [],
                execution_time = (time.time() - start_time) *1000
            )
            
        context_texts = [item['text'] for item in results]
        
        combined_context = "\n\n---\n\n".join(context_texts)
        
        # --- DEBUG BLOCK ---
        print("\n" + "="*50)
        print("[DEBUG] THE AI IS READING THIS EXACT CONTEXT:")
        print("="*50)
        print(combined_context)
        print("="*50 + "\n")
        # ----------------------------
        
        sources = list(set([item['metadata'].get('source_file','unknown') for item in results])) 
        
        ai_answer = llm.generate_answer(query=request.query,context=combined_context)
        
        end_time = time.time()
        
        return AskResponse(
            query = request.query,
            answer = ai_answer,
            sources = sources,
            execution_time_ms = (end_time - start_time) *1000
        )
            
    except Exception as e:
        HTTPException(status_code=500,detail=str(e))
        
@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Receives a file over the internet and saves it to the vault."""
    try:
        
        os.makedirs(PRIMARY_REPO_DIR, exist_ok=True)
        
        
        save_path = Path(PRIMARY_REPO_DIR) / file.filename
        
        
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {
            "status": "success", 
            "filename": file.filename, 
            "message": "File safely landed in the vault! Ready for indexing."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
