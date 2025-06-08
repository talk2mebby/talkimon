class Driver:
    def list_capabilities(self):
        raise NotImplementedError

    def execute(self, action_name, parameters):
        raise NotImplementedError
