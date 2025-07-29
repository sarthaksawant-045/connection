import json
import time
import os

def wait_for_scan_complete(status_file="../signals/scan_status.json", timeout=60):
    print("⏳ Waiting for scan to complete...")
    start = time.time()

    while time.time() - start < timeout:
        if os.path.exists(status_file):
            with open(status_file, "r") as f:
                data = json.load(f)
                if data.get("status") == "complete":
                    print("✅ Scan complete signal received.")
                    return True
        time.sleep(2)

    print("⚠ Timed out waiting for scan completion.")
    return False

# Optional standalone run
if __name__ == "_main_":
    wait_for_scan_complete()