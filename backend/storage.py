import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
MEMORY_PATH = os.path.join(BASE_DIR, "data", "case_memory.json")

def ensure_memory_file():
    if not os.path.exists(MEMORY_PATH):
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)

def load_memory():
    ensure_memory_file()
    with open(MEMORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_case(case_record):
    memory = load_memory()
    case_record["timestamp"] = datetime.utcnow().isoformat()
    memory.append(case_record)

    with open(MEMORY_PATH, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def get_memory():
    return load_memory()
