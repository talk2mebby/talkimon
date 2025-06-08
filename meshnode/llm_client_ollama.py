import requests
import json
from llm_client_interface import LLMClientInterface

class LLMClient(LLMClientInterface):
    def __init__(self, model="llama3", backend="ollama"):
        self.model = model
        self.backend = backend
        self.base_url = "http://localhost:11434"

    def chat(self, messages):
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False
        }

        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload
        )
        response.raise_for_status()

        # Ollama does not natively enforce functions yet — so we will parse response ourselves
        reply = response.json()["message"]["content"]

        # HACK: expect GPT to reply with JSON-formatted action (you can prompt for this)
        # Example prompt: "Respond ONLY in this JSON format: { 'action': ..., 'target_device': ..., 'parameters': {...} }"
        action = json.loads(reply)

        return json.dumps(action)  # return as JSON string for consistency
