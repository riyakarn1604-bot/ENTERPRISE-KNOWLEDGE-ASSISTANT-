from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Ensure src directory is in the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from retrieve import Retriever
from generate import generate_answer

app = FastAPI(title="Enterprise Knowledge Assistant API")

# Setup CORS to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str

class SourceChunk(BaseModel):
    chunk_id: str
    source: str
    text: str
    distance: float

class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceChunk]

# Initialize Retriever globally
retriever = None

@app.on_event("startup")
async def startup_event():
    global retriever
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    index_file = os.path.join(base_dir, "backend", "faiss_index.bin")
    meta_file = os.path.join(base_dir, "backend", "faiss_meta.json")
    
    if os.path.exists(index_file) and os.path.exists(meta_file):
        retriever = Retriever(index_file, meta_file)
        print("Retriever initialized successfully.")
    else:
        print("Warning: FAISS index not found. The /ask endpoint will fail.")

@app.post("/ask", response_model=QueryResponse)
async def ask_question(request: QueryRequest):
    if not retriever:
        raise HTTPException(status_code=500, detail="Retriever not initialized. FAISS index missing.")
        
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
        
    try:
        # 1. Retrieve chunks
        results = retriever.search(query, top_k=3, distance_threshold=1.5)
        
        # 2. Generate answer
        answer = generate_answer(query, results)
        
        # 3. Format response
        sources = [SourceChunk(**r) for r in results]
        return QueryResponse(answer=answer, sources=sources)
        
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Internal server error while processing query.")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "index_loaded": retriever is not None}
