# mesh_action_vocab.py

MESH_ACTION_VOCAB = {
    "core": [
        {
            "name": "turn_on",
            "parameters": {}
        },
        {
            "name": "turn_off",
            "parameters": {}
        },
        {
            "name": "set_value",
            "parameters": {
                "value": "int(0-100)"
            }
        },
        {
            "name": "set_angle",
            "parameters": {
                "angle": "int(0-180)"
            }
        },
        {
            "name": "get_status",
            "parameters": {}
        }
    ],
    "meta": {
        "version": "1.0.0",
        "last_updated": "2024-06-04"
    }
}
