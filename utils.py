# utils.py
def format_results(results):
    if not results:
        return "❌ No matching files found."

    output = []
    for idx, item in enumerate(results, 1):
        output.append(
            f"{idx}. 📄 {item['filename']}\n"
            f"   📁 Path: {item['path']}\n"
            f"   🕒 Modified: {item['modified']}\n"
            f"   📦 Type: {item['filetype']}\n"
        )
    return "\n".join(output)
