"""
LLM Client Configuration
Connects to OpenAI-compatible endpoint with Learner001 credentials.
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://keygateway.arshnivlabs.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4o-mini")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))


def get_llm_client() -> OpenAI:
    """Return configured OpenAI client pointing to custom endpoint."""
    return OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL,
    )


def chat_completion(messages: list, system_prompt: str = "", temperature: float = 0.3) -> str:
    """
    Call the LLM with a list of messages.
    Returns the assistant's response text.
    """
    client = get_llm_client()

    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=full_messages,
            max_tokens=MAX_TOKENS,
            temperature=temperature,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM Error]: {str(e)}"
