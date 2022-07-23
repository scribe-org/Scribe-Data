<div align="center">
  <a href="https://github.com/scribe-org/Scribe-Data"><img src="https://raw.githubusercontent.com/scribe-org/Organization/main/logo/ScribeAppLogo.png" width=512 height=230 alt="Scribe Logo"></a>
</div>

---

[![issues](https://img.shields.io/github/issues/scribe-org/Scribe-Data)](https://github.com/scribe-org/Scribe-Data/issues)
[![discussions](https://img.shields.io/github/discussions/scribe-org/Scribe-Data)](https://github.com/scribe-org/Scribe-Data/discussions)
[![language](https://img.shields.io/badge/Python-3-306998.svg?logo=python&logoColor=ffffff)](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md)
[![pypi](https://img.shields.io/pypi/v/scribe-data.svg?color=4B8BBE)](https://pypi.org/project/scribe-data/)
[![pypistatus](https://img.shields.io/pypi/status/scribe-data.svg)](https://pypi.org/project/scribe-data/)
[![license](https://img.shields.io/github/license/scribe-org/Scribe-Data.svg)](https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt)
[![coc](https://img.shields.io/badge/coc-Contributor%20Covenant-ff69b4.svg)](https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md)
[![codestyle](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

### Data extraction and formatting for Scribe applications

This repository contains the scripts for extracting and formatting data from [Wikidata](https://www.wikidata.org/) for Scribe applications. Updates to the language keyboard and interface data can be done using [scribe_data/load/update_data.py](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/load/update_data.py).

<a id="contents"></a>

# **Contents**

- [Process](#process)
- [Supported Languages](#supported-languages)
- [Contributing](#contributing)
- [Featured By](#featured-by)

<a id="process"></a>

# Process [`⇧`](#contents)

[scribe_data/load/update_data.py](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/load/update_data.py) is used to update all data for [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS), with this functionality later being expanded to update [Scribe-Android](https://github.com/scribe-org/Scribe-Android) and [Scribe-Desktop](https://github.com/scribe-org/Scribe-Desktop) when they're active. The ultimate goal is that this repository will house language packs that are periodically updated with new [Wikidata](https://www.wikidata.org/) lexicographical data, with these packs then being available to download by users of Scribe applications.

<a id="supported-languages"></a>

# Supported Languages [`⇧`](#contents)

Scribe's goal is functional, feature-rich keyboards and interfaces for all languages. Check the [data](https://github.com/scribe-org/Scribe-Data/tree/main/data) directory for queries for currently supported languages and those that have substantial data on [Wikidata](https://www.wikidata.org/).

The following table shows the supported languages and the amount of data available for each on [Wikidata](https://www.wikidata.org/):

| Languages  |   Nouns | Verbs | Translations\* | Adjectives† | Prepositions‡ |
| :--------- | ------: | ----: | -------------: | ----------: | ------------: |
| French     |  16,233 | 1,501 |         67,652 |           - |             - |
| German     |  28,745 | 3,381 |         67,652 |           - |           187 |
| Italian    |     847 |    73 |         67,652 |           - |             - |
| Portuguese |   5,109 |   495 |         67,652 |           - |             - |
| Russian    | 194,401 |    11 |         67,652 |           - |            12 |
| Spanish    |  20,987 | 3,717 |         67,652 |           - |             - |
| Swedish    |  42,002 | 4,160 |         67,652 |           - |             - |

`*` Given the current **`beta`** status where words are machine translated.

`†` Adjective-preposition support is in progress [(see issue)](https://github.com/scribe-org/Scribe-iOS/issues/86).

`‡` Only for languages for which preposition annotation is needed.

<a id="contributing"></a>

# Contributing [`⇧`](#contents)

Work that is in progress or could be implemented is tracked in the [issues](https://github.com/scribe-org/Scribe-Data/issues). Please see the [contribution guidelines](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md) if you are interested in contributing to Scribe-Data. Also check the [`-priority-`](https://github.com/scribe-org/Scribe-Data/labels/-priority-) labels in the [issues](https://github.com/scribe-org/Scribe-Data/issues) for those that are most important, as well as those marked [`good first issue`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) that are tailored for first time contributors.

### Ways to Help

- Join us in the [Discussions](https://github.com/scribe-org/Scribe-Data/discussions) 👋
- [Reporting bugs](https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=bug&template=bug_report.yml) as they're found
- Working on [new features](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3Afeature)
- [Documentation](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3Adocumentation) for onboarding and project cohesion
- Adding language data to [Scribe-Data](https://github.com/scribe-org/Scribe-Data/issues) via [Wikidata](https://www.wikidata.org/)!

### Data Edits

Scribe does not accept direct edits to the grammar JSON files as they are sourced from [Wikidata](https://www.wikidata.org/). Edits can be discussed and the queries themselves will be changed and ran before an update. If there is a problem with one of the files, then the fix should be made on [Wikidata](https://www.wikidata.org/) and not on Scribe. Feel free to let us know that edits have been made by [opening a data issue](https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=data&template=data_wikidata.yml) and we'll be happy to integrate them!

<a id="featured-by"></a>

# Featured By [`⇧`](#contents)

<details><summary><strong>Articles and Presentations on Scribe</strong></summary>
<p>

<strong>2022</strong>

- [Presentation slides](https://docs.google.com/presentation/d/10Ai0-b8XUj5u9Hw4UgBtB7ufiPhvfFrb1vEUEyXYr5w/edit?usp=sharing) for a talk with [CocoaHeads Berlin](https://www.meetup.com/cocoaheads-berlin/)
- [Video on Scribe](https://www.youtube.com/watch?v=4GpFN0gGmy4&list=PL66MRMNlLyR7p9wsYVfuqJOjKZpbuwp8U&index=6) for [Wikimedia Celtic Knot 2022](https://meta.wikimedia.org/wiki/Celtic_Knot_Conference_2022)
- [Presentation slides](https://docs.google.com/presentation/d/1K2lj8PPgdx12I-xuhm--CBLrGm-Cz50NJmbp96zpGrk/edit?usp=sharing) for a talk with the [LD4 Wikidata Affinity Group](https://www.wikidata.org/wiki/Wikidata:WikiProject_LD4_Wikidata_Affinity_Group)
- [Scribe](https://github.com/scribe-org) featured for new developers on [MediaWiki](https://www.mediawiki.org/wiki/New_Developers)
- [Presentation slides](https://docs.google.com/presentation/d/1Cu3VwQ3lJUp5W84YDe0AFYS-6zfBxKsm0MI-OMl_IzY/edit?usp=sharing) for [Wikimedia Hackathon 2022](https://www.mediawiki.org/wiki/Wikimedia_Hackathon_2022)
- [Blog post](https://tech-news.wikimedia.de/en/2022/03/18/lexicographical-data-for-language-learners-the-wikidata-based-app-scribe/) on [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS) for [Wikimedia Tech News](https://tech-news.wikimedia.de/en/homepage/) ([DE](https://tech-news.wikimedia.de/2022/03/18/sprachenlernen-mit-lexikografische-daten-die-wikidata-basierte-app-scribe/) / [Tweet](https://twitter.com/wikidata/status/1507335538596106257?s=20&t=YGRGamftI-5B_VwQ_bFRhA))
- [Presentation slides](https://docs.google.com/presentation/d/16ld_rCbwJCiAdRrfhF-Fq9Wm_ciHCbk_HCzGQs6TB1Q/edit?usp=sharing) for [Wikidata Data Reuse Days 2022](https://diff.wikimedia.org/event/wikidata-data-reuse-days-2022/)

</p>
</details>

<div align="center">
  <br>
    <a href="https://tech-news.wikimedia.de/en/2022/03/18/lexicographical-data-for-language-learners-the-wikidata-based-app-scribe/"><img height="120"src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/wikimedia_deutschland_logo.png" alt="Wikimedia Tech News"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://www.mediawiki.org/wiki/New_Developers"><img height="120" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/mediawiki_logo.png" alt="MediaWiki"></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>

# Powered By

<div align="center">
  <br>
  <a href="https://www.wikidata.org/"><img height="175" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/wikidata_logo.png" alt="Wikidata"></a>
  <br>
</div>
