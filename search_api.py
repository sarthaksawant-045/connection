from flask import Flask, request, jsonify
from search import search_documents
from embedder import Embedder

app = Flask(__name__)
embedder = Embedder()  # Ensure model is loaded

@app.route("/search", methods=["GET"])
def search():
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
    return "🔍 Search API is running!"

if __name__ == "__main__":
    print("🚀 Starting Search API on http://127.0.0.1:5002")
    app.run(port=5002)
