# meshnode/gpt_agent.py

import os
import requests
import time
import json

from mesh_cloud_client import MeshCloudClient
from memory_store import MemoryStore
from security_layer import SecurityLayer
from audit_log import AuditLog
from driver_registry import DriverRegistry
from signer import load_private_key, sign_payload

# CONFIG
MESH_URL = "http://localhost:9000"
AGENT_INTERVAL = 5  # seconds
LLM_BACKEND = "openai"  # or "ollama" or "custom"

# LLM adapter selection
if LLM_BACKEND == "openai":
    from llm_client_openai import LLMClient
elif LLM_BACKEND == "ollama":
    from llm_client_ollama import LLMClient
elif LLM_BACKEND == "custom":
    from llm_client_custom import LLMClient
else:
    raise ValueError("Unknown backend")

# INIT core objects
llm = LLMClient(model="gpt-4o", backend=LLM_BACKEND)
cloud_client = MeshCloudClient()
memory_store = MemoryStore()
security_layer = SecurityLayer()
audit_log = AuditLog()
driver_registry = DriverRegistry()

# Load keys 🚀
node_id = os.getenv("MESH_NODE_ID", "meshnode-001")
private_key = load_private_key()

# Dynamic driver loading based on environment
MESH_ENV = os.getenv("MESH_ENV", "dev")  # default to dev

if MESH_ENV == "pi":
    from drivers.relay_driver import RelayDriver
    driver_registry.register_driver("relay1", RelayDriver(pin=17))
    print("[GPTAgent] Loaded RelayDriver (Pi mode)")

elif MESH_ENV == "dev":
    from drivers.dummy_driver import DummyDriver
    driver_registry.register_driver("dummy1", DummyDriver())
    print("[GPTAgent] Loaded DummyDriver (Dev mode)")

else:
    raise RuntimeError(f"Unknown MESH_ENV: {MESH_ENV}")

# Helper: Fetch manifest from node
def fetch_node_manifest(node_url):
    try:
        manifest_resp = requests.get(f"{node_url}/manifest", timeout=5)
        if manifest_resp.status_code == 200:
            manifest = manifest_resp.json()
            return manifest
        else:
            print(f"[GPTAgent] Failed to fetch manifest from {node_url} (status {manifest_resp.status_code})")
            return None
    except Exception as e:
        print(f"[GPTAgent] ERROR fetching manifest from {node_url}: {e}")
        return None

# LOOP
while True:
    try:
        # 1️⃣ Get global mesh node registry
        try:
            nodes_response = requests.get(f"{MESH_URL}/nodes", timeout=5)
            global_mesh = nodes_response.json().get("nodes", {})
            print(f"[GPTAgent] Global Mesh: {list(global_mesh.keys())}")
        except Exception as e:
            print(f"[GPTAgent] ERROR fetching global mesh: {e}")
            global_mesh = {}

        # 1️⃣.6 Fetch node manifests
        mesh_manifests = {}

        for node_id_loop, node_info in global_mesh.items():
            node_url_loop = node_info.get("url")
            if node_url_loop:
                manifest = fetch_node_manifest(node_url_loop)
                if manifest:
                    mesh_manifests[node_id_loop] = manifest

        print(f"[GPTAgent] Fetched {len(mesh_manifests)} node manifests")

        # 2️⃣ Build device capability summary
        device_capability_summary = json.dumps(driver_registry.list_capabilities(), indent=2)

        # 2️⃣.6 Register this node with CloudMesh (SIGNED)
        node_url = os.getenv("MESH_NODE_URL", "http://localhost:8000")

        registration_payload = {
            "capabilities": driver_registry.get_capability_schema(),
            "url": node_url
        }

        signed_registration = sign_payload(node_id, private_key, registration_payload)

        try:
            reg_response = requests.post(f"{MESH_URL}/register_node", json=signed_registration, timeout=5)
            if reg_response.status_code == 200:
                print(f"[GPTAgent] Registered with CloudMesh as {node_id} ({node_url})")
            else:
                print(f"[GPTAgent] Failed to register node (status {reg_response.status_code})")
        except Exception as e:
            print(f"[GPTAgent] ERROR registering node: {e}")

        # 2️⃣.5 Build recent action history
        recent_actions = memory_store.get_recent_memories(limit=10)
        action_history = "\n".join(recent_actions)

        # 3️⃣ Build prompt
        messages = [
            {"role": "system", "content": "You are an intelligent agent that controls IoT devices via a mesh network."},
            {"role": "system", "content": "Here is a history of recent actions you performed. Do not repeat the same action unnecessarily."},
            {"role": "system", "content": f"Recent action history:\n{action_history}"},
            {"role": "system", "content": "Respond ONLY in this JSON format: { \"action\": string, \"target_device\": string, \"target_node\": string, \"parameters\": object }"},
            {"role": "system", "content": f"Global mesh node registry:\n{json.dumps(global_mesh, indent=2)}"},
            {"role": "system", "content": f"Global mesh node manifests:\n{json.dumps(mesh_manifests, indent=2)}"},
            {"role": "user", "content": "What action should be performed next?"}
        ]

        # 4️⃣ Chat
        reply = llm.chat(messages)
        print(f"[GPTAgent] Raw GPT reply → {reply}")

        # 5️⃣ Parse structured action
        action = json.loads(reply)

        if "parameters" not in action:
            action["parameters"] = {}
        if "target_node" not in action:
            action["target_node"] = node_id

        # 6️⃣ Execute pipeline
        if action["target_node"] == node_id:
            driver = driver_registry.get_driver(action["target_device"])
            if driver:
                if security_layer.approve(action):
                    print(f"[GPTAgent] Executing LOCAL action on {node_id}")
                    driver.execute(action["action"], action["parameters"])
                    audit_log.store(action)
                else:
                    print("[GPTAgent] Action blocked by security layer")
            else:
                print(f"[GPTAgent] Unknown device: {action['target_device']}")
        else:
            target_node_id = action["target_node"]

            if target_node_id in global_mesh:
                target_node_url = global_mesh[target_node_id].get("url", None)
                shared_secret = os.getenv("MESH_SHARED_SECRET", "")

                if target_node_url:
                    print(f"[GPTAgent] Sending CROSS-NODE action to {target_node_id} at {target_node_url}/execute_action")
                    cross_node_response = requests.post(
                        f"{target_node_url}/execute_action",
                        json=action,
                        headers={"x-mesh-token": shared_secret},
                        timeout=5
                    )
                    if cross_node_response.status_code == 200:
                        print(f"[GPTAgent] CROSS-NODE action SUCCESS")
                    else:
                        print(f"[GPTAgent] CROSS-NODE action FAILED (status {cross_node_response.status_code})")
                else:
                    print(f"[GPTAgent] No URL found for target_node {target_node_id}")
            else:
                print(f"[GPTAgent] Unknown target_node {target_node_id}")

        # 7️⃣ Store memory
        new_memory = json.dumps(action)
        memory_store.add_memory(new_memory)
        cloud_client.log_memory(new_memory)

        # Log action to CloudMesh (SIGNED)
        log_payload = {
            "action": action
        }
        signed_log = sign_payload(node_id, private_key, log_payload)

        try:
            log_response = requests.post(f"{MESH_URL}/log_action", json=signed_log, timeout=5)
            if log_response.status_code == 200:
                print(f"[GPTAgent] Logged action to CloudMesh")
            else:
                print(f"[GPTAgent] Failed to log action to CloudMesh (status {log_response.status_code})")
        except Exception as e:
            print(f"[GPTAgent] ERROR logging action to CloudMesh: {e}")

        # 8️⃣ Send heartbeat (SIGNED)
        heartbeat_payload = {}
        signed_heartbeat = sign_payload(node_id, private_key, heartbeat_payload)

        try:
            hb_response = requests.post(f"{MESH_URL}/heartbeat", json=signed_heartbeat, timeout=5)
            if hb_response.status_code == 200:
                print(f"[GPTAgent] Heartbeat sent to CloudMesh")
            else:
                print(f"[GPTAgent] Failed to send heartbeat (status {hb_response.status_code})")
        except Exception as e:
            print(f"[GPTAgent] ERROR sending heartbeat: {e}")

    except Exception as e:
        print(f"[GPTAgent] ERROR: {e}")

    # 9️⃣ Wait
    time.sleep(AGENT_INTERVAL)

