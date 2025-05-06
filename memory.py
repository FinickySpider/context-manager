MEMORY_FILE = "/workspace/memory_override.txt"

def inject_memory():
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        return ""