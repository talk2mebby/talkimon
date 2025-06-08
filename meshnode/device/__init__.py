from meshnode.device.base_device import BaseDevice
from meshnode.device.relay_device import RelayDevice
from meshnode.device.servo_device import ServoDevice
from meshnode.device.rest_api_device import RestApiDevice
import yaml

device_registry = {}

DEVICE_CLASSES = {
    "RelayDevice": RelayDevice,
    "ServoDevice": ServoDevice,
    "RestApiDevice": RestApiDevice
}

def load_devices():
    global device_registry
    with open("config.yaml", "r") as f:
        devices_config = yaml.safe_load(f).get("devices", [])

    new_registry = {}
    for d in devices_config:
        device_class = DEVICE_CLASSES.get(d["type"])
        if device_class:
            new_registry[d["device_id"]] = device_class(d["device_id"], d)
        else:
            print(f"[WARN] Unknown device type: {d['type']}")

    device_registry = new_registry
    print(f"[MeshNode] Loaded {len(device_registry)} devices.")

# Load at startup
load_devices()

