<div align="center">
  <a href="https://github.com/scribe-org/Scribe-Data"><img src="https://raw.githubusercontent.com/scribe-org/Organization/main/logo/ScribeAppLogo.png" width=512 height=230 alt="Scribe Logo"></a>
</div>

---

[![issues](https://img.shields.io/github/issues/scribe-org/Scribe-Data)](https://github.com/scribe-org/Scribe-Data/issues)
[![discussions](https://img.shields.io/github/discussions/scribe-org/Scribe-Data)](https://github.com/scribe-org/Scribe-Data/discussions)
[![license](https://img.shields.io/github/license/scribe-org/Scribe-Data.svg)](https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt)
[![coc](https://img.shields.io/badge/coc-Contributor%20Covenant-ff69b4.svg)](https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md)
[![codestyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Data extraction and formatting for Scribe applications

This repository contains the scripts for extracting and formatting data from [Wikidata](https://www.wikidata.org/) for Scribe keyboards. Updates to the language keyboard data can be done using [Data/update_data.py](https://github.com/scribe-org/Scribe-Data/tree/main/Data/update_data.py).

# **Contents**<a id="contents"></a>

- [Supported Languages](#supported-languages)

# Supported Languages [`⇧`](#contents) <a id="supported-languages"></a>

Scribe's goal is functional, feature-rich keyboards for all languages. Check the [Data](https://github.com/scribe-org/Scribe-Data/tree/main/Data) directory for queries for currently supported languages and those that have substantial data on [Wikidata](https://www.wikidata.org/).

The following table shows the supported languages and the amount of data available for each on [Wikidata](https://www.wikidata.org/):

| Languages  |   Nouns | Verbs | Translations\* | Adjectives† | Prepositions‡ |
| :--------- | ------: | ----: | -------------: | ----------: | ------------: |
| French     |  15,788 | 1,246 |         67,652 |           - |             - |
| German     |  28,089 | 3,130 |         67,652 |           - |           187 |
| Italian    |     783 |    71 |         67,652 |           - |             - |
| Portuguese |   4,662 |   189 |         67,652 |           - |             - |
| Russian    | 194,394 |    11 |         67,652 |           - |            12 |
| Spanish    |   9,452 | 2,062 |         67,652 |           - |             - |
| Swedish    |  41,187 | 4,138 |         67,652 |           - |             - |

`*` Given the current **`beta`** status where words are machine translated.

`†` Adjective-preposition support is in progress [(see issue)](https://github.com/scribe-org/Scribe-iOS/issues/86).

`‡` Only for languages for which preposition annotation is needed.

# Powered By

<div align="center">
  <br>
  <a href="https://www.wikidata.org/"><img height="175" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/wikidata_logo.png" alt="Wikidata"></a>
  <br>
</div>
