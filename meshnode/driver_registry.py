# driver_registry.py

class DriverRegistry:
    def __init__(self):
        self.drivers = {}
        self.driver_schemas = {}

    def register_driver(self, device_id, driver_instance):
        self.drivers[device_id] = driver_instance
        print(f"[DriverRegistry] Registered driver for {device_id} 🚀")

    def register_driver_schema(self, device_id, capability_schema):
        self.driver_schemas[device_id] = capability_schema
        print(f"[DriverRegistry] Registered driver SCHEMA for {device_id} 🚀")

    def get_driver(self, device_id):
        return self.drivers.get(device_id)

    def list_capabilities(self):
        combined = {}

        # Include instantiated driver capabilities
        for device_id, driver in self.drivers.items():
            if hasattr(driver, "get_capability_schema"):
                combined[device_id] = driver.get_capability_schema()

        # Include dynamically registered schemas
        for device_id, schema in self.driver_schemas.items():
            combined[device_id] = schema

        return combined

