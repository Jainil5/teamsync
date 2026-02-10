import os
import pandas as pd
import pdfplumber
from docx import Document
from captioning_model import caption_file_content

def describe_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    content = ""

    if ext == ".pdf":
        with pdfplumber.open(filepath) as pdf:
            content = "\n".join(page.extract_text() or "" for page in pdf.pages)

    elif ext == ".docx":
        doc = Document(filepath)
        content = "\n".join(p.text for p in doc.paragraphs)

    elif ext == ".txt":
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

    elif ext == ".csv":
        df = pd.read_csv(filepath, nrows=10)
        info = f"Columns: {', '.join(df.columns)}"
        print(f"\n📄 {os.path.basename(filepath)} → {info}")
        return info

    else:
        print(f"Unsupported file type: {filepath}")
        return None

    words = content.split()
    limited_content = " ".join(words) 

    print(f"{os.path.basename(filepath)} -> {len(words[:500])} words extracted.")
    return limited_content


def describe_all_files(folder_path):
    supported_ext = [".pdf", ".docx", ".txt", ".csv"]
    records = []
    file_id = 1

    for filename in os.listdir(folder_path):
        if any(filename.lower().endswith(ext) for ext in supported_ext):
            filepath = os.path.join(folder_path, filename)
            content = describe_file(filepath)

            if content:
                description = caption_file_content(content)
                records.append({
                    "file_id": file_id,
                    "file_name": filename,
                    "description": description
                })
                print(f"Added: {filename}")
                file_id += 1

    if records:
        df = pd.DataFrame(records)
        df.to_csv("file_descriptions.csv", index=False, encoding="utf-8-sig")
        print("Descriptions saved to: file_descriptions.csv")
    else:
        print("No valid files found.")

    print(f"Total files processed: {len(records)}")
    return records

if __name__ == "__main__":
    folder_path = r"backend/team-documents"
    describe_all_files(folder_path)
