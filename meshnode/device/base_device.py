class BaseDevice:
    def __init__(self, device_id, config):
        self.device_id = device_id
        self.config = config
        self.allowed_api_keys = config.get("allowed_api_keys", [])

    def execute_action(self, action, params):
        raise NotImplementedError("Must implement execute_action in subclass")

    def get_capabilities(self):
        return []
