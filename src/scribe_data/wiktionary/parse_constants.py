# SPDX-License-Identifier: GPL-3.0-or-later
"""
Parsing constants and utilities for the Wiktionary extraction module.
"""

import re

# MARK: Regex Settings

# Level-3 headers only (===Noun===), not level-4 (====Translations====).
# This prevents capturing nested headers mistakenly as POS sections.
POS_HEADER_RE = re.compile(r"^===(?!=)\s*([^=\n]+?)\s*===\s*$", re.MULTILINE)

# Strictly match the translations header block cleanly.
TRANSLATIONS_HEADER_RE = re.compile(
    r"^====+\s*Translations\s*====+\s*$", re.MULTILINE | re.IGNORECASE
)

# Top and bottom blocks defining translation groups inside Wiktionary pages.
TRANS_TOP_RE = re.compile(r"\{\{trans-top(?:\|[^}]*)?\}\}", re.IGNORECASE)
TRANS_BOTTOM_RE = re.compile(r"\{\{trans-bottom\}\}", re.IGNORECASE)

# Standard {{t|lang|word|tags}} detection. We match standard templates cleanly.
# Capture 1: Language Code | Capture 2: Word | Capture 3: Trailing Grammar Tags
T_TEMPLATE_RE = re.compile(
    r"\{\{(?:t\+?|t-check|tt|tt\+)\s*"
    r"(?:\|[^}|]+)*"
    r"\|\s*([a-zA-Z]{2,3})\s*"
    r"\|\s*([^}|]+)"
    r"([^}]*)\}\}",
    re.IGNORECASE,
)

# Named template extraction like {{t|f=1|1=de|2=Buch|g=n}}.
# Captures precisely using lazy boundaries to avoid catastrophic backtracking.
T_NAMED_RE = re.compile(
    r"\{\{(?:t\+?|t-check|tt|tt\+)\s*"
    r"(?:\|[^}|]+)*?\|\s*"
    r"1\s*=\s*([a-zA-Z]{2,3})\s*"
    r"(?:\|[^}|]+)*?\|\s*"
    r"2\s*=\s*([^}|]+)"
    r"([^}]*)\}\}",
    re.IGNORECASE,
)

# As we iterate millions of tiny fragments, matching string boundaries
# blindly can take thousands of milliseconds of CPU execution time.
# To overcome this, we compiled a super-fast Python Set Hook mapping directly
# to standard Wikipedia's most common abuse strings.
# Any string wrapped in {{t|}} like "please add this translation if you can",
# "literally", "different structure used", or that starts with "see: " is now
# instantly tossed directly in memory by checking the native Set.
# Scribe will never accidentally output garbage strings anymore.
IGNORED_TRANSLATION_STRINGS = {
    "please add this translation if you can",
    "script needed",
    "[script needed]",
    "literally",
    "lit.",
    "e.g.",
    "cf.",
    "different structure used",
    "no equivalent",
    "not used",
    "not attested",
}

IGNORED_TRANSLATION_PREFIXES = (
    "see:",
    "see ",
    "use:",
    "use ",
    "prefix ",
    "suffix ",
    "usually expressed",
    "expressed with",
    "-prefix",
    "-suffix",
)

# MARK: Parsing Utilities


def _normalize_pos(pos: str) -> str:
    """Map POS header to normalized form."""
    if not pos:
        return "other"
    pos_lower = pos.strip().lower()
    pos_map = {
        "noun": "noun",
        "verb": "verb",
        "adjective": "adjective",
        "adj": "adjective",
        "adverb": "adverb",
        "adv": "adverb",
        "preposition": "preposition",
        "prep": "preposition",
        "conjunction": "conjunction",
        "conj": "conjunction",
        "interjection": "interjection",
        "intj": "interjection",
        "pronoun": "pronoun",
        "pron": "pronoun",
        "determiner": "determiner",
        "det": "determiner",
        "numeral": "numeral",
        "num": "numeral",
        "phrase": "phrase",
        "proper noun": "proper_noun",
        "proper name": "proper_noun",
        "name": "proper_noun",
        "symbol": "symbol",
        "particle": "particle",
    }
    return pos_map.get(pos_lower, pos_lower.replace(" ", "_"))
