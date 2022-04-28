# Changelog

Scribe-Data tries to follow [semantic versioning](https://semver.org/), a MAJOR.MINOR.PATCH version where increments are made of the:

- MAJOR version when we make incompatible API changes
- MINOR version when we add functionality in a backwards compatible manner
- PATCH version when we make backwards compatible bug fixes

Emojis for the following are chosen based on [gitmoji](https://gitmoji.dev/).

# Next release

### ♻️ Code Refactoring

- Update error messages for incorrect args in update_data.py

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
