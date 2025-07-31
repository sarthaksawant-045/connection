from flask import Flask, request, jsonify
from flask_cors import CORS
import os, json, pickle, threading, time, sqlite3, logging
from datetime import datetime

# ---- your modules
from embedder import Embedder
from search import search_documents
from db import init_db, insert_documents, get_all_doc_stats, upsert_document, delete_document
from api import index_documents  # single writer for FAISS
from reader import read_file_content  # to build docs

# -------- Setup logging --------
LOG_FILE = "document_finder.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

app = Flask(__name__)
CORS(app)

# -------- Paths / State
INDEX_PATH = "Aaryan_store/index.faiss"
META_PATH = "Aaryan_store/meta.pkl"
STATE_FILE = "config_state.json"

WATCH_ROOTS = ["C:\\", "D:\\"]

VALID_EXTS = {
    ".txt", ".pdf", ".docx", ".xlsx", ".xls", ".db",
    ".js", ".py", ".java", ".cpp", ".c",
    ".jpg", ".jpeg", ".png", ".bmp", ".webp"
}
EXCLUDED_DIRS = {
    "windows", "program files", "programdata", ".git", ".venv",
    "appdata", "system volume information", "$recycle.bin",
    "node_modules", "__pycache__", ".idea", ".vscode",
    "site-packages", "lib", "dist", "build", ".mypy_cache"
}

embedder = Embedder()

STATE_LOCK = threading.Lock()
STATE = {
    "termsAccepted": False,
    "firstTime": True,
    "job": {"status": "idle", "step": "", "startedAt": None, "endedAt": None, "error": None, "indexed": 0}
}

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                STATE.update(data)
        except Exception:
            pass

def save_state():
    with STATE_LOCK:
        with open(STATE_FILE, "w") as f:
            json.dump({
                "termsAccepted": STATE["termsAccepted"],
                "firstTime": STATE["firstTime"]
            }, f)

load_state()

# -------- Job management
def set_job(status, step="", error=None, indexed=0):
    with STATE_LOCK:
        STATE["job"]["status"]    = status
        STATE["job"]["step"]      = step
        STATE["job"]["error"]     = error
        STATE["job"]["indexed"]   = indexed
        now = datetime.now().isoformat(timespec="seconds")
        if status == "running":
            STATE["job"]["startedAt"] = now
            STATE["job"]["endedAt"]   = None
        elif status in ("done", "error"):
            STATE["job"]["endedAt"]   = now

    logging.info(f"Job {status}: {step} (indexed={indexed}) error={error}")

# -------- Helper functions for smart-rescan
def _allowed_file(path: str) -> bool:
    p = path.lower()
    if not any(p.endswith(ext) for ext in VALID_EXTS):
        return False
    parts = p.split(os.sep)
    return not any(ex in parts for ex in EXCLUDED_DIRS)

def _stat_walk(roots):
    out = {}
    for root in roots:
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if all(ex not in (os.path.join(dirpath, d)).lower() for ex in EXCLUDED_DIRS)]
            for name in filenames:
                path = os.path.join(dirpath, name)
                if not _allowed_file(path):
                    continue
                try:
                    st = os.stat(path)
                except FileNotFoundError:
                    continue
                out[path] = (st.st_size, st.st_mtime)
    return out

def _build_docs_for_paths(paths):
    docs = {}
    for p in paths:
        if not os.path.exists(p) or not _allowed_file(p):
            continue
        try:
            filename = os.path.basename(p)
            ext = os.path.splitext(p)[1].lower()
            st = os.stat(p)
            content = read_file_content(p) or filename
            docs[p] = {
                "filename": filename,
                "path": p,
                "extension": ext,
                "size": st.st_size,
                "modified": st.st_mtime,
                "content": content
            }
        except Exception as e:
            logging.warning(f"Skipped file {p}: {e}")
            continue
    return docs

# -------- Background Jobs
def run_full_scan_bg():
    from api import scan_files
    try:
        set_job("running", step="init-db")
        init_db()

        set_job("running", step="scan-files")
        docs = scan_files()
        if not docs:
            set_job("done", step="scan-files", indexed=0)
            return

        set_job("running", step="insert-db")
        inserted = insert_documents(docs)

        set_job("running", step="index-faiss")
        index_documents(docs)

        with STATE_LOCK:
            STATE["firstTime"] = False
        save_state()

        set_job("done", step="complete", indexed=inserted)
    except Exception as e:
        set_job("error", step="full-scan", error=str(e))

def run_smart_rescan_bg():
    try:
        set_job("running", step="compute-changes")

        db_stats = get_all_doc_stats()
        fs_stats = _stat_walk(WATCH_ROOTS)

        new_paths      = [p for p in fs_stats if p not in db_stats]
        modified_paths = [p for p,(s,m) in fs_stats.items() if p in db_stats and db_stats[p] != (s,m)]
        deleted_paths  = [p for p in db_stats if p not in fs_stats]

        changed_count = len(new_paths) + len(modified_paths) + len(deleted_paths)
        if changed_count == 0:
            set_job("done", step="no-changes", indexed=0)
            return

        set_job("running", step=f"apply-deletes({len(deleted_paths)})")
        for p in deleted_paths:
            delete_document(p)

        existing_paths = set()
        if os.path.exists(META_PATH):
            with open(META_PATH, "rb") as f:
                try:
                    existing_paths = set(pickle.load(f))
                except Exception:
                    existing_paths = set()
        current_paths = (existing_paths - set(deleted_paths)) | set(new_paths) | set(modified_paths)

        set_job("running", step=f"build-docs({len(current_paths)})")
        docs = _build_docs_for_paths(current_paths)

        set_job("running", step="update-db")
        for p, meta in docs.items():
            upsert_document(p, meta["filename"], meta["extension"], meta["size"], meta["modified"], content=meta.get("content",""))

        set_job("running", step=f"index-faiss({len(docs)})")
        index_documents(docs)

        set_job("done", step="smart-rescan", indexed=changed_count)

    except Exception as e:
        set_job("error", step="smart-rescan", error=str(e))

# -------- Task endpoint
@app.route("/task", methods=["POST", "OPTIONS"])
def task():
    if request.method == "OPTIONS":
        return ("", 204)

    data = request.get_json(silent=True) or {}
    action = (data.get("action") or "").strip().lower()

    if action == "accept":
        with STATE_LOCK:
            STATE["termsAccepted"] = True
        save_state()

        need_full_scan = STATE["firstTime"] or not (os.path.exists(INDEX_PATH) and os.path.exists(META_PATH))
        if need_full_scan and STATE["job"]["status"] != "running":
            threading.Thread(target=run_full_scan_bg, daemon=True).start()
            return jsonify({"ok": True, "message": "Terms accepted. Full scan started in background."})

        return jsonify({"ok": True, "message": "Terms accepted. Index already exists."})

    elif action == "search":
        if not STATE["termsAccepted"]:
            return jsonify({"ok": False, "error": "Terms not accepted"}), 403
        q = (data.get("q") or "").strip()
        if not q:
            return jsonify({"ok": False, "error": "No query provided"}), 400

        try:
            results = search_documents(q, embedder)
            return jsonify({"ok": True, "results": results})
        except Exception as e:
            return jsonify({"ok": False, "error": str(e)}), 500

    elif action == "smart-rescan":
        if not STATE["termsAccepted"]:
            return jsonify({"ok": False, "error": "Terms not accepted"}), 403
        if STATE["job"]["status"] == "running":
            return jsonify({"ok": False, "message": "Another job running"}), 409

        threading.Thread(target=run_smart_rescan_bg, daemon=True).start()
        return jsonify({"ok": True, "message": "Smart Rescan started"})

    elif action == "status":
        with STATE_LOCK:
            return jsonify({
                "ok": True,
                "termsAccepted": STATE["termsAccepted"],
                "firstTime": STATE["firstTime"],
                "indexExists": os.path.exists(INDEX_PATH) and os.path.exists(META_PATH),
                "job": STATE["job"]
            })

    else:
        return jsonify({"ok": False, "error": f"Unknown action: {action}"}), 400

@app.route("/", methods=["POST"])
def root():
    return jsonify({"message": "📁 Document Finder API running."})

if __name__ == "__main__":
    print(f"\n🚀 Starting Document Finder at {datetime.now().isoformat(timespec='seconds')}")
    logging.info("Application started")

    # 🔁 Start real-time file monitoring
    from file_watcher import start_file_watch
    threading.Thread(target=start_file_watch, daemon=True).start()

    # 🔹 Automatically trigger Smart Rescan at startup if index exists
    if STATE["termsAccepted"] and os.path.exists(INDEX_PATH) and os.path.exists(META_PATH):
        logging.info("Running Smart Rescan at startup...")
        threading.Thread(target=run_smart_rescan_bg, daemon=True).start()

    app.run(port=5000)
