"""Tests for the scrubber package. No network is used."""

from __future__ import annotations

import io
import json
import unittest
from unittest.mock import patch

from scrubber.scrub import (
    scrub,
    scrub_addresses,
    scrub_emails,
    scrub_names,
    scrub_phones,
    EMAIL_TOKEN,
    PHONE_TOKEN,
    ADDRESS_TOKEN,
    NAME_TOKEN,
)
from scrubber.polish import polish, DEFAULT_ENDPOINT, DEFAULT_MODEL
from scrubber.cli import main, build_parser


class FakeResponse:
    """Minimal stand-in for urllib.response.addinfourl."""

    def __init__(self, payload):
        self._payload = payload

    def read(self):
        if isinstance(self._payload, bytes):
            return self._payload
        return json.dumps(self._payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


class ScrubTests(unittest.TestCase):
    def assertNoPii(self, text, haystack):
        self.assertNotRegex(haystack, text)

    def test_email(self):
        out = scrub("Contact jane.doe@example.com or support@company.co.uk.")
        self.assertIn(EMAIL_TOKEN, out)
        self.assertNotIn("jane.doe@example.com", out)
        self.assertNotIn("support@company.co.uk", out)

    def test_email_removed_fully(self):
        out = scrub("Send to <john.smith+lists@mail.example.org> please.")
        self.assertNotRegex(out, r"john\.smith")
        self.assertNotRegex(out, r"@")

    def test_phones(self):
        out = scrub("Call (555) 123-4567, 555-123-4567, 555.123.4567, or +1 555 123 4567.")
        self.assertEqual(out.count(PHONE_TOKEN), 4)
        self.assertNotIn("555", out)

    def test_addresses(self):
        out = scrub("Visit 123 Main St, Anytown, IN 46202 or 456 Oak Avenue, NY 10001.")
        self.assertIn(ADDRESS_TOKEN, out)
        self.assertNotIn("123 Main St", out)
        self.assertNotIn("Anytown, IN 46202", out)
        self.assertNotIn("456 Oak Avenue", out)

    def test_names_titles_and_greetings(self):
        out = scrub("Dear Alice Brown, please ask Dr. Smith or Ms. Jane Doe-Jones.")
        self.assertIn(NAME_TOKEN, out)
        self.assertNotIn("Alice Brown", out)
        self.assertNotIn("Smith", out)
        self.assertNotIn("Jane Doe-Jones", out)

    def test_names_sentence_start(self):
        out = scrub("John Smith left the meeting early. The meeting was long.")
        self.assertIn(NAME_TOKEN, out)
        self.assertNotIn("John Smith", out)
        self.assertIn("The meeting was long", out)

    def test_scrub_combined(self):
        text = (
            "Dear Pat Lee,\n"
            "Email me at pat@example.com or call (555) 123-4567. "
            "Our office is at 777 Pine Road, Seattle, WA 98101.\n"
        )
        out = scrub(text)
        for token in (EMAIL_TOKEN, PHONE_TOKEN, ADDRESS_TOKEN, NAME_TOKEN):
            self.assertIn(token, out)
        self.assertNotIn("pat@example.com", out)
        self.assertNotIn("555", out)
        self.assertNotIn("Pat Lee", out)
        self.assertNotIn("777 Pine Road", out)
        self.assertNotIn("Seattle, WA 98101", out)

    def test_no_pii_left(self):
        raw = (
            "Maria Garcia contacted us at maria.garcia@example.com, "
            "(212) 555-0198, 10 Broadway, New York, NY 10001."
        )
        out = scrub(raw)
        self.assertNotRegex(out, r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
        self.assertNotRegex(out, r"\d{3}[-.\s]\d{3}[-.\s]\d{4}")
        self.assertNotIn("Maria Garcia", out)
        self.assertNotIn("Broadway", out)
        self.assertNotIn("New York, NY 10001", out)


class PolishTests(unittest.TestCase):
    def test_polish_returns_endpoint_content(self):
        payload = {"choices": [{"message": {"content": "Polished [NAME] text."}}]}
        with patch("scrubber.polish.urlopen", return_value=FakeResponse(payload)):
            out = polish("Hello [NAME].", endpoint="http://localhost:11434/v1", model="llama3")
        self.assertEqual(out, "Polished [NAME] text.")

    def test_polish_sends_model_and_messages(self):
        captured = {}

        def fake_urlopen(req, timeout=None):
            captured["url"] = req.full_url
            captured["method"] = req.method
            captured["body"] = req.data
            captured["req"] = req
            return FakeResponse({"choices": [{"message": {"content": "ok"}}]})

        with patch("scrubber.polish.urlopen", side_effect=fake_urlopen):
            polish("Hi [NAME].", endpoint=DEFAULT_ENDPOINT, model=DEFAULT_MODEL, api_key="sk-test")
        self.assertEqual(captured["url"], DEFAULT_ENDPOINT.rstrip("/") + "/chat/completions")
        self.assertEqual(captured["method"], "POST")
        self.assertIn(b'"model": "llama3"', captured["body"])
        self.assertIn(b'"content": "Hi [NAME]."', captured["body"])
        headers = dict(captured["req"].header_items())
        self.assertEqual(headers.get("Authorization"), "Bearer sk-test")

    def test_polish_failure_returns_original(self):
        with patch("scrubber.polish.urlopen", side_effect=OSError("connection refused")):
            out = polish("Hi [NAME].", quiet=True)
        self.assertEqual(out, "Hi [NAME].")


class CliTests(unittest.TestCase):
    def test_stdin_to_stdout_scrubs(self):
        inp = io.StringIO("Reach Sue Park at sue@example.org today.")
        out = io.StringIO()
        with patch("sys.stdin", inp), patch("sys.stdout", out):
            rc = main([])
        self.assertEqual(rc, 0)
        self.assertIn("[EMAIL]", out.getvalue())
        self.assertIn("[NAME]", out.getvalue())
        self.assertNotIn("sue@example.org", out.getvalue())
        self.assertNotIn("Sue Park", out.getvalue())

    def test_cli_flag_help(self):
        parser = build_parser()
        args = parser.parse_args(["--polish", "--endpoint", "http://x:1/v1", "--model", "m", "--quiet"])
        self.assertTrue(args.polish)
        self.assertEqual(args.endpoint, "http://x:1/v1")
        self.assertEqual(args.model, "m")
        self.assertTrue(args.quiet)


if __name__ == "__main__":
    unittest.main()
