# Changelog

See the [releases for Scribe-Data](https://github.com/scribe-org/Scribe-Data/releases) for an up to date list of versions and their release dates.

Scribe-Data tries to follow [semantic versioning](https://semver.org/), a MAJOR.MINOR.PATCH version where increments are made of the:

- MAJOR version when we make incompatible API changes
- MINOR version when we add functionality in a backwards compatible manner
- PATCH version when we make backwards compatible bug fixes

Emojis for the following are chosen based on [gitmoji](https://gitmoji.dev/).

## [Upcoming] Scribe-Data 4.0.0

## Scribe-Data 3.3.0

### ✨ Features

- The translation process has been updated to allow for translations from non-English languages ([#72](https://github.com/scribe-org/Scribe-Data/issues/72), [#73](https://github.com/scribe-org/Scribe-Data/issues/73), [#74](https://github.com/scribe-org/Scribe-Data/issues/74), [#75](https://github.com/scribe-org/Scribe-Data/issues/75), [#75](https://github.com/scribe-org/Scribe-Data/issues/75), [#76](https://github.com/scribe-org/Scribe-Data/issues/76), [#77](https://github.com/scribe-org/Scribe-Data/issues/77), [#78](https://github.com/scribe-org/Scribe-Data/issues/78), [#79](https://github.com/scribe-org/Scribe-Data/issues/79)).

### 📝 Documentation

- The documentation has been given a new layout with the logo in the top left ([#90](https://github.com/scribe-org/Scribe-Data/issues/90)).
- The documentation now has links to the code at the top of each page ([#91](https://github.com/scribe-org/Scribe-Data/issues/91)).

### 🐞 Bug Fixes

- Annotation bugs were removed like repeat or empty values.
- Perfect tenses of Portuguese verbs were fixed via finding the appropriate PID ([#68](https://github.com/scribe-org/Scribe-Data/issues/68)).
  - Note that the most common past perfect property is not the standard one, so this will need to be fixed.

### ♻️ Code Refactoring

- [pre-commit](https://pre-commit.com/) have been added to the repo to improve the development experience ([#137](https://github.com/scribe-org/Scribe-Data/issues/137)).
- Code formatting was shifted from [black](https://github.com/psf/black) to [Ruff](https://github.com/astral-sh/ruff).
- A Ruff based GitHub workflow was added to check the code formatting and lint the codebase on each pull request ([#109](https://github.com/scribe-org/Scribe-Data/issues/109)).
- The `_update_files` directory was renamed `update_files` as these files are used in non-internal manners now ([#57](https://github.com/scribe-org/Scribe-Data/issues/57)).
- A common function has been created to map Wikidata ids to noun genders ([#69](https://github.com/scribe-org/Scribe-Data/issues/69)).
- The project now is installed locally for development and command line usage, so usages of `sys.path` have been removed from files ([#122](https://github.com/scribe-org/Scribe-Data/issues/122)).
- The directory structure has been dramatically streamlined and includes folders for future projects where language data could come from other sources like Wiktionary ([#139](https://github.com/scribe-org/Scribe-Data/issues/139)).
  - Translation files are moved to their own directory.
  - The `extract_transform` directory has been removed and all files within it have been moved one level up.
  - The `languages` directory has been renamed `language_data_extraction`.
  - All files within `wikidata/_resources` have been moved to the `resources` directory.
  - The gender and case annotations for data formatting have now been commonly defined.
  - All language directory `formatted_data` files have been now moved to the `scribe_data_json_export` directory to prepare for outputs being required to be directed to a directory outside of the package.
  - Path computing has been refactored throughout the codebase, and unneeded functions for data transfers have been removed.

## Scribe-Data 3.2.2

- Minor fixes to documentation index and file docstrings to fix errors.
- Revert change to package path definition to hopefully register the resources directory.

## Scribe-Data 3.2.1

### ♻️ Code Refactoring

- The docs and tests were grafted into the package using `MANIFEST.in`.
- Minor fixes to file and function docstrings and documentation files.
- `include_package_data=True` is used in `setup.py` to hopefully include all files in the package distribution.

## Scribe-Data 3.2.0

### ✨ Features

- The data and process needed for an English keyboard has been added ([#39](https://github.com/scribe-org/Scribe-Data/issues/39)).
  - The Wikidata queries for English have been updated to get all nouns and verbs.
  - Formatting scripts have been written to prepare the queried data and load it into an SQLite database.
- The data update process has been cleaned up in preparation for future changes to Scribe-Data and to implement better practices.
- Language data was extracted into a JSON file for more succinct referencing ([#52](https://github.com/scribe-org/Scribe-Data/issues/52)).
- Language codes are now checked with the package [langcodes](https://github.com/rspeer/langcodes) for easier expansion.
- A process has been created to check and update words that can be translated for each Scribe language ([#44](https://github.com/scribe-org/Scribe-Data/issues/44)).
- The baseline data returned from Wikidata queries is now removed once a formatted data file is created.

### ✅ Tests

- A full testing suite has been added to run on GitHub Actions ([#37](https://github.com/scribe-org/Scribe-Data/issues/37)).
- Unit tests have been added for Wikidata queries ([#48](https://github.com/scribe-org/Scribe-Data/issues/48)) and utility functions ([#50](https://github.com/scribe-org/Scribe-Data/issues/50)).

### 🐞 Bug Fixes

- Tensorflow was removed from the download wiki process to fix build problems on Macs.

### ♻️ Code Refactoring

- The Anaconda based virtual environment was removed and documentation was updated to reflect this.
- Language data processes were moved into the `src/scribe_data/extract_transform/languages` directory to clean up the structure.
- Code formatting processes were defined with common structures based on language and word type variables defined at the top of files.

## Scribe-Data 3.1.0

### ✨ Features

- The word "Scribe" is now added to language database nouns files if it's not already present ([#35](https://github.com/scribe-org/Scribe-Data/issues/35)).
- German contracted prepositions have been added to the German prepositions formatting process ([#34](https://github.com/scribe-org/Scribe-Data/issues/34)).
- Words that are upper case are now better included in the autocomplete lexicon with their lower case equivalents being removed.
- Words with apostrophes have been removed from the autocomplete lexicon.

### ♻️ Code Refactoring

- Database output column names are now zero indexed to better align with Python and other language standards.

## Scribe-Data 3.0.0

### ✨ Features

- Scribe-Data now has the ability to generate SQLite databases from formatted language data.
  - `data_to_sqlite.py` is used to read available JSON files and input their information into the databases.
- These databases are now sent to Scribe apps via defined paths.
  - `send_dbs_to_scribe.py` finds all available language databases and copies them.
  - Separating this step from the data update is in preparation for data import in the future where this will be an individual step.
- Scribe-Data now also creates autocomplete lexicons for each language within `data_to_sqlite.py`.
- JSON data is no longer able to be uploaded to Scribe app directories directly, with the SQLite directories now being exported instead.
- Emojis of singular nouns are now also linked to their plural counterparts if the plural isn't present in the emoji keyword outputs.
- The emoji process also now updates a column to the `data_table.txt` file for sharing on readmes with `update_data.py` maintaining it in the data update process.

### ♻️ Code Refactoring

- The Jupyter notebooks for autosuggestions and emojis as well as `update_data.py` were moved to the `extract_transform` directory given that they're not used to load data anymore.
  - Their code was refactored to reflect their new locations.
- Massive amounts of refactoring happened to achieve the shift in the data export method:
  - `format_WORD_TYPE.py` files export to a `formatted_data` directory within `extract_transform`.
  - Copies of all data JSONs that were originally in Scribe apps are now in the `formatted_data` directories.
  - Functions in `update_utils.py` were switched given that data is no longer uploaded into a `Data` directory within the language keyboard directories within Scribe apps.
  - Lots of functions and variables were renamed to make them more understandable.
  - Code to derive appropriate export locations within `format_WORD_TYPE.py` files was removed in favor of a language `formatted_data` directory.
  - regex was added as a dependency.
  - pylint comments were removed.
- Verb SPARQL query scripts for Spanish and Italian were simplified to remove unneeded repeat conditions ([#7](https://github.com/scribe-org/Scribe-Data/issues/7)).

### 🐞 Bug Fixes

- The statements in translation files have been fixed as they were improperly defined after a file was moved.

## Scribe-Data 2.2.2

### ✨ Features

- An option to remove the `is_base` and `rank` sub keys was added.

### ♻️ Code Refactoring

- The export filenames for emoji keywords were renamed to reflect their usage in autosuggestions and soon autocompletions as well.

## Scribe-Data 2.2.1

### ✨ Features

- The number of suggested emojis for words can now be limited.
- The total number of emojis that suggestions can be made for can now be limited.

## Scribe-Data 2.2.0

### ✨ Features

- Scribe-Data now allows the user to create JSONs of word-emoji key-value pairs ([#24](https://github.com/scribe-org/Scribe-Data/issues/24)).

## Scribe-Data 2.1.0

### ✨ Features

- Scribe-Data can now split Wikidata queries into multiple stages to break up those that were too large to run ([#21](https://github.com/scribe-org/Scribe-Data/issues/21)).

## Scribe-Data 2.0.0

### ✨ Features

- Scribe-Data now has the ability to download Wikipedia dumps of any language ([#15](https://github.com/scribe-org/Scribe-Data/issues/15)).
- Functions have been added to parse and clean the above dumps ([#15](https://github.com/scribe-org/Scribe-Data/issues/15)).
- Autosuggestions are generated from the cleaned texts by deriving most common words and those words that most commonly follow them ([#15](https://github.com/scribe-org/Scribe-Data/issues/15)).
- A query for profane words has been added and integrated into the autosuggest flow to make sure that inappropriate words are not included ([#16](https://github.com/scribe-org/Scribe-Data/issues/16)).
  - The adjectives column has been removed from Scribe data tables until support is offered.

### ♻️ Code Refactoring

- The error messages for incorrect args in update_data.py have been updated.

## Scribe-Data 1.0.1

### ✨ Features

- update_data.py now functions using SPARQLWrapper instead of wikidataintegrator.

### 🐞 Bug Fixes

- The data update process has been fixed to work for all queries.
- Hard coded strings for Spanish formatting files were fixed.
- The paths of update_data.py were changed to match the new package structure.

## Scribe-Data 1.0.0

### 🚀 Deployment

- Releasing a Python package so that codes are accessible and the structure is set for future project iterations.

### ✨ Features

- Data updates are done via a single file that loads new formatted data into each Scribe application.
- This will be expanded on in the future to create language packs that can be downloaded in app.

### 🗃️ Data

- Data extraction and formatting scripts for each of Scribe's current languages as well as those with significant data on Wikidata are included.

Languages include: French, German, Italian, Portuguese, Russian, Spanish, and Swedish.
Word types include: nouns, verbs, prepositions and translations.

### ♻️ Code Refactoring

- The data update process now updates files in Android and Desktop directories if they're present.
