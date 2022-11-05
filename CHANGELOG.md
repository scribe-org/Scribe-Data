# Changelog

See the [releases for Scribe-Data](https://github.com/scribe-org/Scribe-Data/releases) for an up to date list of versions and their release dates.

Scribe-Data tries to follow [semantic versioning](https://semver.org/), a MAJOR.MINOR.PATCH version where increments are made of the:

- MAJOR version when we make incompatible API changes
- MINOR version when we add functionality in a backwards compatible manner
- PATCH version when we make backwards compatible bug fixes

Emojis for the following are chosen based on [gitmoji](https://gitmoji.dev/).

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
