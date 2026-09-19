import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import sys

class Retriever:
    def __init__(self, index_file, meta_file):
        print("Loading SentenceTransformer model...")
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        print("Loading FAISS index...")
        self.index = faiss.read_index(index_file)
        
        print("Loading metadata...")
        with open(meta_file, 'r', encoding='utf-8') as f:
            self.meta = json.load(f)
            
    def search(self, query, top_k=3, distance_threshold=1.5):
        # Embed the query
        query_vector = self.model.encode([query])
        
        # Search the index
        distances, indices = self.index.search(np.array(query_vector), top_k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: # FAISS returns -1 if not enough results
                continue
                
            distance = distances[0][i]
            
            # Simple thresholding logic
            if distance > distance_threshold:
                continue
                
            chunk_data = self.meta[idx]
            results.append({
                "chunk_id": chunk_data["chunk_id"],
                "source": chunk_data["source"],
                "text": chunk_data["text"],
                "distance": float(distance)
            })
            
        return results

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    index_file = os.path.join(base_dir, "backend", "faiss_index.bin")
    meta_file = os.path.join(base_dir, "backend", "faiss_meta.json")
    
    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        print("FAISS index or metadata not found. Please run embed.py first.")
        sys.exit(1)
        
    retriever = Retriever(index_file, meta_file)
    
    # Test queries
    test_queries = [
        "How many days of annual leave do I get?",
        "What happens if I accept a gift from a vendor?",
        "How do I pair the EchoSound Pro earbuds?",
        "What does error code E71 mean on the SmartThermo?",
        "How long is maternity leave?"
    ]
    
    for query in test_queries:
        print(f"\n==================================================")
        print(f"QUERY: {query}")
        results = retriever.search(query, top_k=2)
        
        if not results:
            print("No relevant chunks found.")
        else:
            for r in results:
                print(f"\n[Source: {r['source']} | Distance: {r['distance']:.4f}]")
                print(f"{r['text']}")
