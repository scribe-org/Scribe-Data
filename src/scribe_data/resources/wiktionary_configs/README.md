# [Wiktionary Configs](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/resources/wiktionary_configs)

Scribe extracts translation data from [Wiktionary](https://en.wiktionary.org/wiki/Wiktionary) page dumps. Each language edition uses different section headers, translation templates, and part-of-speech labels. A single hard-coded parser would miss most editions or mis-attribute senses. These YAML files describe **per-edition** conventions so [`parse_translations`](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/wiktionary/parse_translations.py) can slice the right language block, recognize translation rows, normalize POS names, and skip editorial noise.

Configs are loaded by ISO code: `{iso}_wiktionary_config.yaml` (see [`get_wiktionary_config`](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/wiktionary/parse_constants.py)). If a file is missing, the CLI reports that the edition is unsupported until a config is added. Supported source ISO codes: [bn](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/bn_wiktionary_config.yaml), [de](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/de_wiktionary_config.yaml), [en](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/en_wiktionary_config.yaml), [es](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/es_wiktionary_config.yaml), [fr](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/fr_wiktionary_config.yaml), [id](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/id_wiktionary_config.yaml), [it](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/it_wiktionary_config.yaml), [pt](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/pt_wiktionary_config.yaml), [ru](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/ru_wiktionary_config.yaml), [sv](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/sv_wiktionary_config.yaml).

## Practical Workflow

Use these two raw pages as your reference set:

- German sample: [de.wiktionary.org Buch raw](https://de.wiktionary.org/w/index.php?title=Buch&action=raw)
- English sample: [en.wiktionary.org book raw](https://en.wiktionary.org/w/index.php?title=book&action=raw)

Read both pages side by side and extract structural differences first, lexical details second.

### 1) Start from the English config

Copy the English file as your baseline mindset, not as a final template.

- Keep universal cleanup ideas (`ignored_prefixes`, `ignored_strings`) where they still make sense.
- Replace English-specific assumptions (headers, templates, POS labels) with German ones.

### 2) Identify the German language section marker

In the German raw page, the language block is marked with `{{Sprache|Deutsch}}`, not plain `==English==`.

Set:

- `lang_header_pattern` to match the German marker
- `lang_header_level` only if needed by the edition layout

`lang_header_pattern` is regex, so special characters must be escaped. Use:

- `\(\{\{Sprache\|Deutsch\}\}\)`

Do not use unescaped `( {{Sprache|Deutsch}} )` in regex-based config fields.

### 3) Identify how translation blocks are built

German entries use `{{Übersetzungen}}` and `{{Ü-Tabelle ...}}` style sections, with translation rows like `{{Ü|...}}` and `{{Üt|...}}`.

Set:

- `engine` for the Ü-table style
- translation-related template keys for the actual German template names
- `prefilters` with high-signal substrings from real German pages

## Raw Dump -> Config Examples

### Example A: German (`de`)

Raw dump snippet (from `Buch`):

```wikitext
== Buch ({{Sprache|Deutsch}}) ==
=== {{Wortart|Substantiv|Deutsch}}, {{n}} ===
...
==== {{Übersetzungen}} ====
{{Ü-Tabelle|1|G=fest gebundenes Schriftwerk|Ü-Liste=
*{{en}}: {{Ü|en|book}}
*{{ar}}: {{Üt|ar|كتاب|kitāb}}
*{{fr}}: {{Ü|fr|livre}} {{m}}
}}
```

Config snippet:

```yaml
engine: ast_u_tabelle
lang_header_pattern: \(\{\{Sprache\|Deutsch\}\}\)
prefilters:
  - Ü-Tabelle
  - '{{Ü|'
  - '{{Üt|'
template_pos: wortart
template_table: ü-tabelle
template_list: ü-liste
template_translation:
  - ü
  - üt
```

Why this mapping:

- `{{Sprache|Deutsch}}` -> `lang_header_pattern`
- `{{Ü-Tabelle ...}}` -> `engine: ast_u_tabelle` + `template_table`
- `|Ü-Liste=` -> `template_list`
- `{{Ü|...}}` / `{{Üt|...}}` -> `template_translation`
- `prefilters` includes both `{{Ü|` and `{{Üt|` so pages dominated by either form are detected early
- `engine: ast_u_tabelle` is a config-side parser mode (internal switch), so the literal text appears only in YAML, not in wiki pages

Mini example:

```wikitext
# raw dump (what you see in Wiktionary)
{{Ü-Tabelle|1|G=...|Ü-Liste=
*{{en}}: {{Ü|en|book}}
}}
```

```yaml
# config (what you set in YAML)
engine: ast_u_tabelle
template_table: ü-tabelle
template_list: ü-liste
template_translation:
  - ü
  - üt
```

If `engine` is removed here, extraction falls back to the default `trans-top` family and can miss these German `Ü-Tabelle` blocks.

### Example B: English (`en`)

Raw dump snippet (header/POS shape from `book`):

```wikitext
==English==
...
====Noun====
...
=====Translations=====
{{see translation subpage|Noun}}
```

Config snippet:

```yaml
lang_header_pattern: ^\s*English\s*$
prefilters:
  - translation
  - '{{t'
template_top:
  - trans-top
template_bottom: trans-bottom
template_translation:
  - t
  - t+
```

Why this mapping:

- `==English==` -> `lang_header_pattern`
- English pages are `trans-top` family driven for inline translation blocks -> `template_top` / `template_bottom`
- `{{t...}}` templates -> `template_translation`
- `translation` and `{{t` are practical prefilter signals

### Example C: Italian (`it`)

Raw dump snippet (header/block from `libro`):

```wikitext
== {{-it-}} ==
...
=== {{Sostantivo|it}} ===
...
==== Traduzione ====
{{Trad1|...}}
* {{en}}: [[book]]
* {{fr}}: [[livre]] {{m}}
{{Trad2}}
```

Config snippet:

```yaml
engine: ast_wikilink_list
lang_header_pattern: ^\{\{-it-\}\}$
prefilters:
  - Traduzione
template_top:
  - trad1
template_bottom: trad2
```

Why this mapping:

- `== {{-it-}} ==` -> `lang_header_pattern`
- Italian pages use the `Trad1`/`Trad2` block wrapper with raw wikilinks for the words -> `engine: ast_wikilink_list` + `template_top` / `template_bottom`.
- `template_translation` is not needed because the `ast_wikilink_list` engine assumes the templates found at the start of bullets inside the block *are* the ISO language codes (e.g., `{{en}}`).

### 4) Build the POS normalization map

German POS labels are local (`Substantiv`, `Verb`, `Adjektiv`, etc.). Normalize these into your shared output POS set.

Set `pos_map` entries such as:

- `substantiv -> noun`
- `verb -> verb`
- `adjektiv -> adjective`
- `adverb -> adverb`
- `präposition -> preposition`

Add only what you can verify from real pages.

### 5) Add ignore rules for non-translation noise

Wiktionary relies on community contributors, meaning pages often contain editorial text and placeholders that should not be treated as actual translations. You can identify these by reading translation blocks in the raw dump.

**How to find noise in the raw dump:**
When browsing the raw wikitext, look for placeholder templates or explanatory text inside translation rows. Let's look at a real example from the English (`en`) edition — open [en.wiktionary.org more raw](https://en.wiktionary.org/w/index.php?title=more&action=raw) and search for `t-needed`:

```wikitext
{{trans-top|word to form a comparative}}
* Burmese: {{t-needed|my}}
* Lao: {{t-needed|lo}}
* Tibetan: {{t-needed|bo}}
* Uyghur: {{t-needed|ug}}
{{trans-bottom}}
```

These `{{t-needed|...}}` entries are placeholders — editors added the language name but haven't found the translation yet. To prevent Scribe from saving `t-needed` as a spurious word, add it to `ignored_strings`:

```yaml
ignored_strings:
  - t-needed
  - please add this translation if you can
  - '[script needed]'
  - no equivalent

ignored_prefixes:
  - 'use:'
  - 'use '
  - 'see:'
  - 'see '
```

By adding these rules, Scribe will automatically drop these notes instead of assuming they are foreign vocabulary!

*(Reference: [`en_wiktionary_config.yaml`](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/resources/wiktionary_configs/en_wiktionary_config.yaml) ignores)*

### 6) Validate with multiple German words

Do not validate with one page only. Check several common nouns, verbs, and adjectives.

Validation target:

- language section is found
- translation blocks are found
- POS is normalized correctly
- obvious noise is skipped

If one class fails, adjust YAML rules, not output expectations.

## Minimal Checklist Before Finalizing `de_wiktionary_config.yaml`

- `lang_header_pattern` matches German blocks in raw pages
- `engine` matches the German translation layout
- `prefilters` are specific enough to reject irrelevant pages
- `template_*` keys reflect real German template names
- `pos_map` covers high-frequency POS labels
- `ignored_prefixes` and `ignored_strings` remove common noise

When this checklist is green across multiple German entries, the config is ready for regular extraction runs.
