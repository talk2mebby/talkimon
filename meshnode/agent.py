# meshnode/agent.py

import threading
import time
from meshnode.config import load_config
from meshnode.device import device_registry

# Example pluggable AI interface (stub for now)
class AIProviderInterface:
    def chat(self, prompt):
        # Stub: Replace this with real AI call
        return "I'm thinking about: " + prompt

# Mesh Brain Agent Loop
class MeshBrainAgent:
    def __init__(self):
        self.ai = AIProviderInterface()
        self.running = False
        self.config = load_config()

    def sense(self):
        # Example: Sense devices
        devices = list(device_registry.keys())
        return f"Devices I see: {devices}"

    def think(self, sensed_data):
        # Example: Use AI to think
        prompt = f"Given this sensed data: {sensed_data}, what should I do?"
        response = self.ai.chat(prompt)
        return response

    def act(self, decision):
        # Example: Log decision (later → trigger device actions)
        print(f"[MeshBrain] Acting on decision: {decision}")

    def loop(self):
        print("[MeshBrain] Starting agent loop...")
        self.running = True
        while self.running:
            try:
                sensed = self.sense()
                decision = self.think(sensed)
                self.act(decision)
                time.sleep(5)  # Loop every 5 seconds (tune as needed)
            except Exception as e:
                print(f"[MeshBrain] Error in loop: {e}")
                time.sleep(5)

    def start(self):
        t = threading.Thread(target=self.loop, daemon=True)
        t.start()
