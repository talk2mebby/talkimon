# cloudmesh/main.py

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
import json
import time
import os
import requests
import hashlib

app = FastAPI()

# -------------------------------------------------
# 🚀 PLATFORM STATE
# -------------------------------------------------

FEDERATION_REGISTRY_FILE = "federation_registry.json"

def load_federation_registry():
    try:
        with open(FEDERATION_REGISTRY_FILE, "r") as f:
            registry = json.load(f)
            print(f"[CloudMesh Federation] Loaded {len(registry)} federation nodes 🚀")
            return registry
    except Exception as e:
        print(f"[CloudMesh Federation] ERROR loading federation_registry.json: {e}")
        return {}

def save_federation_registry():
    try:
        with open(FEDERATION_REGISTRY_FILE, "w") as f:
            json.dump(federation_registry, f, indent=2)
            print(f"[CloudMesh Federation] Saved federation_registry.json 🚀")
    except Exception as e:
        print(f"[CloudMesh Federation] ERROR saving federation_registry.json: {e}")

federation_registry = load_federation_registry()

governance_token_balances = {}
approval_votes = {}
FEDERATION_QUORUM_THRESHOLD = 0.5

pending_federation_state = {}
federation_state_signatures = {}

api_keys = {}
api_usage_log = {}
api_billing_plans = {}
webhook_registry = {}

# -------------------------------------------------
# 🚀 CORS Middleware
# -------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# 🚀 HEALTH + PLATFORM INFO
# -------------------------------------------------

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "platform": "AI Mesh Cloud",
        "version": "1.0.0",
        "timestamp": time.time()
    }

@app.get("/public_keys")
async def get_public_keys():
    public_keys = {}
    for node_id, node_info in federation_registry.items():
        if node_info.get("approved", False):
            public_keys[node_id] = node_info.get("public_key", "")
    return {
        "public_keys": public_keys,
        "timestamp": time.time()
    }

# -------------------------------------------------
# 🚀 FEDERATION REGISTRY
# -------------------------------------------------

@app.post("/register_mesh_node")
async def register_mesh_node(request: Request):
    body = await request.json()
    node_id = body.get("node_id", "")
    node_url = body.get("node_url", "")
    public_key = body.get("public_key", "")

    if node_id in federation_registry:
        return {"status": "error", "error": "Node already registered"}

    federation_registry[node_id] = {
        "node_url": node_url,
        "public_key": public_key,
        "registered_at": time.time(),
        "approved": False
    }

    save_federation_registry()

    print(f"[CloudMesh Federation] REGISTERED Node {node_id} → pending approval 🚀")

    return {
        "status": "ok",
        "node_id": node_id,
        "approved": False,
        "timestamp": time.time()
    }

@app.post("/approve_mesh_node")
async def approve_mesh_node(request: Request):
    body = await request.json()
    node_id = body.get("node_id", "")

    if node_id not in federation_registry:
        return {"status": "error", "error": "Node not found"}

    federation_registry[node_id]["approved"] = True
    save_federation_registry()

    print(f"[CloudMesh Federation] APPROVED Node {node_id} 🚀")

    return {
        "status": "ok",
        "node_id": node_id,
        "approved": True,
        "timestamp": time.time()
    }

@app.get("/federation_registry")
async def get_federation_registry():
    return {
        "federation_registry": federation_registry,
        "timestamp": time.time()
    }

# -------------------------------------------------
# 🚀 GOVERNANCE → TOKENS + VOTING
# -------------------------------------------------

@app.post("/mint_token")
async def mint_token(request: Request):
    body = await request.json()
    node_id = body.get("node_id", "")
    amount = body.get("amount", 1)

    if node_id not in governance_token_balances:
        governance_token_balances[node_id] = 0

    governance_token_balances[node_id] += amount

    print(f"[CloudMesh Governance] MINTED {amount} token(s) to {node_id} 🚀")

    return {
        "status": "ok",
        "node_id": node_id,
        "new_balance": governance_token_balances[node_id],
        "timestamp": time.time()
    }

@app.post("/vote_approve_mesh_node")
async def vote_approve_mesh_node(request: Request):
    body = await request.json()
    voter_node_id = body.get("voter_node_id", "")
    target_node_id = body.get("target_node_id", "")

    if voter_node_id not in governance_token_balances:
        return {"status": "error", "error": "Voter node has no tokens"}

    if target_node_id not in federation_registry:
        return {"status": "error", "error": "Target node not found"}

    if target_node_id not in approval_votes:
        approval_votes[target_node_id] = {}

    approval_votes[target_node_id][voter_node_id] = governance_token_balances[voter_node_id]

    print(f"[CloudMesh Governance] VOTE → {voter_node_id} voted to approve {target_node_id} 🚀")

    total_supply = sum(governance_token_balances.values())
    votes_for = sum(approval_votes[target_node_id].values())
    quorum_required = max(1, int(total_supply * FEDERATION_QUORUM_THRESHOLD))

    if votes_for >= quorum_required:
        federation_registry[target_node_id]["approved"] = True
        save_federation_registry()
        print(f"[CloudMesh Governance] APPROVED {target_node_id} via token vote 🚀")
        return {
            "status": "ok",
            "result": "APPROVED",
            "target_node_id": target_node_id,
            "votes_for": votes_for,
            "total_supply": total_supply,
            "timestamp": time.time()
        }

    return {
        "status": "ok",
        "result": "VOTED",
        "target_node_id": target_node_id,
        "votes_for": votes_for,
        "total_supply": total_supply,
        "timestamp": time.time()
    }

@app.get("/governance_state")
async def get_governance_state():
    return {
        "governance_token_balances": governance_token_balances,
        "approval_votes": approval_votes,
        "timestamp": time.time()
    }
    
# -------------------------------------------------
# 🚀 FEDERATED SIGNING
# -------------------------------------------------

@app.post("/propose_federation_state")
async def propose_federation_state(request: Request):
    body = await request.json()
    node_id = body.get("node_id", "")
    proposed_state = body.get("state", {})
    signature_b64 = body.get("signature", "")

    if node_id not in federation_registry or not federation_registry[node_id].get("approved", False):
        return {"status": "error", "error": "Node not approved"}

    public_b64 = federation_registry[node_id].get("public_key", "")
    pubkey_bytes = base64.b64decode(public_b64)
    pubkey = ed25519.Ed25519PublicKey.from_public_bytes(pubkey_bytes)

    proposed_json = json.dumps(proposed_state, separators=(',', ':'), sort_keys=True).encode("utf-8")
    signature_bytes = base64.b64decode(signature_b64)

    try:
        pubkey.verify(signature_bytes, proposed_json)
    except Exception as e:
        print(f"[CloudMesh BFT] Signature verification failed for {node_id}: {e}")
        return {"status": "error", "error": "Invalid signature"}

    state_hash = base64.b64encode(hashlib.sha256(proposed_json).digest()).decode("utf-8")

    pending_federation_state[state_hash] = proposed_state

    if state_hash not in federation_state_signatures:
        federation_state_signatures[state_hash] = {}

    federation_state_signatures[state_hash][node_id] = signature_b64

    print(f"[CloudMesh BFT] RECEIVED SIGNATURE from {node_id} → state_hash: {state_hash} 🚀")

    approved_nodes = [nid for nid, info in federation_registry.items() if info.get("approved", False)]
    quorum_count = len(approved_nodes)
    signatures_count = len(federation_state_signatures[state_hash])

    quorum_required = max(1, int(quorum_count * FEDERATION_QUORUM_THRESHOLD))

    if signatures_count >= quorum_required:
        print(f"[CloudMesh BFT] QUORUM REACHED → state_hash: {state_hash} 🚀")

        return {
            "status": "ok",
            "result": "QUORUM_REACHED",
            "state_hash": state_hash,
            "signatures_count": signatures_count,
            "quorum_required": quorum_required,
            "timestamp": time.time()
        }

    return {
        "status": "ok",
        "result": "SIGNATURE_ACCEPTED",
        "state_hash": state_hash,
        "signatures_count": signatures_count,
        "quorum_required": quorum_required,
        "timestamp": time.time()
    }

@app.get("/pending_federation_states")
async def get_pending_federation_states():
    return {
        "pending_federation_states": pending_federation_state,
        "federation_state_signatures": federation_state_signatures,
        "timestamp": time.time()
    }

# -------------------------------------------------
# 🚀 BILLING + WEBHOOKS
# -------------------------------------------------

@app.get("/api_usage")
async def get_api_usage():
    return {
        "api_usage_log": api_usage_log,
        "timestamp": time.time()
    }

@app.get("/api_billing")
async def get_api_billing():
    return {
        "api_billing_plans": api_billing_plans,
        "timestamp": time.time()
    }

@app.post("/set_api_billing_plan")
async def set_api_billing_plan(request: Request):
    body = await request.json()
    api_key_id = body.get("api_key_id", "")
    plan_name = body.get("plan_name", "free")
    monthly_quota = body.get("monthly_quota", 1000)

    if api_key_id not in api_keys:
        return {"status": "error", "error": "Invalid API key ID"}

    api_billing_plans[api_key_id] = {
        "plan_name": plan_name,
        "monthly_quota": monthly_quota,
        "used_this_month": 0,
        "billing_cycle_start": time.time()
    }

    print(f"[CloudMesh Billing] SET plan for API key {api_key_id} → {plan_name} 🚀")

    return {
        "status": "ok",
        "api_key_id": api_key_id,
        "plan_name": plan_name,
        "monthly_quota": monthly_quota,
        "timestamp": time.time()
    }

@app.post("/register_webhook")
async def register_webhook(request: Request):
    body = await request.json()
    api_key_id = body.get("api_key_id", "")
    webhook_url = body.get("webhook_url", "")

    if api_key_id not in api_keys:
        return {"status": "error", "error": "Invalid API key ID"}

    if api_key_id not in webhook_registry:
        webhook_registry[api_key_id] = []

    webhook_registry[api_key_id].append({
        "webhook_url": webhook_url,
        "registered_at": time.time()
    })

    print(f"[CloudMesh] Registered webhook for API key {api_key_id} → {webhook_url} 🚀")

    return {
        "status": "ok",
        "webhook_url": webhook_url,
        "timestamp": time.time()
    }

# -------------------------------------------------
# 🚀 DYNAMIC DRIVER REGISTRATION
# -------------------------------------------------

@app.post("/register_driver")
async def register_driver(request: Request):
    try:
        from driver_registry import DriverRegistry
        driver_registry = DriverRegistry()

        body = await request.json()
        device_id = body.get("device_id", "")
        capability_schema = body.get("capability_schema", {})

        if not device_id or not capability_schema:
            return {"status": "error", "error": "Missing device_id or capability_schema"}

        driver_registry.register_driver_schema(device_id, capability_schema)

        return {
            "status": "ok",
            "device_id": device_id,
            "registered": True,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# -------------------------------------------------
# 🚀 MESH CAPABILITIES → DYNAMIC DISCOVERY
# -------------------------------------------------

@app.get("/mesh_capabilities")
async def mesh_capabilities():
    try:
        from driver_registry import DriverRegistry
        driver_registry = DriverRegistry()
        from drivers.dummy_driver import DummyDriver
        driver_registry.register_driver("dummy1", DummyDriver())

        capabilities = driver_registry.list_capabilities()

        return {
            "mesh_capabilities": capabilities,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# -------------------------------------------------
# 🚀 CANONICAL ACTION VOCABULARY → OWN THE STANDARD
# -------------------------------------------------

@app.get("/mesh_action_vocab")
async def mesh_action_vocab():
    try:
        from mesh_action_vocab import MESH_ACTION_VOCAB

        return {
            "mesh_action_vocab": MESH_ACTION_VOCAB,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# -------------------------------------------------
# 🚀 MULTI-AI → SUBMIT ACTION PROPOSAL → AI-NEUTRAL
# -------------------------------------------------

@app.post("/submit_action_proposal")
async def submit_action_proposal(request: Request):
    try:
        body = await request.json()

        proposer_id = body.get("proposer_id", "")
        target_device = body.get("target_device", "")
        action_name = body.get("action", "")
        parameters = body.get("parameters", {})
        signature = body.get("signature", "")

        from mesh_action_vocab import MESH_ACTION_VOCAB
        allowed_actions = {a["name"] for a in MESH_ACTION_VOCAB.get("core", [])}

        if action_name not in allowed_actions:
            return {"status": "error", "error": f"Action '{action_name}' not in Mesh Action Vocabulary"}

        print(f"[CloudMesh Multi-AI] Received Action Proposal → proposer: {proposer_id} → device: {target_device} → action: {action_name} → parameters: {parameters} 🚀")

        return {
            "status": "ok",
            "result": "Proposal Accepted",
            "proposer_id": proposer_id,
            "target_device": target_device,
            "action": action_name,
            "parameters": parameters,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

# -------------------------------------------------
# 🚀 MESH EXPLORER → PUBLIC UI → BILLION-DOLLAR API
# -------------------------------------------------

@app.get("/explorer")
async def explorer():
    html = """
    <html>
    <head>
        <title>AI Mesh Explorer 🚀</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; color: #333; }
            h1 { color: #0057e7; }
            a { color: #d62d20; text-decoration: none; }
            a:hover { text-decoration: underline; }
            .section { margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <h1>🌐 AI Mesh Explorer</h1>

        <div class="section">
            <h2>Federation</h2>
            <ul>
                <li><a href="/federation_registry" target="_blank">Federation Registry</a></li>
                <li><a href="/pending_federation_states" target="_blank">Pending Federation States</a></li>
            </ul>
        </div>

        <div class="section">
            <h2>Governance</h2>
            <ul>
                <li><a href="/governance_state" target="_blank">Governance State</a></li>
            </ul>
        </div>

        <div class="section">
            <h2>Billing + Webhooks</h2>
            <ul>
                <li><a href="/api_usage" target="_blank">API Usage</a></li>
                <li><a href="/api_billing" target="_blank">API Billing</a></li>
            </ul>
        </div>

        <div class="section">
            <h2>Mesh API</h2>
            <ul>
                <li><a href="/mesh_capabilities" target="_blank">Mesh Capabilities</a></li>
                <li><a href="/mesh_action_vocab" target="_blank">Mesh Action Vocabulary</a></li>
            </ul>
        </div>

        <div class="section">
            <h2>System</h2>
            <ul>
                <li><a href="/health" target="_blank">Health Check</a></li>
                <li><a href="/public_keys" target="_blank">Public Keys</a></li>
            </ul>
        </div>

        <p style="margin-top:40px; font-size:small; color:#888;">AI Mesh Explorer 🚀 — Platform API 1.0 — Powered by YOUR Mesh 🚀</p>
    </body>
    </html>
    """
    return html
