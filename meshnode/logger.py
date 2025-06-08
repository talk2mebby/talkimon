from datetime import datetime
import json
import os
import requests

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "meshnode.log")
os.makedirs(LOG_DIR, exist_ok=True)

LOGGING_URL = os.environ.get("LOGGING_URL", None)

def log_action(device_id, action, params, success, error=None, dry_run=False):
    timestamp = datetime.utcnow().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "device_id": device_id,
        "action": action,
        "params": params,
        "success": success,
        "error": error,
        "dry_run": dry_run
    }
    print(log_entry)
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log_entry) + "\n")
    if LOGGING_URL:
        try:
            requests.post(LOGGING_URL, json=log_entry, timeout=2)
        except Exception as e:
            print(f"[WARN] Cloud log failed: {e}")
