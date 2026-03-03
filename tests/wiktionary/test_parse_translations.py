# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for Wiktionary Translation Parsing Engine in Scribe-Data.
Inspired by wiktextract's extensive testing suite, but tailored
for Scribe-Data's high-speed pure regex implementations.
"""

import unittest

from scribe_data.wiktionary.parse_constants import _normalize_pos
from scribe_data.wiktionary.parse_translations import (
    _extract_templates_from_block,
    _parse_page_translations,
)


class TestScribeWiktionaryTranslations(unittest.TestCase):
    def test_normalize_pos(self):
        """Test normalization of POS (Part of Speech) headers."""
        self.assertEqual(_normalize_pos("Proper Noun"), "proper_noun")
        self.assertEqual(_normalize_pos("Noun"), "noun")
        self.assertEqual(_normalize_pos("Adjective"), "adjective")

    def test_extract_from_block_junk_filter(self):
        """
        Ensure garbage conversational phrases inserted by Wikipedians
        (like 'literally' or 'please add this translation') are correctly
        filtered out without disrupting valid items.
        """
        block = (
            "{{t|de|literally}} {{t|de|Buch|n}} "
            "{{t|de|please add this translation if you can}}"
        )
        words = _extract_templates_from_block(block, ["de"])
        self.assertEqual(words.get("de", []), ["Buch (n)"])

    def test_extract_junk_prefixes(self):
        """Ensure conversational prefixes (like 'see: ') are filtered."""
        block = "{{t+|de|see: Test}} {{t|de|word}}"
        words = _extract_templates_from_block(block, ["de"])
        self.assertEqual(words.get("de", []), ["word"])

    def test_extract_named_parameters(self):
        """
        Test the named parameters syntax {{t|1=code|2=word}} and ensure
        no catastrophic backtracking occurs even with complex interleaving.
        """
        block = "{{t|1=de|2=Mädchen|g=n}} {{t|f=1|1=de|x=y|2=Buch|n|m}}"
        words = _extract_templates_from_block(block, ["de"])
        self.assertEqual(words.get("de", []), ["Mädchen (n)", "Buch (n, m)"])

    def test_grammar_trailing_tags(self):
        """
        Ensure trailing grammar tags are extracted intelligently.
        It should accurately map explicit attributes like `g2=m` down to `m`,
        while simultaneously ignoring noise tags (like `sc=` or `tr=`).
        """
        block = "{{t-check|de|Blitz|m|g2=m|sc=Latn|tr=bux}}"
        words = _extract_templates_from_block(block, ["de"])
        # Should map 'm' and 'g2=m' down to unique 'm', dropping 'sc' and 'tr'.
        self.assertEqual(words.get("de", []), ["Blitz (m)"])

    def test_full_page_parse(self):
        """
        Test a full-scale mock page parsing simulation: traversing POS
        blocks, locating Translation subsections, and extracting words
        with definitions.
        """
        wikitext = """==English==
===Noun===
# A subject of a test.
====Translations====
{{trans-top|a subject of a test}}
* German: {{t+|de|Mädchen|n}}, {{t|de|Buch|m}}
* French: {{t+|fr|fille|f}}
{{trans-bottom}}

===Verb===
# To perform an examination.
====Translations====
{{trans-top|to test}}
* German: {{t|de|prüfen}}
{{trans-bottom}}
"""
        # Let's test target=['de']
        res = _parse_page_translations(wikitext, ["de"], "test", "English")

        # Verify Noun processing
        self.assertIn("noun", res.get("de", {}))
        self.assertIn("1", res["de"]["noun"])
        self.assertEqual(res["de"]["noun"]["1"]["translation"], "Mädchen (n), Buch (m)")
        self.assertEqual(res["de"]["noun"]["1"]["description"], "a subject of a test")

        # Verify Verb processing
        self.assertIn("verb", res.get("de", {}))
        self.assertEqual(res["de"]["verb"]["1"]["translation"], "prüfen")
        self.assertEqual(res["de"]["verb"]["1"]["description"], "to test")


if __name__ == "__main__":
    unittest.main()
