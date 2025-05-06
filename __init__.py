import os
import json

from modules import shared
from openai import completions
from extensions.injector_memory.memory import inject_memory
from extensions.injector_memory.logger import log_chat
from extensions.injector_memory import hook

# ... (config loading and flag setup)

original_chat = completions.chat_completions_common

def patched_chat_completions_common(body, is_legacy=False, stream=False, prompt_only=False):
    if not ENABLED:
        return original_chat(body, is_legacy=is_legacy, stream=stream, prompt_only=prompt_only)

    # Extract user input
    messages = body.get("messages", [])
    user_input, _, history = completions.convert_history(messages)

    # Memory injection
    if DO_MEMORY:
        mem = inject_memory()
        if mem:
            user_input = f"{mem}\n{user_input}"
            body['messages'][-1]['content'] = user_input

    # Pre-prompt hook
    if DO_PRE_PROMPT_HOOK:
        user_input = hook.pre_prompt_hook(user_input)
        body['messages'][-1]['content'] = user_input

    # Store for logging
    _logged = user_input

    # Invoke original
    result = original_chat(body, is_legacy=is_legacy, stream=stream, prompt_only=prompt_only)

    # Logging + post-hook
    if stream:
        def streamer():
            buf = ""
            for chunk in result:
                delta = chunk.get('choices', [{}])[0].get('delta', {}).get("content", "")
                buf += delta
                yield chunk
            if DO_POST_RESPONSE_HOOK:
                buf = hook.post_response_hook(buf)
            if DO_LOGGING:
                log_chat(_logged, buf)
        return streamer()
    else:
        chunks = list(result)
        try:
            resp = chunks[-1]["choices"][0]["message"]["content"]
            if DO_POST_RESPONSE_HOOK:
                resp = hook.post_response_hook(resp)
            if DO_LOGGING:
                log_chat(_logged, resp)
        except Exception:
            pass
        return iter(chunks)

# Apply patch
completions.chat_completions_common = patched_chat_completions_common
shared.logger.info(
    f"[injector_memory] patch applied"
    f" | enabled={ENABLED}"
    f" | memory={DO_MEMORY}"
    f" | logging={DO_LOGGING}"
    f" | pre_hook={DO_PRE_PROMPT_HOOK}"
    f" | post_hook={DO_POST_RESPONSE_HOOK}"
)