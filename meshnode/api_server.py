from fastapi import FastAPI, Request, HTTPException
from meshnode.auth import verify_api_key, get_api_role
from meshnode.logger import log_action
from meshnode.utils import run_with_timeout, TimeoutException
from meshnode.config import load_config
from meshnode.device import device_registry, load_devices

app = FastAPI()
config = load_config()

@app.get("/devices")
async def list_devices(request: Request):
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    devices = []
    for device_id, device in device_registry.items():
        devices.append({
            "device_id": device_id,
            "type": device.__class__.__name__
        })

    return {"devices": devices}

@app.get("/devices/{device_id}/capabilities")
async def get_device_capabilities(device_id: str, request: Request):
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    device = device_registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    return {
        "device_id": device_id,
        "capabilities": device.get_capabilities()
    }

@app.post("/execute-action")
async def execute_action(request: Request):
    data = await request.json()
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    device_id = data.get("device_id")
    action = data.get("action")
    params = data.get("params", {})
    dry_run = data.get("dry_run", False)

    device = device_registry.get(device_id)
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    if device.allowed_api_keys and api_key not in device.allowed_api_keys:
        raise HTTPException(status_code=403, detail="API key not allowed for this device")

    try:
        if dry_run:
            log_action(device_id, action, params, success=True, dry_run=True)
            return {"status": "dry-run", "message": "Dry run simulated — no action executed"}
        else:
            result = run_with_timeout(device.execute_action, args=(action, params), timeout_sec=3)
            log_action(device_id, action, params, success=True)
            return {"status": "success", "result": result}
    except TimeoutException as te:
        log_action(device_id, action, params, success=False, error=str(te))
        raise HTTPException(status_code=504, detail=str(te))
    except Exception as e:
        log_action(device_id, action, params, success=False, error=str(e))
        raise HTTPException(status_code=500, detail=f"Execution failed: {e}")

@app.post("/reload-devices")
async def reload_devices(request: Request):
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    load_devices()
    return {"status": "reloaded", "device_count": len(device_registry)}

@app.get("/mesh-status")
async def mesh_status(request: Request):
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    peers = app.state.mesh_peers if "mesh_peers" in app.state.__dict__ else {}

    return {
        "meshnode_id": config["meshnode_id"],
        "local_devices": [
            {
                "device_id": device_id,
                "type": device.__class__.__name__,
                "capabilities": device.get_capabilities()
            } for device_id, device in device_registry.items()
        ],
        "known_peers": peers
    }

@app.get("/api/logs")
async def api_logs(request: Request):
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    try:
        with open("logs/meshnode.log", "r") as f:
            lines = f.readlines()[-50:]
    except Exception as e:
        lines = [f"Error reading log: {e}"]

    return {"logs": lines}

@app.post("/register-peer")
async def register_peer(request: Request):
    data = await request.json()
    api_key = request.headers.get("x-api-key")
    if not verify_api_key(api_key):
        raise HTTPException(status_code=403, detail="Unauthorized")

    peer_id = data.get("peer_id")
    peer_url = data.get("peer_url")
    peer_devices = data.get("devices", [])

    if "mesh_peers" not in app.state.__dict__:
        app.state.mesh_peers = {}

    app.state.mesh_peers[peer_id] = {
        "url": peer_url,
        "devices": peer_devices
    }

    print(f"[MeshNode] Registered peer: {peer_id} at {peer_url} with {len(peer_devices)} devices.")

    return {"status": "peer-registered", "peer_id": peer_id}
