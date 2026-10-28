"""Scrub personal information from text: names, phones, emails, addresses.

All detection is heuristic and dependency-free so the tool stays local-first.
Redactions are replaced with safe tokens so the remaining text keeps its shape.
"""

from __future__ import annotations

import re

EMAIL_TOKEN = "[EMAIL]"
PHONE_TOKEN = "[PHONE]"
ADDRESS_TOKEN = "[ADDRESS]"
NAME_TOKEN = "[NAME]"

EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}\b")

PHONE_RE = re.compile(
    r"(?:(?<=\s)|^)(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}"
)

STREET_RE = re.compile(
    r"\b\d{1,6}\s+[A-Za-z0-9'.#&\-]+\s+"
    r"(?:St|Ave|Avenue|Rd|Road|Blvd|Boulevard|Ln|Lane|Dr|Drive|Ct|Court|"
    r"Pl|Place|Way|Cir|Circle|Ter|Terrace|Sq|Square|Pkwy|Parkway|"
    r"Hwy|Highway|Exp|Expressway|Cswy|Causeway|Trce|Trace|Byp|Bypass)\.?",
    re.IGNORECASE,
)

CITY_STATE_ZIP_RE = re.compile(
    r"\b[A-Za-z][A-Za-z'\.\s\-]{1,40},\s*[A-Z]{2}\s*\d{5}(?:-\d{4})?\b"
)

_TITLE = r"(?:Mr|Mrs|Ms|Dr|Prof|Rev|Hon|Sr|Jr|Mx)\.?"
_GREET = r"(?:Dear|Hello|Hi|From)"
_NAME_WORD = r"[A-Z](?:[a-z]+|'[A-Za-z]+)(?:['\-][A-Za-z]+)*"
_NAME_PAIR = rf"{_NAME_WORD}\s+{_NAME_WORD}"
_NAME = rf"{_NAME_WORD}(?:\s+{_NAME_WORD})?"

_TITLE_NAME_RE = re.compile(rf"\b({_TITLE})\s+{_NAME}\b")
_GREET_NAME_RE = re.compile(rf"\b({_GREET})\s+({_NAME})\b(?=\s*[,.!:])")

_NUMBER_STREET_COMMA_RE = re.compile(r"\b\d{1,6}\s+[A-Z][a-zA-Z'&\-]+\s*,")
_SENTENCE_START_NAME_RE = re.compile(
    rf"(?P<pre>(?:^|[.!?]\s+))(?P<name>{_NAME_PAIR})\b"
)

_SENTENCE_STARTERS = {
    "The", "This", "That", "These", "Those", "New", "Old", "Our", "My", "Your",
    "His", "Her", "Its", "We", "He", "She", "It", "They", "In", "On", "At", "To",
    "For", "With", "From", "By", "As", "If", "Then", "When", "Where", "Why",
    "How", "All", "Any", "Some", "No", "Yes", "Not", "Now", "Today", "Tomorrow",
    "Yesterday", "Tonight", "Morning", "Afternoon", "Evening",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December", "I", "A", "An", "Once",
    "Since", "Until", "While", "After", "Before", "During", "Into", "Upon",
    "Without", "Within", "Under", "Over", "Between", "Among", "Around", "About",
    "Across", "Again", "Also", "Even", "Just", "Still", "Very", "Quite", "Rather",
    "Such", "Only", "Each", "Every", "Either", "Neither", "Both", "Another",
    "Other", "Many", "Much", "Few", "Several",
}


def scrub_emails(text: str) -> str:
    return EMAIL_RE.sub(EMAIL_TOKEN, text)


def scrub_phones(text: str) -> str:
    return PHONE_RE.sub(PHONE_TOKEN, text)


def scrub_addresses(text: str) -> str:
    text = CITY_STATE_ZIP_RE.sub(ADDRESS_TOKEN, text)
    text = STREET_RE.sub(ADDRESS_TOKEN, text)
    text = _NUMBER_STREET_COMMA_RE.sub(ADDRESS_TOKEN, text)
    return text


def scrub_names(text: str) -> str:
    def title_repl(match):
        return match.group(1) + " " + NAME_TOKEN

    def greet_repl(match):
        return match.group(1) + " " + NAME_TOKEN

    def sentence_repl(match):
        first_word = match.group("name").split()[0]
        if first_word in _SENTENCE_STARTERS:
            return match.group(0)
        return match.group("pre") + NAME_TOKEN

    text = _TITLE_NAME_RE.sub(title_repl, text)
    text = _GREET_NAME_RE.sub(greet_repl, text)
    text = _SENTENCE_START_NAME_RE.sub(sentence_repl, text)
    return text


def scrub(text: str) -> str:
    text = scrub_emails(text)
    text = scrub_phones(text)
    text = scrub_addresses(text)
    text = scrub_names(text)
    return text
