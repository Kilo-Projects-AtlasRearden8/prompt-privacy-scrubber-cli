"""Optional polishing of scrubbed text through an OpenAI-compatible endpoint.

Default endpoint is Ollama's OpenAI-compatible server
(http://localhost:11434/v1). The tool is local-first: if the endpoint is
unavailable or any request fails, the scrubbed text is returned unchanged so
nothing ever hard-fails on a missing LLM. No API keys are stored or required.
"""

from __future__ import annotations

import json
import sys
import urllib.error
from urllib.request import Request, urlopen
from typing import Optional

DEFAULT_ENDPOINT = "http://localhost:11434/v1"
DEFAULT_MODEL = "llama3"

DEFAULT_SYSTEM_PROMPT = (
    "You polish scrubbed text for clarity and tone. Do not reveal, infer, or "
    "restore any redacted personal information ([NAME], [PHONE], [EMAIL], "
    "[ADDRESS]). Keep every redaction token intact and unchanged. Return only "
    "the polished text, with no extra commentary."
)


class EndpointError(Exception):
    """Raised when the polishing endpoint cannot be used."""


def polish(
    text: str,
    endpoint: str = DEFAULT_ENDPOINT,
    model: str = DEFAULT_MODEL,
    api_key: Optional[str] = None,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT,
    timeout: float = 30.0,
    quiet: bool = False,
) -> str:
    """Send scrubbed text to the endpoint; return polished text on success.

    Any failure (network, bad JSON, missing keys) returns `text` unchanged and
    prints a short warning to stderr unless `quiet` is true.
    """

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": text},
        ],
        "temperature": 0.3,
        "stream": False,
    }

    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    url = endpoint.rstrip("/") + "/chat/completions"
    data = json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, headers=headers, method="POST")

    try:
        with urlopen(req, timeout=timeout) as response:
            body = response.read()
    except Exception as exc:  # network failures, timeouts, etc.
        if not quiet:
            print(f"scrubber: polish unavailable ({exc}); returning scrubbed text", file=sys.stderr)
        return text

    try:
        parsed = json.loads(body)
        return parsed["choices"][0]["message"]["content"]
    except Exception as exc:
        if not quiet:
            print(f"scrubber: could not parse polish response ({exc}); returning scrubbed text", file=sys.stderr)
        return text
