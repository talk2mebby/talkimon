# meshnode/mesh_cloud_client.py
import requests

class MeshCloudClient:
    def __init__(self, cloud_url="http://localhost:9000"):
        self.cloud_url = cloud_url

    def log_memory(self, memory):
        try:
            requests.post(f"{self.cloud_url}/log_memory", json={"memory": memory}, timeout=5)
        except Exception as e:
            print(f"[MeshCloudClient] ERROR logging memory: {e}")

    def fetch_memory(self):
        try:
            resp = requests.get(f"{self.cloud_url}/memory", timeout=5)
            if resp.status_code == 200:
                return resp.json().get("memories", [])
            else:
                return []
        except Exception as e:
            print(f"[MeshCloudClient] ERROR fetching memory: {e}")
            return []
