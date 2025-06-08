# drivers/dummy_driver.py

class DummyDriver:
    def execute(self, action, parameters):
        print(f"[DummyDriver] Executing action: {action} with parameters {parameters}")

    def get_capability_schema(self):
        return {
            "device_type": "dummy",
            "actions": [
                {"name": "turn_on", "parameters": {}},
                {"name": "turn_off", "parameters": {}},
                {"name": "set_value", "parameters": {"value": "int(0-100)"}}
            ]
        }
