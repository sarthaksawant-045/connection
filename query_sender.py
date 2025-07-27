from search import search_documents

def send_query(query, top_k=5):  # ✅ Accept top_k argument here
    return search_documents(query, top_k=top_k)
