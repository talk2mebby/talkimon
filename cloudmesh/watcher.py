# cloudmesh/watcher.py

import time
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os

# Import these from main.py
from main import load_public_keys, public_keys_ref, AUTHORIZED_KEYS_FILE

class KeyFileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        # Normalize path
        changed_path = os.path.abspath(event.src_path)
        watch_path = os.path.abspath(AUTHORIZED_KEYS_FILE)

        if changed_path == watch_path:
            print("[CloudMesh] Detected authorized_keys.json change → reloading keys...")
            public_keys_ref["keys"] = load_public_keys()

def start_key_watcher():
    observer = Observer()
    event_handler = KeyFileChangeHandler()

    # Watch the directory containing the file
    watch_dir = os.path.dirname(AUTHORIZED_KEYS_FILE) or "."
    observer.schedule(event_handler, path=watch_dir, recursive=False)
    observer.start()
    print("[CloudMesh] Key watcher started 🚀")

    # Run in background thread
    def run():
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

