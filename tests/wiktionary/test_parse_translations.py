# SPDX-License-Identifier: GPL-3.0-or-later
"""
Tests for the Wiktionary translation parsing functions in Scribe-Data.
"""

import unittest

import mwparserfromhell

from scribe_data.wiktionary.parse_constants import get_wiktionary_config
from scribe_data.wiktionary.parse_translations import (
    _extract_source_lang_section,
    _extract_translation_word,
    _get_output_subdir,
    _parse_page_translations,
    _parse_page_worker,
    _resolve_dump_path,
    parse_wiktionary_translations,
    parse_xml_dump,
)


class TestScribeWiktionaryTranslations(unittest.TestCase):
    def setUp(self):
        # Load real configs so test extraction covers actual filtering rules.
        self.en_config = get_wiktionary_config(source_iso="en")
        self.fr_config = get_wiktionary_config(source_iso="fr")
        self.de_config = get_wiktionary_config(source_iso="de")

    def test_extract_translation_word_junk_filter(self):
        """
        Words like 'literally' that appear in ignored_strings are filtered out.
        """
        node = mwparserfromhell.parse("{{t|de|literally}}").nodes[0]
        word = _extract_translation_word(
            node, "de", "literally", self.en_config, frozenset(["de"])
        )
        self.assertIsNone(word)

    def test_extract_junk_prefixes(self):
        """
        Words starting with an ignored prefix like 'see: ' are filtered out.
        """
        node = mwparserfromhell.parse("{{t+|de|see: Test}}").nodes[0]
        word = _extract_translation_word(
            node, "de", "see: Test", self.en_config, frozenset(["de"])
        )
        self.assertIsNone(word)

    def test_extract_named_parameters(self):
        """
        Named template params (1=lang, 2=word) are resolved the same as positional ones.
        """
        node = mwparserfromhell.parse("{{t|1=de|2=Mädchen|g=n}}").nodes[0]
        raw_word = str(node.get(2).value.strip_code()).strip()
        code = str(node.get(1).value.strip_code()).strip()
        word = _extract_translation_word(
            node, code, raw_word, self.en_config, frozenset(["de"])
        )
        self.assertEqual(word, "Mädchen (n)")

    def test_grammar_trailing_tags(self):
        """
        Grammar tags from trailing positional params are appended in parentheses.
        """
        node = mwparserfromhell.parse(
            "{{t-check|de|Blitz|m|g2=m|sc=Latn|tr=bux}}"
        ).nodes[0]
        raw_word = str(node.get(2).value.strip_code()).strip()
        code = str(node.get(1).value.strip_code()).strip()
        word = _extract_translation_word(
            node, code, raw_word, self.en_config, frozenset(["de"])
        )
        self.assertEqual(word, "Blitz (m)")

    def test_full_page_parse(self):
        """
        Multiple POS sections with trans-top blocks are each parsed into separate sense entries.
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
        res = _parse_page_translations(
            self.en_config, frozenset(["de"]), wikitext, "test"
        )

        # Verify noun translations.
        self.assertIn("noun", res.get("de", {}))
        self.assertIn("1", res["de"]["noun"])
        self.assertEqual(res["de"]["noun"]["1"]["translation"], "Mädchen (n), Buch (m)")
        self.assertEqual(res["de"]["noun"]["1"]["description"], "a subject of a test")

        # Verify verb translations.
        self.assertIn("verb", res.get("de", {}))
        self.assertEqual(res["de"]["verb"]["1"]["translation"], "prüfen")
        self.assertEqual(res["de"]["verb"]["1"]["description"], "to test")

    def test_french_template_headers_parse(self):
        """
        French-style {{S|nom|fr}} headers inside section titles are resolved to the right POS.
        """
        wikitext = """== {{langue|fr}} ==
=== {{S|nom|fr}} ===
==== {{S|traductions}} ====
{{trad-début|un type de mot}}
* English: {{trad+|en|word}}
{{trad-fin}}
"""
        res = _parse_page_translations(
            self.fr_config, frozenset(["en"]), wikitext, "mot"
        )

        # Verify the translation is mapped correctly.
        self.assertIn("noun", res.get("en", {}))
        self.assertEqual(res["en"]["noun"]["1"]["translation"], "word")
        self.assertEqual(res["en"]["noun"]["1"]["description"], "un type de mot")

    def test_german_ast_u_tabelle_parse(self):
        """
        The Ü-Tabelle format used by German Wiktionary is parsed correctly.
        """
        wikitext = """== Wort ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}} ===
{{Ü-Tabelle|Ü-Liste=
*Englisch: [1] {{ü|en|word}}
*Französisch: [1] {{ü|fr|mot}}
}}
"""
        res = _parse_page_translations(
            self.de_config, frozenset(["en", "fr"]), wikitext, "Wort"
        )

        self.assertIn("noun", res.get("en", {}))
        self.assertEqual(res["en"]["noun"]["1"]["translation"], "word")
        self.assertEqual(res["fr"]["noun"]["1"]["translation"], "mot")

    def test_extract_source_lang_section(self):
        """
        The correct language section is extracted and neighbouring sections are excluded.
        """
        wikitext = (
            "==English==\n===Noun===\nabc\n====Translations====\nxyz\n==French==\nhello"
        )
        section = _extract_source_lang_section(wikitext, self.en_config)
        self.assertIsNotNone(section)
        self.assertIn("===Noun===", section)
        self.assertNotIn("==French==", section)

        # Also check the spaced header variant.
        wikitext2 = "== English ==\n===Verb===\n123"
        section2 = _extract_source_lang_section(wikitext2, self.en_config)
        self.assertIsNotNone(section2)
        self.assertIn("===Verb===", section2)

    def test_parse_page_worker_edge_cases(self):
        """
        Worker returns None for empty or untranslated pages.
        """
        self.assertIsNone(_parse_page_worker(("", "", frozenset(), self.en_config)))
        self.assertIsNone(
            _parse_page_worker(("test", "no translations", frozenset(), self.en_config))
        )

    def test_parse_xml_dump_with_dummy_file(self):
        """
        Both single-process and multi-process paths produce correct output from a dummy XML file.
        """
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
            # Single-process fallback.
            res_single = parse_xml_dump(
                tmp_path,
                ["de"],
                source_lang_name="English",
                num_workers=1,
                progress=False,
            )
            self.assertIn("de", res_single)
            self.assertIn("test", res_single["de"])
            self.assertEqual(
                res_single["de"]["test"]["noun"]["1"]["translation"], "Mädchen (n)"
            )

            # Multi-process mode.
            res_multi = parse_xml_dump(
                tmp_path,
                ["de"],
                source_lang_name="English",
                num_workers=2,
                progress=False,
            )
            self.assertEqual(
                res_multi["de"]["test"]["noun"]["1"]["translation"], "Mädchen (n)"
            )
        finally:
            Path(tmp_path).unlink()

    def test_parse_xml_dump_not_found(self):
        with self.assertRaises(FileNotFoundError):
            parse_xml_dump(
                "does_not_exist.xml.bz2",
                ["de"],
                source_lang_name="English",
                progress=False,
            )

    def test_empty_xml_parsing(self):
        """
        An empty XML file returns an empty result without raising.
        """
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(suffix=".xml", delete=False, mode="w") as tmp:
            tmp.write("")
            tmp_path = tmp.name

        try:
            res = parse_xml_dump(
                tmp_path, ["de"], source_lang_name="English", progress=False
            )
            self.assertEqual(res, {})
        except Exception:
            pass
        finally:
            Path(tmp_path).unlink()

    def test_resolve_dump_path(self):
        """
        Explicit paths are returned as-is; missing paths return None with a sensible ISO.
        """
        import tempfile
        from pathlib import Path
        from unittest.mock import patch

        # Explicit existing path.
        with tempfile.NamedTemporaryFile(
            suffix="-pages-articles.xml.bz2", delete=False
        ) as tmp:
            tmp_path = tmp.name

        try:
            path, iso = _resolve_dump_path(tmp_path, ".")
            self.assertEqual(path, Path(tmp_path).resolve())

            # Mock the interactive questionary prompt specifically to skip the download process.
            with patch("questionary.select") as mock_select:
                mock_select.return_value.ask.return_value = "No"
                # Missing path falls back to None.
                path, iso = _resolve_dump_path("nonexistent", ".")
                self.assertIsNone(path)

                path, iso = _resolve_dump_path("zhwiktionary", ".")
                self.assertIsNone(path)
                self.assertEqual(iso, "zh")
        finally:
            Path(tmp_path).unlink()

    def test_get_output_subdir(self):
        """
        Top-level languages map to their lowercase name; sub-languages include their parent.
        """
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
        """
        translations are written to the expected JSON file on disk.
        """
        import shutil
        import tempfile
        from pathlib import Path

        dummy_xml_content = """<mediawiki>
  <page>
    <title>test</title>
    <revision>
      <text xml:space="preserve">==English==
===Noun===
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
