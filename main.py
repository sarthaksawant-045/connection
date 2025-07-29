from embedder import Embedder
from search import search_documents

def main():
    print("🧠 Loading embedding model...")
    embedder = Embedder()

    while True:
        query = input("\n🔎 Enter search query (or 'exit'): ").strip()
        if query.lower() in ["exit", "quit"]:
            print("👋 Exiting.")
            break
        if not query:
            print("⚠ Please enter a valid query.")
            continue

        try:
            results = search_documents(query, embedder)
            if not results:
                print("❌ No matching documents found.")
                continue

            print("\n🔍 Top Matches:")
            for i, res in enumerate(results, 1):
                print(f"{i}. 📄 {res['filename']}")
                print(f"   📁 Path: {res['path']}")
                print(f"   🕒 Modified: {res['modified']}")
                print(f"   📦 Type: {res['extension']}\n")

        except Exception as e:
            print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    main()
