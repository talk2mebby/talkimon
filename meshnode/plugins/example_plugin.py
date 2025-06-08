from meshnode.device.base_device import BaseDevice

class ExamplePluginDevice(BaseDevice):
    def __init__(self, device_id, config):
        super().__init__(device_id, config)
        self.custom_param = config.get("custom_param", "default")

    def execute_action(self, action, params):
        if action == "say_hello":
            return f"Hello from {self.device_id} with param {self.custom_param}!"
        else:
            raise ValueError(f"Unknown action: {action}")

    def get_capabilities(self):
        return ["say_hello"]
