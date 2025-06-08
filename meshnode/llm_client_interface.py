class LLMClientInterface:
    def chat(self, messages):
        """
        Given a list of messages, returns a response.
        Must be implemented by concrete LLM client.
        """
        raise NotImplementedError
