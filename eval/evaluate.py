import os
import sys
import json
from dotenv import load_dotenv

# Ensure backend/src is in path
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_src = os.path.join(base_dir, "backend", "src")
sys.path.append(backend_src)

from retrieve import Retriever
from generate import generate_answer, OPENAI_API_KEY, call_llm

def llm_judge(question, expected, actual):
    """
    Uses an LLM to judge if the actual answer correctly matches the expected answer.
    """
    if OPENAI_API_KEY:
        prompt = f"""You are an expert evaluator.
Compare the ACTUAL ANSWER to the EXPECTED ANSWER for the given QUESTION.
Determine if the actual answer is correct and faithful to the expected answer. 
It does not need to be word-for-word identical, but it must contain the same core facts and not contradict the expected answer.

QUESTION: {question}
EXPECTED ANSWER: {expected}
ACTUAL ANSWER: {actual}

Reply with exactly one word: "CORRECT" or "INCORRECT".
"""
        judgment = call_llm("You are an expert evaluator.", prompt, max_tokens=10)
        return "CORRECT" in judgment.upper()
    else:
        # Fallback to simple keyword/substring overlap since small models make poor judges
        # Very basic check: are key terms from expected answer in the actual answer?
        expected_words = set(w.lower() for w in expected.split() if len(w) > 3)
        actual_lower = actual.lower()
        match_count = sum(1 for w in expected_words if w in actual_lower)
        if len(expected_words) == 0: return True
        return (match_count / len(expected_words)) >= 0.5

def evaluate():
    qa_file = os.path.join(base_dir, "eval", "qa_pairs.json")
    index_file = os.path.join(base_dir, "backend", "faiss_index.bin")
    meta_file = os.path.join(base_dir, "backend", "faiss_meta.json")
    
    with open(qa_file, 'r', encoding='utf-8') as f:
        qa_pairs = json.load(f)
        
    retriever = Retriever(index_file, meta_file)
    
    total = len(qa_pairs)
    retrieval_successes = 0
    generation_successes = 0
    
    print(f"Starting evaluation of {total} questions...")
    
    for i, qa in enumerate(qa_pairs):
        question = qa['question']
        expected_ans = qa['expected_answer']
        expected_src = qa['expected_source']
        
        # Retrieval
        results = retriever.search(question, top_k=3, distance_threshold=1.5)
        retrieved_sources = [r['source'] for r in results]
        
        retrieval_hit = any(expected_src in s for s in retrieved_sources)
        if retrieval_hit:
            retrieval_successes += 1
            
        # Generation
        actual_ans = generate_answer(question, results)
        gen_hit = llm_judge(question, expected_ans, actual_ans)
        if gen_hit:
            generation_successes += 1
            
        print(f"Q{i+1}: {question}")
        print(f"  Retrieval: {'PASS' if retrieval_hit else 'FAIL'} (Expected: {expected_src})")
        print(f"  Generation: {'PASS' if gen_hit else 'FAIL'}")
        
    print("\n--- FINAL EVALUATION RESULTS ---")
    retrieval_score = (retrieval_successes / total) * 100
    generation_score = (generation_successes / total) * 100
    print(f"Retrieval Accuracy (Top-3): {retrieval_score:.2f}% ({retrieval_successes}/{total})")
    print(f"Generation Faithfulness:    {generation_score:.2f}% ({generation_successes}/{total})")

if __name__ == "__main__":
    evaluate()
