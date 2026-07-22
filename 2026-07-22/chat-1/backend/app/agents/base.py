import anthropic
import json
from app.config import settings

client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

MAX_RETRIES = 1


def call_agent(system_prompt: str, user_message: str, model: str = "claude-sonnet-4-20250514") -> dict:
    """Call Claude and return parsed JSON response with retry on malformed output."""
    last_error = None
    for attempt in range(MAX_RETRIES + 1):
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
        )
        raw = response.content[0].text.strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as e:
            last_error = e
            continue
    raise ValueError(f"Agent returned malformed JSON after {MAX_RETRIES + 1} attempts: {last_error}")
