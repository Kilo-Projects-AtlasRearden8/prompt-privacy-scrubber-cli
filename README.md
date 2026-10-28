# Prompt Privacy Scrubber

A small, dependency-free Python CLI that scrubs names, phones, emails, and
postal addresses out of text before you send it to an LLM. Optional polishing
rewrites the scrubbed text for clarity through a local OpenAI-compatible
endpoint (Ollama by default). Built to be local-first: no API keys, no
accounts, nothing leaves your machine unless you point it at an endpoint.

Credit: built and published by **Asdale Dynamics, LLC**.

## Install

```bash
git clone https://github.com/dylanasdale/prompt-privacy-scrubber-cli  # example only, no remote is created by this project
cd prompt-privacy-scrubber-cli
pip install -e .
```

This requires Python 3.8+ and nothing else — the scrubber uses only the
standard library.

## Usage

```bash
# Scrub text from stdin, write scrubbed text to stdout
echo "Email me at alex@example.com or call (555) 123-4567." | scrubber

# Scrub a file, write result to another file
scrubber -i note.txt -o note.scrubbed.txt

# Also polish the scrubbed text for clarity via Ollama (default endpoint)
scrubber --polish -i note.txt -o note.polished.txt

# Use a different OpenAI-compatible endpoint or model
scrubber --polish --endpoint http://localhost:11434/v1 --model llama3 -i note.txt

# See options
scrubber --help
```

Redactions are replaced with readable tokens:

- `[NAME]` — people's names (titles and greetings included: `Dr. Smith`, `Dear Alice`)
- `[PHONE]` — phone numbers
- `[EMAIL]` — email addresses
- `[ADDRESS]` — street addresses and city, state ZIP lines

## How it works

Detection is heuristic and dependency-free: regular expressions for emails,
phones, and addresses, plus title/greeting/sentence-start patterns for names.
Because it is heuristic, it will not catch everything (handwritten-style text,
unusual name formats, or addresses written without a street number may slip
through). Review sensitive text before sending it anywhere. When `--polish` is
enabled, only the already-scrubbed text is sent to the endpoint; redaction
tokens are sent with instructions to leave them untouched.

Polishing is resilient by design: if the endpoint is down or the response
cannot be parsed, the scrubbed text is returned unchanged and a note goes to
stderr.

## Testing

```bash
python -m unittest discover -s tests
```

Tests use a mock endpoint — no network and no API keys.

## Local-first, no secrets

This tool never stores API keys or personal data. Do not put keys, passwords,
or real personal information in this repository. The `--api-key` flag is only
passed through to your endpoint for a single run.

## License

MIT. Copyright (c) 2026 Asdale Dynamics, LLC. See LICENSE.

## About

Asdale Dynamics, LLC (Indiana, formed October 2026) is Dylan Asdale's LLC —
a registered nurse turned AI author and founder. The LLC publishes
beginner-friendly AI education, books and guides, and practical open-source
tools: prompt tools, local-LLM utilities, MCP servers, agent skills,
small-business and author tools, and accessible life-admin helpers.

Dylan writes AI explainers "like a friend would": plain English, step by step,
never condescending. See his book *The Massive AI Manual* and hub site
dylanasdale.github.io.
