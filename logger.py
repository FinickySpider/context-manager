import json
from datetime import datetime

LOG_PATH = "/workspace/chat_log.jsonl"

def log_chat(user_input: str, response: str):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "user": user_input.strip(),
        "response": response.strip()
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")