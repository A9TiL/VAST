from fastapi import FastAPI 
from src.api.routes import router

app = FastAPI(
    title="VAST Semantic Search Engine",
    description="Enterprise Retrieval-Augmented Generation API",
    version="1.0.0"
)

app.include_router(router,prefix="/api/v1")

@app.get("/health")
def health_check():
    return {"status" : "online" , "system" : "VAST Engine Core"}