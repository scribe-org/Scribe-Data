# Changelog

See the [releases for Scribe-Data](https://github.com/scribe-org/Scribe-Data/releases) for an up to date list of versions and their release dates.

Scribe-Data tries to follow [semantic versioning](https://semver.org/), a MAJOR.MINOR.PATCH version where increments are made of the:

- MAJOR version when we make incompatible API changes
- MINOR version when we add functionality in a backwards compatible manner
- PATCH version when we make backwards compatible bug fixes

Emojis for the following are chosen based on [gitmoji](https://gitmoji.dev/).

# [Unreleased] Scribe-Data 3.1.0

### ✨ Features

- The word "Scribe" is now added to language database nouns files if it's not already present.
- German contracted prepositions have been added to the German prepositions formatting process.
- Words that are upper case are now better included in the autocomplete lexicon with their lower case equivalents being removed.
- Autosuggestions are now capitalized or upper case if they're capitalized or upper case in the nouns table.

### ♻️ Code Refactoring

- Database output column names are now zero indexed to better align with Python and other language standards.

# Scribe-Data 3.0.0

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
- Verb SPARQL query scripts for Spanish and Italian were simplified to remove unneeded repeat conditions.

### 🐞 Bug Fixes

- The statements in translation files have been fixed as they were improperly defined after a file was moved.

# Scribe-Data 2.2.2

### ✨ Features

- An option to remove the `is_base` and `rank` sub keys was added.

### ♻️ Code Refactoring

- The export filenames for emoji keywords were renamed to reflect their usage in autosuggestions and soon autocompletions as well.

# Scribe-Data 2.2.1

### ✨ Features

- The number of suggested emojis for words can now be limited.
- The total number of emojis that suggestions can be made for can now be limited.

# Scribe-Data 2.2.0

### ✨ Features

- Scribe-Data now allows the user to create JSONs of word-emoji key-value pairs.

# Scribe-Data 2.1.0

### ✨ Features

- Scribe-Data can now split Wikidata queries into multiple stages to break up those that were too large to run.

# Scribe-Data 2.0.0

### ✨ Features

- Scribe-Data now has the ability to download Wikipedia dumps of any language.
- Functions have been added to parse and clean the above dumps.
- Autosuggestions are generated from the cleaned texts by deriving most common words and those words that most commonly follow them.
- A query for profane words has been added and integrated into the autosuggest flow to make sure that inappropriate words are not included.
  - The adjectives column has been removed from Scribe data tables until support is offered.

### ♻️ Code Refactoring

- The error messages for incorrect args in update_data.py have been updated.

# Scribe-Data 1.0.1

### ✨ Features

- update_data.py now functions using SPARQLWrapper instead of wikidataintegrator.

### 🐞 Bug Fixes

- The data update process has been fixed to work for all queries.
- Hard coded strings for Spanish formatting files were fixed.
- The paths of update_data.py were changed to match the new package structure.

# Scribe-Data 1.0.0

### 🚀 Deployment

Releasing a Python package so that codes are accessible and the structure is set for future project iterations.

### ✨ Features

- Data updates are done via a single file that loads new formatted data into each Scribe application.
- This will be expanded on in the future to create language packs that can be downloaded in app.

### 🗃️ Data

- Data extraction and formatting scripts for each of Scribe's current languages as well as those with significant data on Wikidata are included.

Languages include: French, German, Italian, Portuguese, Russian, Spanish, and Swedish.
Word types include: nouns, verbs, prepositions and translations.

### ♻️ Code Refactoring

- The data update process now updates files in Android and Desktop directories if they're present.
