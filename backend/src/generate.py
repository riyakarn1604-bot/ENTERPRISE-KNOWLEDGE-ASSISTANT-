import os
import sys
import time
from dotenv import load_dotenv

load_dotenv()

# Check if OpenAI is configured
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

client = None
if OPENAI_API_KEY:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=OPENAI_API_KEY)
        print("OpenAI client initialized — using gpt-4o-mini for generation.")
    except Exception as e:
        print(f"OpenAI initialization failed ({e}); falling back to local fallback.")
        OPENAI_API_KEY = None
        client = None
else:
    print("OPENAI_API_KEY not found. Using local fallback for generation.")

pipe = None

def get_pipeline():
    global pipe
    if pipe is None:
        import torch
        from transformers import pipeline
        print("Loading local TinyLlama fallback model...")
        pipe = pipeline(
            "text-generation",
            model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",
            dtype=torch.bfloat16,
            device_map="auto",
        )
    return pipe

def call_llm(system_prompt, user_prompt, max_tokens=500):
    if OPENAI_API_KEY and client:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return f"Error: {str(e)}"
    else:
        try:
            p = get_pipeline()
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ]
            prompt = p.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            outputs = p(prompt, max_new_tokens=max_tokens if max_tokens <= 200 else 200, do_sample=False)
            return outputs[0]["generated_text"].split("<|assistant|>")[-1].strip()
        except Exception as e:
            print(f"Error using local LLM: {e}")
            return f"Error: {str(e)}"


def generate_answer(query, context_chunks):
    """
    Generates an answer using retrieved context chunks.
    If OpenAI API key is present, uses gpt-4o-mini to synthesize a focused answer.
    Otherwise, returns the highest-ranked chunk text for fast and reliable response.
    """
    if not context_chunks:
        return (
            "I'm sorry, I couldn't find any relevant information in the company documents to answer your question."
        )
    
    if OPENAI_API_KEY and client:
        context_text = "\n\n".join([f"Source: {c['source']}\n{c['text']}" for c in context_chunks])
        system_prompt = (
            "You are a helpful and accurate enterprise knowledge assistant. "
            "Answer the user's question concisely using ONLY the provided context. "
            "If the context does not contain enough information to answer, state that clearly."
        )
        user_prompt = f"Context:\n{context_text}\n\nQuestion: {query}\n\nAnswer:"
        return call_llm(system_prompt, user_prompt)

    # Return the text of the highest-ranked chunk (lowest distance)
    best_chunk = min(context_chunks, key=lambda c: c.get('distance', float('inf')))
    return best_chunk['text']



if __name__ == "__main__":
    from retrieve import Retriever

    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    index_file = os.path.join(base_dir, "backend", "faiss_index.bin")
    meta_file = os.path.join(base_dir, "backend", "faiss_meta.json")

    if not os.path.exists(index_file) or not os.path.exists(meta_file):
        print("FAISS index or metadata not found. Please run embed.py first.")
        sys.exit(1)

    retriever = Retriever(index_file, meta_file)
    for q in ["How many days of annual leave do I get?"]:
        results = retriever.search(q, top_k=2)
        answer = generate_answer(q, results)
        print(f"\nQUERY: {q}\nANSWER:\n{answer}")
