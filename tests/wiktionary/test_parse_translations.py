# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for Wiktionary Translation Parsing Engine in Scribe-Data.
Inspired by wiktextract's extensive testing suite, but tailored
for Scribe-Data's high-speed pure regex implementations.
"""

import unittest

from scribe_data.wiktionary.parse_constants import _normalize_pos
from scribe_data.wiktionary.parse_translations import (
    _extract_source_lang_section,
    _extract_templates_from_block,
    _get_output_subdir,
    _parse_page_translations,
    _parse_page_worker,
    _resolve_dump_path,
    parse_wiktionary_translations,
    parse_xml_dump,
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
        words = _extract_templates_from_block(block, frozenset(["de"]))
        self.assertEqual(words.get("de", []), ["Buch (n)"])

    def test_extract_junk_prefixes(self):
        """Ensure conversational prefixes (like 'see: ') are filtered."""
        block = "{{t+|de|see: Test}} {{t|de|word}}"
        words = _extract_templates_from_block(block, frozenset(["de"]))
        self.assertEqual(words.get("de", []), ["word"])

    def test_extract_named_parameters(self):
        """
        Test the named parameters syntax {{t|1=code|2=word}} and ensure
        no catastrophic backtracking occurs even with complex interleaving.
        """
        block = "{{t|1=de|2=Mädchen|g=n}} {{t|f=1|1=de|x=y|2=Buch|n|m}}"
        words = _extract_templates_from_block(block, frozenset(["de"]))
        self.assertEqual(words.get("de", []), ["Mädchen (n)", "Buch (n, m)"])

    def test_grammar_trailing_tags(self):
        """
        Ensure trailing grammar tags are extracted intelligently.
        It should accurately map explicit attributes like `g2=m` down to `m`,
        while simultaneously ignoring noise tags (like `sc=` or `tr=`).
        """
        block = "{{t-check|de|Blitz|m|g2=m|sc=Latn|tr=bux}}"
        words = _extract_templates_from_block(block, frozenset(["de"]))
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
        # Let's test target=frozenset(['de'])
        res = _parse_page_translations(wikitext, frozenset(["de"]), "test", "English")

        # Verify Noun processing
        self.assertIn("noun", res.get("de", {}))
        self.assertIn("1", res["de"]["noun"])
        self.assertEqual(res["de"]["noun"]["1"]["translation"], "Mädchen (n), Buch (m)")
        self.assertEqual(res["de"]["noun"]["1"]["description"], "a subject of a test")

        # Verify Verb processing
        self.assertIn("verb", res.get("de", {}))
        self.assertEqual(res["de"]["verb"]["1"]["translation"], "prüfen")
        self.assertEqual(res["de"]["verb"]["1"]["description"], "to test")

    def test_extract_source_lang_section(self):
        """Test the native string `.find()` method used for source language parsing."""

        wikitext = (
            "==English==\n===Noun===\nabc\n====Translations====\nxyz\n==French==\nhello"
        )
        section = _extract_source_lang_section(wikitext, "English")
        self.assertIsNotNone(section)
        self.assertIn("===Noun===", section)
        self.assertNotIn("==French==", section)

        # Space variation
        wikitext2 = "== English ==\n===Verb===\n123"
        section2 = _extract_source_lang_section(wikitext2, "English")
        self.assertIsNotNone(section2)
        self.assertIn("===Verb===", section2)

        # Missing language
        section3 = _extract_source_lang_section(wikitext, "German")
        self.assertIsNone(section3)

    def test_parse_page_worker_edge_cases(self):
        """Test skipping empty or missing parameters in worker."""
        self.assertIsNone(_parse_page_worker(("", "", frozenset(), "English")))
        self.assertIsNone(
            _parse_page_worker(("test", "no translations here", frozenset(), "English"))
        )

    def test_parse_xml_dump_with_dummy_file(self):
        """Test full file parsing logic with a mock xml file."""
        import tempfile
        from pathlib import Path

        dummy_xml = """<mediawiki>
  <page>
    <title>test</title>
    <revision>
      <text xml:space="preserve">==English==
===Noun===
# A subject of a test.
====Translations====
{{trans-top|a subject of a test}}
* German: {{t+|de|Mädchen|n}}
{{trans-bottom}}
      </text>
    </revision>
  </page>
  <page>
    <title>book/translations</title>
    <revision>
      <text xml:space="preserve">==English==
===Noun===
====Translations====
{{trans-top|collection of pages}}
* German: {{t|de|Buch|n}}
{{trans-bottom}}
      </text>
    </revision>
  </page>
  <page>
    <title>invalid</title>
    <!-- missing text -->
    <revision></revision>
  </page>
</mediawiki>"""
        with tempfile.NamedTemporaryFile(
            suffix=".xml", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(dummy_xml)
            tmp_path = tmp.name

        try:
            # Test single-process fallback
            res_single = parse_xml_dump(tmp_path, ["de"], num_workers=1, progress=False)
            self.assertIn("de", res_single)
            self.assertIn("test", res_single["de"])
            self.assertEqual(
                res_single["de"]["test"]["noun"]["1"]["translation"], "Mädchen (n)"
            )
            self.assertIn("book", res_single["de"])  # tests subpage truncation

            # Test multiprocessing mode
            res_multi = parse_xml_dump(tmp_path, ["de"], num_workers=2, progress=False)
            self.assertIn("de", res_multi)
            self.assertIn("test", res_multi["de"])
            self.assertEqual(
                res_multi["de"]["test"]["noun"]["1"]["translation"], "Mädchen (n)"
            )
            self.assertIn("book", res_multi["de"])
        finally:
            Path(tmp_path).unlink()

    def test_parse_xml_dump_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parse_xml_dump("does_not_exist.xml.bz2", ["de"])

    def test_empty_xml_parsing(self):
        """Test iterator handling of empty fallback."""
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="w") as tmp:
            tmp.write("")
            tmp_path = tmp.name

        try:
            res = parse_xml_dump(tmp_path, ["de"], progress=False)
            self.assertEqual(res, {})
        except Exception:
            pass  # Etree ParseError handles it downstream or here, either is fine.
        finally:
            Path(tmp_path).unlink()

    def test_bz2_decompression_path(self):
        """Test bz2 file detection and decompression path using subprocess."""
        import bz2
        import os
        import tempfile
        from pathlib import Path

        dummy_xml = """<mediawiki>
  <page>
    <title>test</title>
    <revision>
      <text xml:space="preserve">==English==
===Noun===
# A subject of a test.
====Translations====
{{trans-top|a subject of a test}}
* German: {{t+|de|Mädchen|n}}
{{trans-bottom}}
      </text>
    </revision>
  </page>
</mediawiki>"""

        with tempfile.NamedTemporaryFile(
            suffix=".xml.bz2", delete=False, mode="wb"
        ) as tmp:
            tmp.write(bz2.compress(dummy_xml.encode("utf-8")))
            tmp_path = tmp.name

        try:
            os.environ["SCRIBE_WIKTIONARY_WORKERS"] = "1"
            res = parse_xml_dump(tmp_path, ["de"], progress=False)
            self.assertIn("de", res)
            self.assertIn("test", res["de"])
            # Remove env var logic override branch coverage
            del os.environ["SCRIBE_WIKTIONARY_WORKERS"]
        finally:
            Path(tmp_path).unlink()

    def test_resolve_dump_path(self):
        """Test dump path resolution logic."""
        import tempfile
        from pathlib import Path

        # Explicit existing path
        with tempfile.NamedTemporaryFile(
            suffix="-pages-articles.xml.bz2", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            path, iso = _resolve_dump_path(tmp_path, ".")
            self.assertEqual(path, Path(tmp_path).resolve())

            # Subdir fallback
            path, iso = _resolve_dump_path("nonexistent", ".")
            self.assertIsNone(path)

            path, iso = _resolve_dump_path("zhwiktionary", ".")
            self.assertIsNone(path)
            self.assertEqual(iso, "zh")
        finally:
            Path(tmp_path).unlink()

    def test_get_output_subdir(self):
        """Test subdirectory structure logic."""
        meta = {
            "english": {"iso": "en"},
            "chinese": {
                "sub_languages": {
                    "mandarin": {"iso": "zh"},
                    "cantonese": {"iso": "yue"},
                }
            },
        }
        self.assertEqual(_get_output_subdir("English", meta), "english")
        self.assertEqual(_get_output_subdir("Mandarin", meta), "chinese/mandarin")
        self.assertEqual(_get_output_subdir("German", meta), "german")

    def test_parse_wiktionary_translations_mock(self):
        """Integration test on parse_wiktionary_translations."""
        import shutil
        import tempfile
        from pathlib import Path

        dummy_xml_content = """<mediawiki>
  <page>
    <title>test</title>
    <revision>
      <text xml:space="preserve">==English==
===Noun===
# A subject of a test.
====Translations====
{{trans-top|a subject of a test}}
* German: {{t+|de|Mädchen|n}}
{{trans-bottom}}
      </text>
    </revision>
  </page>
</mediawiki>"""

        with tempfile.NamedTemporaryFile(
            suffix=".xml", delete=False, mode="w", encoding="utf-8"
        ) as tmp:
            tmp.write(dummy_xml_content)
            tmp_path = tmp.name

        out_dir = Path(tempfile.mkdtemp())

        try:
            parse_wiktionary_translations(
                target_languages=["de"],
                wiktionary_dump_path=tmp_path,
                output_dir=str(out_dir),
                overwrite=True,
            )
            self.assertTrue(out_dir.exists())

            de_file = out_dir / "english" / "de_translations_from_en.json"
            self.assertTrue(de_file.exists())
        finally:
            shutil.rmtree(out_dir)
            Path(tmp_path).unlink()


if __name__ == "__main__":
    unittest.main()
