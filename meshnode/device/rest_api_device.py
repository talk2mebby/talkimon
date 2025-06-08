import requests
from meshnode.device.base_device import BaseDevice

class RestApiDevice(BaseDevice):
    def __init__(self, device_id, config):
        super().__init__(device_id, config)
        self.endpoint = config["endpoint"]

    def execute_action(self, action, params):
        payload = {"action": action, "params": params}
        response = requests.post(self.endpoint, json=payload, timeout=2)
        return f"REST API call result: {response.status_code} {response.text}"

    def get_capabilities(self):
        return ["custom_action"]  # You can define per your API
