import os
import urllib.request
import zipfile
import shutil

DATA_DIR = "C:/Users/Harsh/.gemini/antigravity/scratch/enterprise-knowledge-assistant/data"
SOURCES_FILE = "C:/Users/Harsh/.gemini/antigravity/scratch/enterprise-knowledge-assistant/SOURCES.md"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# URLs of HR policies and Handbooks
HR_URLS = [
    ("SUNY_Employee_Handbook.pdf", "https://www.rfsuny.org/media/rfsuny/policies/Employee-Handbook.pdf"),
    ("MTAR_Code_of_Conduct.pdf", "https://mtar.in/wp-content/uploads/2021/01/Code-of-Conduct.pdf"),
    ("Alaska_Telework_Policy.pdf", "https://doa.alaska.gov/dop/fileadmin/Employee_Relations/pdf/TeleworkPolicy.pdf"),
    ("511_Telework_Policy.pdf", "https://511.org/sites/default/files/pdfs/employers/Telework-Policy-Template.pdf"),
]

PYTHON_DOCS_ZIP = "https://docs.python.org/3/archives/python-3.11.5-docs-pdf-a4.zip"

sources_md = ["# Document Sources\n\nThe following publicly available documents are used in this project:\n"]

# Download HR PDFs
for filename, url in HR_URLS:
    filepath = os.path.join(DATA_DIR, filename)
    print(f"Downloading {filename}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as response, open(filepath, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        sources_md.append(f"- **{filename}**: [{url}]({url})")
    except Exception as e:
        print(f"Failed to download {filename}: {e}")

# Download Python Docs
print("Downloading Python Docs ZIP...")
zip_path = os.path.join(DATA_DIR, "python_docs.zip")
try:
    urllib.request.urlretrieve(PYTHON_DOCS_ZIP, zip_path)
    
    print("Extracting Python Docs...")
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        # Extract a subset of docs
        all_files = zip_ref.namelist()
        pdf_files = [f for f in all_files if f.endswith(".pdf") and not f.startswith("__MACOSX")]
        
        extracted_count = 0
        for pdf_file in pdf_files:
            if extracted_count >= 15:
                break
            # Skip very large or very small ones if desired, but we'll just take the first 15
            zip_ref.extract(pdf_file, DATA_DIR)
            
            # Move out of subdirectory if it's in one
            extracted_path = os.path.join(DATA_DIR, pdf_file)
            base_name = os.path.basename(pdf_file)
            final_path = os.path.join(DATA_DIR, base_name)
            
            if extracted_path != final_path:
                shutil.move(extracted_path, final_path)
            
            sources_md.append(f"- **{base_name}**: Python 3.11.5 Official Documentation (https://docs.python.org/3/)")
            extracted_count += 1
            
    # Cleanup zip and extracted dir if empty
    os.remove(zip_path)
    extract_dir = os.path.join(DATA_DIR, "docs-pdf")
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir, ignore_errors=True)
        
except Exception as e:
    print(f"Failed to process Python Docs: {e}")

with open(SOURCES_FILE, "w", encoding="utf-8") as f:
    f.write("\n".join(sources_md))

print("Data download complete.")
