# config.py
import json, os

def load_db_config(path="db_config.json"):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(base_dir, path)
    if os.path.exists(full_path):
        with open(full_path, "r") as f:
            return json.load(f)
    else:
        raise FileNotFoundError(f"Database config not found at {full_path}")
