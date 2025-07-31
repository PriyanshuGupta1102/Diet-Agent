# pantry_manager.py

import json
import os

PANTRY_FILE = "pantry.json"

def load_pantry():
    """Loads the pantry items from the JSON file."""
    if not os.path.exists(PANTRY_FILE):
        return []  # Return an empty list if the file doesn't exist
    with open(PANTRY_FILE, "r") as f:
        return json.load(f)

def save_pantry(pantry_data):
    """Saves the pantry items to the JSON file."""
    with open(PANTRY_FILE, "w") as f:
        json.dump(pantry_data, f, indent=4)