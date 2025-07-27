# 🧠 Smart Document Finder  
**Offline NLP-Based Desktop Search Application**

---

## 📝 Introduction

In today’s digital world, users store thousands of documents—notes, assignments, research papers, and more. But when it's time to find something specific, they forget filenames or folder paths.

**Smart Document Finder** solves this problem using AI-powered semantic search. You can search using plain English like:

> "Give me notes on transformers from last semester."

This desktop app works **fully offline**, respects user privacy, and supports fast, contextual search over PDFs, Word, and text files.

---

## ✨ Features

- 🔍 Natural language search (no need to remember file names)
- 📂 Works with PDFs, Word docs, and images (OCR)
- 🧠 Uses AI (NLP) for semantic understanding
- ⚡ Fast & accurate results even with 10,000+ files
- 🔒 100% private and offline
- 🖥️ Cross-platform desktop app (built with Tauri + React)

---

## ❓ Why Traditional Search Fails

| 🔎 Traditional Search | 🚀 Smart Document Finder |
|----------------------|--------------------------|
| Needs exact filename | Understands English queries |
| Matches only keywords | Uses semantic meaning |
| No context | Shows content snippets |
| May upload to cloud | Fully local & private |

---

## ⚙️ How It Works

```plaintext
1. User starts the app
2. Accepts Terms & Conditions
3. Scanner reads documents & extracts text
4. Text is chunked & converted into embeddings
5. FAISS + SQLite indexes are built
6. User enters a natural language query
7. Query is embedded & matched with stored chunks
8. Matching results are ranked and returned
