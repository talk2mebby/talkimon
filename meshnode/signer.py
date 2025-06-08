# meshnode/signer.py

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization
import base64
import json

# Load private key from PEM 🚀
def load_private_key(path="private_key.pem"):
    with open(path, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )
    return private_key

# Sign a payload dict 🚀
def sign_payload(node_id, private_key, payload_dict):
    # Canonical JSON encoding
    payload_json = json.dumps(payload_dict, separators=(',', ':'), sort_keys=True).encode("utf-8")

    # Generate signature
    signature = private_key.sign(payload_json)
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    # Return full signed payload
    return {
        "node_id": node_id,
        "payload": payload_dict,
        "signature": signature_b64
    }

