<div align="center">
  <a href="https://github.com/scribe-org/Scribe-Data"><img src="https://raw.githubusercontent.com/scribe-org/Scribe-Data/main/.github/resources/images/ScribeDataLogo.png" height=150 alt="Scribe-Data Logo"></a>
</div>

[![platform](https://img.shields.io/badge/Wikidata-990000.svg?logo=wikidata&logoColor=ffffff)](https://github.com/scribe-org/Scribe-Data)
[![rtd](https://img.shields.io/readthedocs/scribe-data.svg?label=%20&logo=read-the-docs&logoColor=ffffff)](http://scribe-data.readthedocs.io/en/latest/)
[![issues](https://img.shields.io/github/issues/scribe-org/Scribe-Data?label=%20&logo=github)](https://github.com/scribe-org/Scribe-Data/issues)
[![language](https://img.shields.io/badge/Python%203-306998.svg?logo=python&logoColor=ffffff)](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md)
[![pypi](https://img.shields.io/pypi/v/scribe-data.svg?label=%20&color=4B8BBE)](https://pypi.org/project/scribe-data/)
[![pypistatus](https://img.shields.io/pypi/status/scribe-data.svg?label=%20)](https://pypi.org/project/scribe-data/)
[![license](https://img.shields.io/github/license/scribe-org/Scribe-Data.svg?label=%20)](https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt)
[![coc](https://img.shields.io/badge/Contributor%20Covenant-ff69b4.svg)](https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md)
[![mastodon](https://img.shields.io/badge/Mastodon-6364FF.svg?logo=mastodon&logoColor=ffffff)](https://wikis.world/@scribe)
[![matrix](https://img.shields.io/badge/Matrix-000000.svg?logo=matrix&logoColor=ffffff)](https://matrix.to/#/#scribe_community:matrix.org)

### Wikidata and Wikipedia language data extraction

**Scribe-Data** is a convenient command-line interface (CLI) for extracting and formatting language data from [Wikidata](https://www.wikidata.org/) and [Wikipedia](https://www.wikipedia.org/). Functionality includes allowing users to list, download, and manage language data directly from the terminal.

> [!NOTE]\
> The [contributing](#contributing) section has information for those interested, with the articles and presentations in [featured by](#featured-by) also being good resources for learning more about Scribe.

Scribe applications are available on [iOS](https://github.com/scribe-org/Scribe-iOS), [Android](https://github.com/scribe-org/Scribe-Android) (WIP) and [Desktop](https://github.com/scribe-org/Scribe-Desktop) (planned).

Check out Scribe's [architecture diagrams](https://github.com/scribe-org/Organization/blob/main/ARCHITECTURE.md) for an overview of the organization including our applications, services and processes. It depicts the projects that [Scribe](https://github.com/scribe-org) is developing as well as the relationships between them and the external systems with which they interact. Also check out the [Wikidata and Scribe Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md) for an overview of [Wikidata](https://www.wikidata.org/) and getting language data from it.

<a id="contents"></a>

# **Contents**

- [Process](#process)
- [Installation](#installation)
- [CLI Usage](#cli-usage)
- [Data Contracts](#data-contracts)
- [Contributing](#contributing)
- [Environment Setup](#environment-setup)
- [Featured By](#featured-by)

<a id="process"></a>

# Process [`⇧`](#contents)

The CLI commands defined within [scribe_data/cli](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/cli) and the notebooks within the various [scribe_data](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data) directories are used to update all data for [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS), with this functionality later being expanded to update [Scribe-Android](https://github.com/scribe-org/Scribe-Android) and [Scribe-Desktop](https://github.com/scribe-org/Scribe-Desktop) once they're active.

The main data update process in triggers [language based SPARQL queries](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/wikidata/language_data_extraction) to query language data from [Wikidata](https://www.wikidata.org/) using [SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper) as a URI. The autosuggestion process derives popular words from [Wikipedia](https://www.wikipedia.org/) as well as those words that normally follow them for an effective baseline feature until natural language processing methods are employed. Functions to generate autosuggestions are ran in [gen_autosuggestions.py](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/wikipedia/generate_autosuggestions.py). Emojis are further sourced from [Unicode CLDR](https://github.com/unicode-org/cldr), with this process being ran via the `scribe-data get -lang LANGUAGE -dt emoji-keywords` command.

<a id="installation"></a>

# Installation [`⇧`](#contents)

Scribe-Data is available for installation via using [uv](https://docs.astral.sh/uv/) (recommended) or [pip](https://pypi.org/project/scribe-data/).

### For Users

```bash
# Using uv (recommended - fast, Rust-based installer):
uv pip install scribe-data

# Or using pip:
pip install scribe-data
```

### For Development Build

```bash
git clone https://github.com/scribe-org/Scribe-Data.git  # or ideally your fork
cd Scribe-Data

# With uv (recommended):
uv sync --all-extras             # Install all dependencies
source .venv/bin/activate        # Activate venv (macOS/Linux)
# .venv\Scripts\activate         # Activate venv (Windows)

# Or with pip:
python -m venv .venv             # Create virtual environment
source .venv/bin/activate        # Activate venv (macOS/Linux)
# .venv\Scripts\activate         # Activate venv (Windows)
pip install -e .
```

<a id="cli-usage"></a>

# CLI Usage [`⇧`](#contents)

Scribe-Data provides a command-line interface (CLI) for efficient interaction with its language data functionality. Please see the [usage guide](https://github.com/scribe-org/Scribe-Data/blob/main/USAGE.md) or the [official documentation](https://scribe-data.readthedocs.io/) for detailed instructions.

### Basic Usage

To utilize the Scribe-Data CLI, you can execute variations of the following command in your terminal:

```bash
scribe-data -h  # view the cli options
scribe-data [command] [arguments]
```

### Available Commands

- `list` (`l`): Enumerate available languages, data types and their combinations.
- `get` (`g`): Retrieve data from Wikidata for specified languages and data types.
- `total` (`t`): Display the total available data for given languages and data types.
- `convert` (`c`): Transform data returned by Scribe-Data into different file formats.

### Command Examples

<p align="center">
  <img src="https://github.com/user-attachments/assets/653941a7-68bb-4d72-a0f1-3e29c75c5a16" alt="List, Total and Get GIF" width="500" height="300">
</p>

```bash
# Commands used in the above GIF:
scribe-data list --language
scribe-data list --data-type
scribe-data get --language English --data-type verbs -od ./scribe-data
scribe-data total --language English
```

<p align="center">
  <img src="https://github.com/user-attachments/assets/4cbb85ed-d853-4008-8db9-b77ffcbe2e84" alt="Interactive GIF" width="500" height="300">
</p>

```bash
# Commands used in the above GIF:
scribe-data get -i
scribe-data total -i
```

<a id="data-contracts"></a>

# Data Contracts [`⇧`](#contents)

[Wikidata](https://www.wikidata.org/) has lots of [language data](https://www.wikidata.org/wiki/Wikidata:Lexicographical_data) available, but not all of it is useful for all applications. In order to make the functionality of the Scribe-Data `get` requests as simple as possible, we made the decision to always return all data for the given languages and data types. Adding the ability to pass desired forms to the commands seemed cumbersome, and larger Scribe-Data requests should be parsing [Wikidata lexeme dumps](https://dumps.wikimedia.org/wikidatawiki/entities/) as the data source.

Scribe's solution to the get all functionality while preserving the ability to get specific forms is to allow users to filter the resulting data by contracts. The data contracts for Scribe's client applications can be found in the [scribe_data_contracts](./scribe_data_contracts/) directory. Data contracts are JSON objects where the values that are used in end applications are the keys and the resulting data identifiers based on Wikidata lexeme forms are the values. If the forms for a lexeme change, then the values would also change, but all that's needed is to update the contract for the application to function again.

Efficient client application data updates using Scribe-Data follow as such:

- New data is derived via the Scribe-Data CLI
- Contracts are written to map the data values to keys that are used in the application
- Scribe-Data is ran again to get new data in the future
- The contracts are checked to make sure that all contract values still exist within the resulting data
- The question is whether a form was added or removed from a data point such that its identifier has changed
- This is done via the following command:

```bash
scribe-data cc -cd DATA_CONTRACTS_DIRECTORY  # default data path is used
```

- If the check above passes, then new data can be added to the client applications
- If the check fails, then the contract values should be updated given the directions from the CLI and then new data can be loaded
- Getting just the data that's in the client application is done via the following command:

```bash
scribe-data fd -cd DATA_CONTRACTS_DIRECTORY  # default data paths are used
```

Updating contracts shouldn't be something that Scribe-Data users should have to do often if they're using stable data from [Wikidata](https://www.wikidata.org/). We provide this functionality given the wiki nature of the underlying data so that the Scribe community and others can easily react to potential changes in the lexeme data.

> [!NOTE]
> You can learn more about contracts and the process around them in [DATA_CONTRACTS.md](https://github.com/scribe-org/Organization/blob/main/DATA_CONTRACTS.md).

<a id="contributing"></a>

# Contributing [`⇧`](#contents)

<a href="https://matrix.to/#/#scribe_community:matrix.org">
  <img src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/MatrixLogoGrey.png" width="175" alt="Public Matrix Chat" align="right">
</a>

Scribe uses [Matrix](https://matrix.org/) for communications. You're more than welcome to [join us in our public chat rooms](https://matrix.to/#/#scribe_community:matrix.org) to share ideas, ask questions or just say hi to the team :) We'd suggest that you use the [Element](https://element.io/) client and [Element X](https://element.io/app) for a mobile app.

Please see the [contribution guidelines](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md) and [Wikidata and Scribe Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md) if you are interested in contributing to Scribe-Data. Work that is in progress or could be implemented is tracked in the [issues](https://github.com/scribe-org/Scribe-Data/issues) and [projects](https://github.com/scribe-org/Scribe-Data/projects).

> [!NOTE]\
> Just because an issue is assigned on GitHub doesn't mean the team isn't open to your contribution! Feel free to write [in the issues](https://github.com/scribe-org/Scribe-Data/issues) and we can potentially reassign it to you.

Those interested can further check the [`-next release-`](https://github.com/scribe-org/Scribe-Data/labels/-next%20release-) and [`-priority-`](https://github.com/scribe-org/Scribe-Data/labels/-priority-) labels in the [issues](https://github.com/scribe-org/Scribe-Data/issues) for those that are most important, as well as those marked [`good first issue`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) that are tailored for first-time contributors.

After your first few pull requests organization members would be happy to discuss granting you further rights as a contributor, with a maintainer role then being possible after continued interest in the project. Scribe seeks to be an inclusive and supportive organization. We'd love to have you on the team!

### Ways to Help [`⇧`](#contents)

- [Reporting bugs](https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=bug&template=bug_report.yml) as they're found 🐞
- Working on [new features](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3Afeature) ✨
- [Documentation](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3Adocumentation) for onboarding and project cohesion 📝
- Adding language data to [Scribe-Data](https://github.com/scribe-org/Scribe-Data/issues) via [Wikidata](https://www.wikidata.org/)! 🗃️

### Road Map [`⇧`](#contents)

The Scribe road map can be followed in the organization's [project board](https://github.com/orgs/scribe-org/projects/1) where we list the most important issues along with their priority, status and an indication of which sub projects they're included in (if applicable).

> [!NOTE]\
> Consider joining our [bi-weekly developer syncs](https://etherpad.wikimedia.org/p/scribe-dev-sync)!

### Data Edits [`⇧`](#contents)

> [!NOTE]\
> Please see the [Wikidata and Scribe Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md) for an overview of [Wikidata](https://www.wikidata.org/) and how Scribe uses it.

Scribe does not accept direct edits to the grammar JSON files as they are sourced from [Wikidata](https://www.wikidata.org/). Edits can be discussed and the queries themselves will be changed and ran before an update. If there is a problem with one of the files, then the fix should be made on [Wikidata](https://www.wikidata.org/) and not on Scribe. Feel free to let us know that edits have been made by [opening a data issue](https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=data&template=data_wikidata.yml) and we'll be happy to integrate them!

<a id="environment-setup"></a>

# Environment Setup [`⇧`](#contents)

> [!IMPORTANT]
>
> <details><summary>Suggested IDE extensions</summary>
>
> <p>
>
> VS Code
>
> - [blokhinnv.wikidataqidlabels](https://marketplace.visualstudio.com/items?itemName=blokhinnv.wikidataqidlabels)
> - [charliermarsh.ruff](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)
> - [qwtel.sqlite-viewer](https://marketplace.visualstudio.com/items?itemName=qwtel.sqlite-viewer)
> - [streetsidesoftware.code-spell-checker](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
>
> </p>
> </details>

The development environment for Scribe-Data can be installed via the following steps:

1. [Fork](https://docs.github.com/en/get-started/quickstart/fork-a-repo) the [Scribe-Data repo](https://github.com/scribe-org/Scribe-Data), clone your fork, and configure the remotes:

> [!NOTE]
>
> <details><summary>Consider using SSH</summary>
>
> <p>
>
> Alternatively to using HTTPS as in the instructions below, consider SSH to interact with GitHub from the terminal. SSH allows you to connect without a user-pass authentication flow.
>
> To run git commands with SSH, remember then to substitute the HTTPS URL, `https://github.com/...`, with the SSH one, `git@github.com:...`.
>
> - e.g. Cloning now becomes `git clone git@github.com:<your-username>/Scribe-Data.git`
>
> GitHub also has their documentation on how to [Generate a new SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent) 🔑
>
> </p>
> </details>

```bash
# Clone your fork of the repo into the current directory.
git clone https://github.com/<your-username>/Scribe-Data.git
# Navigate to the newly cloned directory.
cd Scribe-Data
# Assign the original repo to a remote called "upstream".
git remote add upstream https://github.com/scribe-org/Scribe-Data.git
```

- Now, if you run `git remote -v` you should see two remote repositories named:
  - `origin` (forked repository)
  - `upstream` (Scribe-Data repository)

2. Create a virtual environment for Scribe-Data (Python `>=3.12`), activate it and install dependencies:

> [!NOTE]
> First, install `uv` if you don't already have it by following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync --all-extras  # create .venv and install all dependencies from uv.lock

# Unix or macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate.bat  # .venv\Scripts\activate.ps1 (PowerShell)
```

After activating the virtual environment, set up [pre-commit](https://pre-commit.com/) by running:

```bash
pre-commit install
# uv run pre-commit run --all-files  # lint and fix common problems in the codebase
```

> [!NOTE]
> If you change dependencies in `pyproject.toml`, regenerate the lock file with the following command:
>
> ```bash
> uv lock  # refresh uv.lock for reproducible installs
> ```

See the [contribution guidelines](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md) for a more detailed explanation and troubleshooting.

> [!NOTE]
> Feel free to contact the team in the [Data room on Matrix](https://matrix.to/#/#ScribeData:matrix.org) if you're having problems getting your environment setup!

<a id="featured-by"></a>

# Featured By [`⇧`](#contents)

Please see the [blog posts page on our website](https://scri.be/docs/about/blog-posts) for a list of articles on Scribe, and feel free to open a pull request to add one that you've written at [scribe-org/scri.be](https://github.com/scribe-org/scri.be)!

### Organizations

The following organizations have supported the development of Scribe projects through various programs. Thank you all! 💙

<div align="center">
  <br>
    <a href="https://tech-news.wikimedia.de/en/2022/03/18/lexicographical-data-for-language-learners-the-wikidata-based-app-scribe/"><img width="180" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikimediaDeutschlandLogo.png" alt="Wikimedia Deutschland logo linking to an article on Scribe in the tech news blog."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://www.mediawiki.org/wiki/New_Developers#Scribe"><img width="180" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikimediaFoundationLogo.png" alt="Wikimedia Foundation logo linking to the MediaWiki new developers page."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>

<div align="center">
  <br>
    <a href="https://summerofcode.withgoogle.com/"><img width="140" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/GSoCLogo.png" alt="Google Summer of Code logo linking to its website."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://www.outreachy.org/"><img width="350" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/OutreachyLogo.png" alt="Outreachy logo linking to its website."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>

# Powered By [`⇧`](#contents)

### Contributors

Many thanks to all the [Scribe-Data contributors](https://github.com/scribe-org/Scribe-Data/graphs/contributors)! 🚀

<a href="https://github.com/scribe-org/Scribe-Data/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=scribe-org/Scribe-Data" />
</a>

### Wikimedia Communities

<div align="center">
  <br>
    <a href="https://www.wikidata.org/">
      <img width="240" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikidataLogo.png" alt="Wikidata logo">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://www.wikipedia.org/">
      <img width="160" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikipediaLogo.png" alt="Wikipedia logo">
    </a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>
