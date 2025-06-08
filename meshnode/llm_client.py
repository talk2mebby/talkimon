from openai import OpenAI
import os
import json

class LLMClient:
    def __init__(self, model="gpt-4o", backend="openai"):
        self.model = model
        self.backend = backend
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, messages):
        # Define "function" schema → structured action
        functions = [
            {
                "name": "execute_action",
                "description": "Execute an action on a mesh device",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "target_device": {"type": "string"},
                        "parameters": {"type": "object"}
                    },
                    "required": ["action", "target_device", "parameters"]
                }
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=functions,
            function_call="auto"
        )

        # This returns a JSON string
        action_args = response.choices[0].message.function_call.arguments
        return action_args  # as JSON string
