from flask import Flask, request, jsonify
# from flask_cors import CORS
from search import search_documents

app = Flask(__name__)
# CORS(app)  # Enable CORS

@app.route("/search")
def search():
    query = request.args.get("q", "")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    return jsonify({"results": search_documents(query)})

if __name__ == "__main__":
    app.run(port=5005)  # Search service only