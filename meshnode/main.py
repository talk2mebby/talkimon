from meshnode.api_server import app
import uvicorn
import threading
import time
import requests
from meshnode.device import device_registry
from meshnode.config import load_config
from meshnode.peer_discovery import start_advertising, start_discovery
from meshnode.agent import MeshBrainAgent  # <--- NEW!

config = load_config()
CONTROLLER_URLS = config.get("peers", [])

def register_with_peers():
    while True:
        try:
            devices = []
            for device_id, device in device_registry.items():
                devices.append({
                    "device_id": device_id,
                    "type": device.__class__.__name__
                })

            payload = {
                "peer_id": config["meshnode_id"],
                "peer_url": "http://localhost:8000",  # can be dynamic
                "devices": devices
            }

            headers = {"x-api-key": config["api_keys"][0]}

            for peer_url in CONTROLLER_URLS:
                try:
                    r = requests.post(f"{peer_url}/register-peer", json=payload, headers=headers, timeout=2)
                    print(f"[MeshNode] Peer sync → {peer_url}: {r.status_code}")
                except Exception as e:
                    print(f"[MeshNode] Peer sync failed → {peer_url}: {e}")

        except Exception as e:
            print(f"[MeshNode] Peer sync loop error: {e}")

        time.sleep(10)

if __name__ == "__main__":
    start_advertising(config["meshnode_id"], 8000)

    def on_peer_found(peer_url):
        print(f"[MeshNode] DISCOVERED PEER: {peer_url}")

    t_discovery = threading.Thread(target=start_discovery, args=(on_peer_found,), daemon=True)
    t_discovery.start()

    t_peers = threading.Thread(target=register_with_peers, daemon=True)
    t_peers.start()

    # Start Mesh Brain agent
    brain = MeshBrainAgent()
    brain.start()

    uvicorn.run(app, host="0.0.0.0", port=8000)

