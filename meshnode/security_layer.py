class SecurityLayer:
    def approve(self, action):
        safe_actions = ["turn_on", "turn_off", "set_value"]
        if action["action"] in safe_actions:
            print("[SecurityLayer] APPROVED")
            return True
        else:
            print("[SecurityLayer] REJECTED:", action)
            return False
