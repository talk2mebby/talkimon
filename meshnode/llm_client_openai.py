from openai import OpenAI
import os
import json
from llm_client_interface import LLMClientInterface

class LLMClient(LLMClientInterface):
    def __init__(self, model="gpt-4o", backend="openai"):
        self.model = model
        self.backend = backend
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def chat(self, messages):
        functions = [
            {
                "name": "execute_action",
                "description": "Execute an action on a mesh device, optionally on a remote node",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string"},
                        "target_device": {"type": "string"},
                        "target_node": {"type": "string"},  # NEW!
                        "parameters": {"type": "object"}
                    },
                    "required": ["action", "target_device", "target_node", "parameters"]
                }
            }
        ]

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            functions=functions,
            function_call={"name": "execute_action"}
        )

        action_args = response.choices[0].message.function_call.arguments
        return action_args  # JSON string

