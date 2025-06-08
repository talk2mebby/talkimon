# import RPi.GPIO as GPIO
from meshnode.device.base_device import BaseDevice

# GPIO.setmode(GPIO.BCM)

class RelayDevice(BaseDevice):
    def __init__(self, device_id, config):
        super().__init__(device_id, config)
        self.pin = config["pin"]
        # GPIO.setup(self.pin, GPIO.OUT)
        # GPIO.output(self.pin, GPIO.LOW)

    def execute_action(self, action, params):
        if action == "turn_on":
            # GPIO.output(self.pin, GPIO.HIGH)
            return "Relay turned on (simulated on Mac)"
        elif action == "turn_off":
            # GPIO.output(self.pin, GPIO.LOW)
            return "Relay turned off (simulated on Mac)"
        else:
            raise ValueError(f"Unknown action: {action}")

    def get_capabilities(self):
        return ["turn_on", "turn_off"]

