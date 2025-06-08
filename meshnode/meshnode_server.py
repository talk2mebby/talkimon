# meshnode/meshnode_server.py

from fastapi import FastAPI, Request, Header, HTTPException
import time
import os

# Import core components 🚀
from memory_store import MemoryStore
from security_layer import SecurityLayer
from audit_log import AuditLog
from driver_registry import DriverRegistry

# INIT core components 🚀
memory_store = MemoryStore()
security_layer = SecurityLayer()
audit_log = AuditLog()
driver_registry = DriverRegistry()

# For this example we assume dev env:
from drivers.dummy_driver import DummyDriver
driver_registry.register_driver("dummy1", DummyDriver())
print("[MeshNode Server] Loaded DummyDriver (Dev mode)")

# FastAPI server 🚀
app = FastAPI()

# In-memory action log
action_log = []

# 🚑 HEALTH CHECK 🚑
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "node_id": os.getenv("MESH_NODE_ID", "meshnode-001"),
        "version": "1.0.0",
        "timestamp": time.time()
    }

# 🚀 PROTECTED /execute_action 🚀
@app.post("/execute_action")
async def execute_action(req: Request, x_mesh_token: str = Header(None)):
    shared_secret = os.getenv("MESH_SHARED_SECRET", "")

    # AUTH CHECK 🚀
    if x_mesh_token != shared_secret:
        print(f"[MeshNode Server] AUTH FAILED — Invalid token: {x_mesh_token}")
        raise HTTPException(status_code=403, detail="Forbidden — invalid mesh token")

    # AUTH PASSED 🚀
    data = await req.json()
    print(f"[MeshNode Server] Received AUTHORIZED /execute_action: {data}")

    # Log it
    action_log.append({
        "timestamp": time.time(),
        "action": data
    })

    # Ensure "parameters" exists
    if "parameters" not in data:
        data["parameters"] = {}

    # Run driver pipeline 🚀
    driver = driver_registry.get_driver(data["target_device"])
    if driver:
        if security_layer.approve(data):
            print(f"[MeshNode Server] Executing LOCAL action")
            driver.execute(data["action"], data["parameters"])
            audit_log.store(data)
        else:
            print("[MeshNode Server] Action blocked by security layer")
    else:
        print(f"[MeshNode Server] Unknown device: {data['target_device']}")

    return {"status": "ok"}

# ACTION LOG VIEW
@app.get("/actions")
async def get_actions():
    return {"actions": action_log[-10:]}  # Show last 10 actions

# MESH MANIFEST ENDPOINT
@app.get("/manifest")
async def get_manifest():
    return {
        "node_id": os.getenv("MESH_NODE_ID", "meshnode-001"),
        "version": "1.0.0",
        "capabilities": driver_registry.get_capability_schema(),
        "timestamp": time.time()
    }
