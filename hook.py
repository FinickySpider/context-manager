def pre_prompt_hook(prompt: str) -> str:
    # Modify or decorate prompt before generation
    return prompt

def post_response_hook(response: str) -> str:
    # Modify response if needed (for censorship, formatting, etc.)
    return response