import os
import json
import tiktoken
import re

# We use cl100k_base which is standard for openai models (gpt-3.5, gpt-4)
tokenizer = tiktoken.get_encoding("cl100k_base")

def get_tokens(text):
    return tokenizer.encode(text)

def chunk_text(text, source, max_tokens=600, overlap=100):
    """
    Chunks text by sentences to try and keep chunks between ~500-800 tokens,
    with an overlap of ~100 tokens.
    """
    # Simple regex to split by sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    chunks = []
    current_chunk_sentences = []
    current_token_count = 0
    
    for sentence in sentences:
        sentence_tokens = len(get_tokens(sentence))
        
        # If a single sentence is larger than max_tokens, we still add it (or we could hard split it, but rare)
        if current_token_count + sentence_tokens > max_tokens and current_chunk_sentences:
            # Finalize current chunk
            chunk_text = " ".join(current_chunk_sentences)
            chunks.append(chunk_text)
            
            # Create overlap: keep removing from start of current_chunk_sentences until we are under `overlap` tokens
            # Wait, overlap means we want the NEW chunk to start with the last ~100 tokens of the previous chunk.
            overlap_sentences = []
            overlap_tokens = 0
            for s in reversed(current_chunk_sentences):
                s_toks = len(get_tokens(s))
                if overlap_tokens + s_toks <= overlap:
                    overlap_sentences.insert(0, s)
                    overlap_tokens += s_toks
                else:
                    # if we can't fit a full sentence into the overlap, just stop
                    if not overlap_sentences:
                        overlap_sentences.insert(0, s) # take at least one sentence
                        overlap_tokens += s_toks
                    break
            
            current_chunk_sentences = overlap_sentences
            current_token_count = overlap_tokens
            
        current_chunk_sentences.append(sentence)
        current_token_count += sentence_tokens
        
    # Add the last chunk
    if current_chunk_sentences:
        chunks.append(" ".join(current_chunk_sentences))
        
    # Format chunks with metadata
    formatted_chunks = []
    for i, c in enumerate(chunks):
        formatted_chunks.append({
            "chunk_id": f"{source}_chunk_{i}",
            "source": source,
            "text": c,
            "token_count": len(get_tokens(c))
        })
        
    return formatted_chunks

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    input_file = os.path.join(base_dir, "backend", "parsed_docs.json")
    output_file = os.path.join(base_dir, "backend", "chunks.json")
    
    with open(input_file, 'r', encoding='utf-8') as f:
        docs = json.load(f)
        
    all_chunks = []
    for doc in docs:
        print(f"Chunking {doc['source']}...")
        doc_chunks = chunk_text(doc['text'], doc['source'], max_tokens=700, overlap=100)
        all_chunks.extend(doc_chunks)
        print(f"  -> Generated {len(doc_chunks)} chunks.")
        
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_chunks, f, indent=4)
        
    print(f"Total chunks created: {len(all_chunks)}")
    print(f"Saved chunks to {output_file}")
