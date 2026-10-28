STATUS - Prompt Privacy Scrubber CLI
====================================

What was built
--------------
A dependency-free Python CLI (Python 3.8+, standard library only) that scrubs
personal information from text before it is sent to an LLM, with optional
polishing through a local OpenAI-compatible endpoint (Ollama by default).

Package layout:
- scrubber/__init__.py      - package version (0.1.0)
- scrubber/__main__.py      - `python -m scrubber` entry point
- scrubber/scrub.py         - PII scrubbing: emails, phones, addresses, names
- scrubber/polish.py        - optional polishing via urllib against an
                              OpenAI-compatible chat/completions endpoint
- scrubber/cli.py           - argparse CLI (stdin/files, --polish,
                              --endpoint, --model, --api-key, --quiet)
- tests/test_scrubber.py    - 13 tests; mock endpoint, no network, no keys
- pyproject.toml            - setuptools build, `scrubber` console script
- README.md                 - usage, design, credits, MIT license pointer
- LICENSE                   - MIT, Copyright (c) 2026 Asdale Dynamics, LLC
- .gitignore                - standard Python ignores

Redaction tokens: [NAME], [PHONE], [EMAIL], [ADDRESS]. Name detection is
heuristic (titles such as Dr./Mr./Ms., greetings such as Dear/Hello/Hi/From,
and capitalized pairs at sentence starts). Detection is intentionally
dependency-free and local-first: nothing is stored, no keys are required, and
nothing leaves the machine unless the user points --polish at an endpoint.

How to run
----------
Install:
    pip install -e .          # or python3 -m venv .venv && .venv/bin/pip install -e .

Scrub stdin to stdout:
    echo "Email me at alex@example.com or call (555) 123-4567." | scrubber

Scrub a file to another file:
    scrubber -i note.txt -o note.scrubbed.txt

Scrub and polish through the local endpoint (Ollama default):
    scrubber --polish -i note.txt -o note.polished.txt

Custom endpoint/model:
    scrubber --polish --endpoint http://localhost:11434/v1 --model llama3 -i note.txt

Tests (mock endpoint, no network, no keys):
    python3 -m unittest discover -s tests

Verification results
--------------------
- `pip install -e .` builds and installs cleanly; `scrubber --help` and
  `python3 -m scrubber --version` work.
- `python3 -m unittest discover -s tests`: 13 tests, 13 pass, 0 failures.
  Tests cover emails, phones, street addresses, city/state/ZIP lines,
  title/greeting/sentence-start names, combined scrubbing, "no PII left"
  assertions, the mock polishing endpoint (success, request shape, and
  connection-failure fallback), and CLI stdin/stdout behavior.
- Manual CLI checks: stdin, -i/-o files, --version, and --polish with an
  unreachable endpoint all behave correctly (polish failure returns the
  scrubbed text unchanged with exit code 0).

Known gaps
----------
- Name detection is heuristic: middle-initial names, single surnames without a
  title, non-Western name formats, and names not at sentence starts may be
  missed. Common sentence-start words are excluded to limit false positives on
  places and organizations, but some proper nouns may still be redacted.
- Addresses are caught best with a street number plus suffix (St, Ave, Rd,
  etc.) or a city, ST ZIP line; other formats may slip through.
- Review scrubbed output before sending sensitive text anywhere.
- Polishing requires a reachable OpenAI-compatible endpoint; when it is
  unavailable the scrubbed text is returned unchanged (local-first safety).
- No .github/workflows files, no remote repository, nothing published, per
  project requirements.

Credit
------
Built and published by Asdale Dynamics, LLC. MIT License
(Copyright (c) 2026 Asdale Dynamics, LLC). See LICENSE and README.md.
