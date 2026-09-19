import os
import json
from pypdf import PdfReader

def ingest_documents(data_dir):
    parsed_docs = []
    
    if not os.path.exists(data_dir):
        print(f"Data directory {data_dir} not found.")
        return parsed_docs

    for filename in os.listdir(data_dir):
        filepath = os.path.join(data_dir, filename)
        text = ""
        
        if filename.endswith(".pdf"):
            try:
                reader = PdfReader(filepath)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
            except Exception as e:
                print(f"Error parsing PDF {filename}: {e}")
                
        elif filename.endswith(".txt"):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    text = f.read()
            except Exception as e:
                print(f"Error reading TXT {filename}: {e}")
        else:
            continue
            
        if text.strip():
            word_count = len(text.split())
            print(f"Ingested {filename} - Word count: {word_count}")
            parsed_docs.append({
                "source": filename,
                "text": text.strip()
            })
            
    return parsed_docs

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    data_directory = os.path.join(base_dir, "data")
    output_file = os.path.join(base_dir, "backend", "parsed_docs.json")
    
    print(f"Reading from {data_directory}")
    docs = ingest_documents(data_directory)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(docs, f, indent=4)
        
    print(f"Total documents ingested: {len(docs)}")
    print(f"Saved parsed documents to {output_file}")
