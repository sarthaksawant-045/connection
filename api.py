import os, time, json
from flask import Flask
from embedder import Embedder
from reader import read_file_content
from db import init_db, insert_documents
import faiss, pickle

app = Flask(__name__)

SCAN_DIRS = ["C:\\", "D:\\"]

VALID_EXTS = [
    ".txt", ".pdf", ".docx", ".xlsx", ".xls", ".db",
    ".js", ".py", ".java", ".cpp", ".c",
    ".jpg", ".jpeg", ".png", ".bmp", ".webp"
]

EXCLUDED_DIRS = ["Windows", "Program Files", "ProgramData", ".git", ".venv",
                 "AppData", "System Volume Information", "$RECYCLE.BIN",
                 "node_modules", "__pycache__", ".idea", ".vscode"]

INDEX_PATH = "Aaryan_store/index.faiss"
META_PATH = "Aaryan_store/meta.pkl"

embedder = Embedder()

def should_exclude(path):
    return any(excl.lower() in path.lower() for excl in EXCLUDED_DIRS)

def scan_files():
    files = {}
    print("🔍 Starting file scan...")
    for root in SCAN_DIRS:
        print(f"📁 Scanning {root}")
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not should_exclude(os.path.join(dirpath, d))]
            for file in filenames:
                path = os.path.join(dirpath, file)
                ext = os.path.splitext(file)[1].lower()
                if ext in VALID_EXTS and os.path.exists(path):
                    try:
                        content = read_file_content(path)
                        files[path] = {
                            "filename": file,
                            "path": path,
                            "extension": ext,
                            "size": os.path.getsize(path),
                            "modified": os.path.getmtime(path),
                            "content": content
                        }
                    except:
                        continue
    print(f"✅ File scan complete. Total valid files found: {len(files)}")
    return files

def index_documents(documents: dict):
    texts = [v["content"] if v["content"] else v["filename"] for v in documents.values()]
    paths = list(documents.keys())

    print(f"🧠 Starting embedding for {len(texts)} documents...")
    vectors = embedder.embed_texts(texts)
    print("✅ Embedding complete.")

    faiss.normalize_L2(vectors)
    index = faiss.IndexFlatIP(vectors.shape[1])
    index.add(vectors)

    os.makedirs(os.path.dirname(INDEX_PATH), exist_ok=True)
    faiss.write_index(index, INDEX_PATH)
    with open(META_PATH, "wb") as f:
        pickle.dump(paths, f)

    print(f"✅ FAISS index saved to '{INDEX_PATH}'. Total documents indexed: {len(paths)}")

@app.route("/")
def index():
    return "📁 Scanner + Indexer is running!"

if __name__ == "__main__":
    init_db()
    print("📡 Starting full scan + index process...")
    docs = scan_files()
    if not docs:
        print("⚠️ No valid files to index.")
    else:
        inserted = insert_documents(docs)
        print(f"🗃 Metadata inserted into DB: {inserted}")
        index_documents(docs)
    app.run(port=5001)
