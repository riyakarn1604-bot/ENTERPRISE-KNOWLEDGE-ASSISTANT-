import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def build_index(chunks_file, index_file, meta_file):
    if not os.path.exists(chunks_file):
        print(f"Chunks file {chunks_file} not found.")
        return

    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
        
    if not chunks:
        print("No chunks to embed.")
        return

    print("Loading SentenceTransformer model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    texts = [chunk['text'] for chunk in chunks]
    
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)
    
    # SentenceTransformers outputs float32 numpy arrays by default, which FAISS needs.
    dimension = embeddings.shape[1]
    
    print(f"Building FAISS index with dimension {dimension}...")
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings))
    
    # Save the index
    faiss.write_index(index, index_file)
    print(f"Saved FAISS index to {index_file}")
    
    # Save the metadata (mapping from index ID to chunk data)
    # The index in FAISS corresponds to the index in this list.
    with open(meta_file, 'w', encoding='utf-8') as f:
        json.dump(chunks, f, indent=4)
    print(f"Saved metadata to {meta_file}")

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    chunks_file = os.path.join(base_dir, "backend", "chunks.json")
    index_file = os.path.join(base_dir, "backend", "faiss_index.bin")
    meta_file = os.path.join(base_dir, "backend", "faiss_meta.json")
    
    build_index(chunks_file, index_file, meta_file)
