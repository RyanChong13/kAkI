"""LLM agent base — wraps OpenAI / Anthropic for structured JSON responses.

All AI agents in the app call ``call_agent()`` with a system prompt and
user message.  The function sends the request to the configured LLM,
extracts JSON from the response, and returns the parsed Python object.

Set either ``OPENAI_API_KEY`` or ``ANTHROPIC_API_KEY`` in the environment
(OpenAI takes priority if both are set).  If neither key is configured the
function raises a clear ``RuntimeError`` so the caller can surface a
helpful message to the user.
"""

import json
import logging
import re

from app.config import get_settings

logger = logging.getLogger(__name__)


def call_agent(
    system_prompt: str,
    user_message: str,
    *,
    max_tokens: int = 4096,
) -> dict | list:
    """Call the configured LLM with a system prompt + user message and return parsed JSON.

    The system prompt should instruct the model to return **only** valid JSON.
    This wrapper handles markdown code-block wrapping and extracts the JSON
    payload automatically.

    Raises:
        RuntimeError: if neither API key is configured.
        ValueError: if the response cannot be parsed as JSON.
    """
    settings = get_settings()

    if settings.openai_api_key:
        return _call_openai(settings, system_prompt, user_message, max_tokens)
    if settings.anthropic_api_key:
        return _call_anthropic(settings, system_prompt, user_message, max_tokens)

    raise RuntimeError(
        "No LLM API key is configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY "
        "in your .env file (see .env.example)."
    )


def _call_openai(settings, system_prompt, user_message, max_tokens):
    from openai import OpenAI

    client = OpenAI(api_key=settings.openai_api_key)

    logger.info("Calling OpenAI (%s) — %d char system prompt, %d char user message",
                settings.openai_model, len(system_prompt), len(user_message))

    response = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )

    text = response.choices[0].message.content or ""
    logger.info("OpenAI responded — %d chars", len(text))
    return _parse_json_response(text)


def call_agent_with_images(
    system_prompt: str,
    user_message: str,
    images: list[bytes],
    *,
    max_tokens: int = 4096,
) -> dict | list:
    """Like ``call_agent`` but attaches PNG/JPEG images to the request.

    Used for vision tasks (e.g. transcribing a scanned resume).  Requires
    an OpenAI key — the vision-capable path.  Raises ``RuntimeError`` if no
    OpenAI key is configured.
    """
    settings = get_settings()

    if not settings.openai_api_key:
        raise RuntimeError(
            "Image analysis requires an OpenAI API key. Set OPENAI_API_KEY "
            "in your .env file (see .env.example)."
        )

    from openai import OpenAI
    import base64

    client = OpenAI(api_key=settings.openai_api_key)

    content: list[dict] = [{"type": "text", "text": user_message}]
    for image_bytes in images:
        encoded = base64.b64encode(image_bytes).decode("ascii")
        content.append({
            "type": "image_url",
            "image_url": {"url": f"data:image/png;base64,{encoded}"},
        })

    logger.info("Calling OpenAI (%s) with %d image(s) — %d char system prompt",
                settings.openai_model, len(images), len(system_prompt))

    response = client.chat.completions.create(
        model=settings.openai_model,
        max_tokens=max_tokens,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": content},
        ],
    )

    text = response.choices[0].message.content or ""
    logger.info("OpenAI vision responded — %d chars", len(text))
    return _parse_json_response(text)


def _call_anthropic(settings, system_prompt, user_message, max_tokens):
    from anthropic import Anthropic

    client = Anthropic(api_key=settings.anthropic_api_key)

    logger.info("Calling Claude (%s) — %d char system prompt, %d char user message",
                settings.anthropic_model, len(system_prompt), len(user_message))

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )

    # Concatenate text blocks
    text = ""
    for block in response.content:
        if hasattr(block, "text"):
            text += block.text

    logger.info("Claude responded — %d chars", len(text))
    return _parse_json_response(text)


def _parse_json_response(text: str) -> dict | list:
    """Extract and parse JSON from an LLM response.

    Handles three cases:
    1. Bare JSON (ideal case).
    2. JSON wrapped in a markdown code block (```json ... ```).
    3. JSON embedded in prose (find first {/[ and last }/]).
    """
    text = text.strip()

    # 1 — direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2 — markdown code block
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3 — brace/bracket extraction
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass

    raise ValueError(
        f"Could not parse JSON from LLM response (first 300 chars): {text[:300]}"
    )
