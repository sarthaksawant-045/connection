from flask import Flask, request, jsonify
from embedder import Embedder
from search import search_documents
from db import init_db, insert_documents
from api import scan_files, index_documents
import os
import pickle

app = Flask(__name__)
embedder = Embedder()

INDEX_PATH = "Aaryan_store/index.faiss"
META_PATH = "Aaryan_store/meta.pkl"

# ✅ Track T&C acceptance in memory
ACCEPTED = {"user": False}

@app.route("/accept", methods=["POST"])
def accept_terms():
    data = request.get_json()
    if not data or not data.get("accepted"):
        return jsonify({"error": "Terms not accepted"}), 400

    ACCEPTED["user"] = True
    print("✅ Terms accepted. Starting scan...")

    init_db()
    docs = scan_files()
    if not docs:
        return jsonify({"message": "⚠ No valid files found to index."})
    inserted = insert_documents(docs)
    index_documents(docs)
    return jsonify({"message": f"✅ Scan complete. Indexed: {inserted} files"})

@app.route("/status")
def check_status():
    return jsonify({
        "termsAccepted": ACCEPTED["user"],
        "indexExists": os.path.exists(INDEX_PATH) and os.path.exists(META_PATH)
    })

@app.route("/search", methods=["GET"])
def search():
    if not ACCEPTED["user"]:
        return jsonify({"error": "Terms not accepted"}), 403

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"error": "No query provided"}), 400

    try:
        results = search_documents(query, embedder)
        return jsonify({"results": results})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def root():
    return "📁 Document Finder API running. Awaiting T&C acceptance."

if __name__ == "__main__":
    app.run(port=5000)
