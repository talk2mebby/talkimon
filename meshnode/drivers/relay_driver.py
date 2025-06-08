from drivers.base_driver import Driver
import RPi.GPIO as GPIO

class RelayDriver(Driver):
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(pin, GPIO.OUT)

    def list_capabilities(self):
        return ["turn_on", "turn_off"]

    def execute(self, action_name, parameters):
        if action_name == "turn_on":
            GPIO.output(self.pin, GPIO.HIGH)
            print(f"[RelayDriver] Pin {self.pin} ON")
        elif action_name == "turn_off":
            GPIO.output(self.pin, GPIO.LOW)
            print(f"[RelayDriver] Pin {self.pin} OFF")
        else:
            raise ValueError(f"Unsupported action: {action_name}")
