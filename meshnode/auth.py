from meshnode.config import load_config

_config = load_config()
_api_keys = {key: "admin" for key in _config.get("api_keys", [])}

def verify_api_key(api_key):
    return api_key in _api_keys

def get_api_role(api_key):
    return _api_keys.get(api_key, None)
