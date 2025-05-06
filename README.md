
# 🧩 context-manager – Monkey-Patch Memory Injector for text-generation-webui

`context-manager` is a **drop-in monkey-patch extension** for [text-generation-webui](https://github.com/oobabooga/text-generation-webui) that unlocks powerful persistent memory, chat logging, and customizable hooks without modifying any core files.

💡 Ideal for:

* Advanced prompt engineering
* Persona memory injection
* Persistent conversation context
* Dynamic hook-based customization

---

## 🚀 Features

* **🧠 Memory Injection**: Automatically prepends memory from a file to every prompt.
* **📝 Chat Logging**: Logs every interaction (input + model response) to a JSONL file.
* **🧩 Pre/Post Hooks**: Modify prompts and responses on the fly with `hook.py`.
* **⚙️ Configurable**: Controlled via `config.json` or environment variables.
* **🔄 Non-invasive**: Zero core file changes. Reversible. Plug-and-play.
* **💥 Extendable**: Hook system enables advanced behaviors (e.g., personas, tagging, filters).

---

## 🧱 File Structure

```
extensions/
└── injector_memory/
    ├── __init__.py          # Main patch logic
    ├── memory.py            # Context injection
    ├── logger.py            # Chat logging (JSONL)
    ├── hook.py              # Optional prompt/response mutators
    └── config.json          # Feature toggles
```

---

## 📌 How It Works

At runtime, `__init__.py` intercepts the model’s `chat_completions_common()` method:

* Injects memory from `memory_override.txt`
* Applies optional `hook.pre_prompt_hook()` and `hook.post_response_hook()`
* Logs the interaction to `chat_log.jsonl`
* All behaviors are configurable

---

## 🔧 Configuration

### `config.json`

```json
{
  "enabled": true,
  "inject_memory": true,
  "logging": true,
  "pre_prompt_hook": true,
  "post_response_hook": true
}
```

> Located in the `injector_memory` directory. Change these to enable/disable features.

### 🌍 Environment Variable Overrides

| Config Key           | Env Var                  |
| -------------------- | ------------------------ |
| `enabled`            | `INJ_ENABLED`            |
| `inject_memory`      | `INJ_INJECT_MEMORY`      |
| `logging`            | `INJ_LOGGING`            |
| `pre_prompt_hook`    | `INJ_PRE_PROMPT_HOOK`    |
| `post_response_hook` | `INJ_POST_RESPONSE_HOOK` |

Set to `1` or `0` to override config values (useful in containers or CI).

---

## ✅ Usage Instructions

1. Clone or drop `injector_memory/` into your `extensions/` folder.
2. Create your persistent context in `/workspace/memory_override.txt`.
3. Adjust `config.json` or set env variables to suit your workflow.
4. Restart `text-generation-webui`. Check logs for `[injector_memory] patch applied`.
5. Your conversations are now context-aware and logged. 🔍

---

## 🧠 Example

**memory\_override.txt**

```
You are a helpful assistant named Kai, empathetic and concise.
```

**User Message**

```
How do I write a unit test in Python?
```

**Prompt Sent to Model**

```
You are a helpful assistant named Kai, empathetic and concise.
How do I write a unit test in Python?
```

---

## 💾 Log Format

Chat interactions are written as JSON lines:

```json
{
  "timestamp": "2025-05-06T14:23:01Z",
  "user": "How do I write a unit test?",
  "response": "You can use the unittest module. Here's an example..."
}
```

File: `/workspace/chat_log.jsonl`

---

## 🧪 Hook Examples

### Timestamp Tag (pre-prompt)

```python
def pre_prompt_hook(prompt):
    from datetime import datetime
    return f"[{datetime.utcnow().isoformat()}]\n{prompt}"
```

### Persona Reminder (pre-prompt)

```python
def pre_prompt_hook(prompt):
    return f"Remember: You are Lucy, kind and direct.\n{prompt}"
```

### Response Label (post-response)

```python
def post_response_hook(response):
    return f"[OUTPUT]\n{response.strip()}"
```

### Truncate Long Responses (post-response)

```python
def post_response_hook(response):
    return response[:2048] + "..." if len(response) > 2048 else response
```

---

## 🔁 Auto-Memory Summarization (Optional)

You can automate rolling memory summaries using a local LLM:

```bash
python summarize_memory.py
```

This script:

* Pulls recent entries from `chat_log.jsonl`
* Summarizes key insights
* Writes them to `memory_override.txt`

See full script in README under "Automated Memory Summarization"

---

## 🗑️ Uninstallation

* Simply remove `injector_memory/` from `extensions/`.
* Optionally delete `/workspace/memory_override.txt` and `/workspace/chat_log.jsonl`.

---

## 📊 Feature Matrix

| Feature             | Toggleable | Source      | Default |
| ------------------- | ---------- | ----------- | ------- |
| Memory Injection    | ✅          | `memory.py` | On      |
| Logging             | ✅          | `logger.py` | On      |
| Pre-Prompt Hook     | ✅          | `hook.py`   | On      |
| Post-Response Hook  | ✅          | `hook.py`   | On      |
| Config via Env Vars | ✅          | `.env / OS` | Off     |

---

## 🧠 Pro Tips

* 🔄 Schedule `summarize_memory.py` with cron or systemd to keep memory fresh.
* 🔒 Use `.gitignore` to prevent committing `chat_log.jsonl` with sensitive data.
* ⚙️ For fine-grained control, add custom logic directly to `hook.py`.

---

## 🧠 Automated Memory Summarization

To keep your memory file up-to-date and concise, you can periodically summarize recent chats and write the summary to `memory_override.txt`. Here’s a ready-to-run script for local LLMs (text-generation-webui API):

```python
import json
import requests

CHAT_LOG_PATH = "/workspace/chat_log.jsonl"
MEMORY_OVERRIDE_PATH = "/workspace/memory_override.txt"
SUMMARIZATION_ENDPOINT = "http://localhost:5000/v1/chat/completions"  # Adjust if needed
MODEL_NAME = "gpt-3.5-turbo"  # Or your local model name
NUM_ENTRIES = 10

def load_recent_chat_entries(path, limit=NUM_ENTRIES):
    try:
        with open(path, "r") as f:
            lines = f.readlines()
            entries = [json.loads(line.strip()) for line in lines[-limit:]]
            return entries
    except FileNotFoundError:
        return []

def summarize(entries):
    if not entries:
        return ""
    messages = [
        {"role": "system", "content": "Summarize the following recent conversation into key memories or insights that might be useful for ongoing dialogue."},
        {"role": "user", "content": json.dumps(entries, indent=2)}
    ]
    response = requests.post(SUMMARIZATION_ENDPOINT, json={
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.5
    })
    if response.ok:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print("Error from model:", response.text)
        return ""

def write_summary(summary):
    with open(MEMORY_OVERRIDE_PATH, "w") as f:
        f.write(summary)

if __name__ == "__main__":
    recent_entries = load_recent_chat_entries(CHAT_LOG_PATH)
    summary = summarize(recent_entries)
    if summary:
        write_summary(summary)
        print("Summary written to memory_override.txt")
    else:
        print("No summary generated.")
```


## 💬 Final Words

You now have a fully modular, persistent memory system for your LLMs—no core edits required, fully hookable, and built for serious context retention. Extend, adapt, and build on top of `context-manager`.


---

**🧩 Repo:** `context-manager`
**Built for:** [text-generation-webui](https://github.com/oobabooga/text-generation-webui)
**License:** MIT
**Author:** Josh Templeton



