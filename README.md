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
- [Contributing](#contributing)
- [Environment Setup](#environment-setup)
- [Featured By](#featured-by)

<a id="Process"></a>

# Process [`⇧`](#contents)

The CLI commands defined within [scribe_data/cli](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/cli) and the notebooks within the various [scribe_data](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data) directories are used to update all data for [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS), with this functionality later being expanded to update [Scribe-Android](https://github.com/scribe-org/Scribe-Android) and [Scribe-Desktop](https://github.com/scribe-org/Scribe-Desktop) once they're active.

The main data update process in triggers [language based SPARQL queries](https://github.com/scribe-org/Scribe-Data/tree/main/src/scribe_data/wikidata/language_data_extraction) to query language data from [Wikidata](https://www.wikidata.org/) using [SPARQLWrapper](https://github.com/RDFLib/sparqlwrapper) as a URI. The autosuggestion process derives popular words from [Wikipedia](https://www.wikipedia.org/) as well as those words that normally follow them for an effective baseline feature until natural language processing methods are employed. Functions to generate autosuggestions are ran in [gen_autosuggestions.ipynb](https://github.com/scribe-org/Scribe-Data/blob/main/src/scribe_data/wikipedia/gen_autosuggestions.ipynb). Emojis are further sourced from [Unicode CLDR](https://github.com/unicode-org/cldr), with this process being ran via the `scribe-data get -lang LANGUAGE -dt emoji-keywords` command.

<a id="installation"></a>

# Installation [`⇧`](#contents)

Scribe-Data is available for installation via [pip](https://pypi.org/project/scribe-data/):

```bash
pip install scribe-data

# For a development build:
git clone https://github.com/scribe-org/Scribe-Data.git  # or ideally your fork
cd Scribe-Data
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

<a id="contributing"></a>

# Contributing [`⇧`](#contents)

<a href="https://matrix.to/#/#scribe_community:matrix.org"><img src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/MatrixLogoGrey.png" height="50" alt="Public Matrix Chat" align="right"></a>

Scribe uses [Matrix](https://matrix.org/) for communications. You're more than welcome to [join us in our public chat rooms](https://matrix.to/#/#scribe_community:matrix.org) to share ideas, ask questions or just say hi :)

Please see the [contribution guidelines](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md) and [Wikidata and Scribe Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md) if you are interested in contributing to Scribe-Data. Work that is in progress or could be implemented is tracked in the [issues](https://github.com/scribe-org/Scribe-Data/issues) and [projects](https://github.com/scribe-org/Scribe-Data/projects).

> [!NOTE]\
> Just because an issue is assigned on GitHub doesn't mean that the team isn't interested in your contribution! Feel free to write [in the issues](https://github.com/scribe-org/Scribe-Data/issues) and we can potentially reassign it to you.

Those interested can further check the [`-next release-`](https://github.com/scribe-org/Scribe-Data/labels/-next%20release-) and [`-priority-`](https://github.com/scribe-org/Scribe-Data/labels/-priority-) labels in the [issues](https://github.com/scribe-org/Scribe-Data/issues) for those that are most important, as well as those marked [`good first issue`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) that are tailored for first time contributors.

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

2. Use [Python venv](https://docs.python.org/3/library/venv.html) to create the local development environment within your Scribe-Data directory:

- On Unix or MacOS, run:

  ```bash
  python3 -m venv venv  # make an environment named venv
  source venv/bin/activate # activate the environment
  ```

- On Windows (using Command Prompt), run:

  ```bash
  python -m venv venv
  venv\Scripts\activate.bat
  ```

- On Windows (using PowerShell), run:

  ```bash
  python -m venv venv
  venv\Scripts\activate.ps1
  ```

After activating the virtual environment, install the required dependencies and set up [pre-commit](https://pre-commit.com/) by running:

```bash
pip install --upgrade pip  # make sure that pip is at the latest version
pip install -r requirements-dev.txt  # install development dependencies
pip install -e .  # install the local version of Scribe-Data
pre-commit install  # install pre-commit hooks
# pre-commit run --all-files  # lint and fix common problems in the codebase
```

See the [contribution guidelines](https://github.com/scribe-org/Scribe-Data/blob/main/CONTRIBUTING.md) for a more detailed explanation and troubleshooting.

> [!NOTE]
> Feel free to contact the team in the [Data room on Matrix](https://matrix.to/#/#ScribeData:matrix.org) if you're having problems getting your environment setup!

<a id="featured-by"></a>

# Featured By [`⇧`](#contents)

<details open><summary><strong>Articles and Presentations on Scribe</strong></summary>
<p>

<strong>2024</strong>

- October: [Blog post on Medium](https://medium.com/@arpita151103/scribe-an-open-source-solution-for-language-learning-and-data-accessibility-092dab026fd6) discussing the [Scribe-Data](https://github.com/scribe-org/Scribe-Data) development process, community and features
- October: [Blog post on medium](https://medium.com/@mhmohona/ins-and-outs-of-scribe-data-cli-bd51202aa7c6) describing the main features of [Scribe-Data](https://github.com/scribe-org/Scribe-Data)
- September: [Final Google Summer of Code report](https://medium.com/@mhmohona/the-final-stretch-gsoc-journey-with-scribe-data-1740084c958d) on the creation of the [Scribe-Data](https://github.com/scribe-org/Scribe-Data) CLI
- August: [Final Google Summer of Code report](https://jagmarcel.hashnode.dev/gsoc-2024-final-report) on the creation of Scribe's cross-language translation functionality
- July: [Blog post on Medium](https://medium.com/@mhmohona/halfway-there-my-gsoc-adventure-with-scribe-data-cli-2ffe6d727ecb) about the progress on creating the [Scribe-Data](https://github.com/scribe-org/Scribe-Data) CLI
- July: [Blog post on Hashnode](https://jagmarcel.hashnode.dev/gsoc-2024-midterm-report) providing an midterm report on the localization and translation expansion for [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS)
- July: [Blog post on Hashnode](https://jagmarcel.hashnode.dev/my-first-experiences-with-gsoc) about the initial steps towards the localization of [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS)
- June: [Blog post on Medium](https://medium.com/@mhmohona/first-month-as-a-gsoc-intern-building-scribe-data-cli-d0c12c9e8371) about the planned [Scribe-Data](https://github.com/scribe-org/Scribe-Data) CLI
- April: [Blog post on Medium](https://medium.com/@mhmohona/scribe-data-a-guide-to-open-source-language-data-a801c59db4c9) about [Scribe-Data](https://github.com/scribe-org/Scribe-Data) and its functionalities
- February: [Presentation slides](https://docs.google.com/presentation/d/1lMhYiQx1R99SVGhbikUGjOVaFgPPASvbzM2Bsu3NXSg/edit?usp=sharing) for Scribe's participation at the [Wikimedia Tech Safari Program](https://www.mediawiki.org/wiki/Wikimedia_Tech_Safari_Program)

<strong>2023</strong>

- August: [Scribe-iOS final submission report for Google Summer of Code 2023](https://saurabhjamadagni.hashnode.dev/gsoc-23-final-work-submission)
- June: [Scribe-iOS development blog post on Nested UITableViews & Apple's built-in ViewControllers in app menu](https://saurabhjamadagni.hashnode.dev/nested-uitableviews-apples-built-in-viewcontrollers) for [GSoC '23](https://www.mediawiki.org/wiki/Google_Summer_of_Code/2023#Accepted_projects:~:text=links%3A%20Phabricator%20issue-,3.%20Adding%20a%20Menu%20and%20Keyboards%20to%20Scribe%2DiOS,-%5Bedit%5D)
- March: [Presentation slides](https://docs.google.com/presentation/d/1W4ZkGi9UDDiTxM_silEij0gTE8YEubluHxe78xoqEP0/edit?usp=sharing) for a talk at [Berlin Hack and Tell](https://bhnt.c-base.org/) ([Hack of the month winner 🏆](https://bhnt.c-base.org/2023-03-28-no87-moore-hacks))

<strong>2022</strong>

- August: [Presentation slides](https://docs.google.com/presentation/d/12WNSt5xgNIAmSxPfvjno9-sBMGlvxG_xSaAxmHQDRNQ/edit?usp=sharing) for a session at the [2022 Wikimania Hackathon](https://wikimania.wikimedia.org/wiki/2022:Hackathon)
- July: [Presentation slides](https://docs.google.com/presentation/d/10Ai0-b8XUj5u9Hw4UgBtB7ufiPhvfFrb1vEUEyXYr5w/edit?usp=sharing) for a talk at [CocoaHeads Berlin](https://www.meetup.com/cocoaheads-berlin/)
- July: [Video on Scribe](https://www.youtube.com/watch?v=4GpFN0gGmy4&list=PL66MRMNlLyR7p9wsYVfuqJOjKZpbuwp8U&index=6) for [Wikimedia Celtic Knot 2022](https://meta.wikimedia.org/wiki/Celtic_Knot_Conference_2022)
- June: [Presentation slides](https://docs.google.com/presentation/d/1K2lj8PPgdx12I-xuhm--CBLrGm-Cz50NJmbp96zpGrk/edit?usp=sharing) for a talk with the [LD4 Wikidata Affinity Group](https://www.wikidata.org/wiki/Wikidata:WikiProject_LD4_Wikidata_Affinity_Group)
- June: [Scribe](https://github.com/scribe-org) featured for new developers on [MediaWiki](https://www.mediawiki.org/wiki/New_Developers#Scribe)
- May: [Presentation slides](https://docs.google.com/presentation/d/1Cu3VwQ3lJUp5W84YDe0AFYS-6zfBxKsm0MI-OMl_IzY/edit?usp=sharing) for [Wikimedia Hackathon 2022](https://www.mediawiki.org/wiki/Wikimedia_Hackathon_2022)
- March: [Blog post](https://tech-news.wikimedia.de/en/2022/03/18/lexicographical-data-for-language-learners-the-wikidata-based-app-scribe/) on [Scribe-iOS](https://github.com/scribe-org/Scribe-iOS) for [Wikimedia Tech News](https://tech-news.wikimedia.de/en/homepage/) ([DE](https://tech-news.wikimedia.de/2022/03/18/sprachenlernen-mit-lexikografische-daten-die-wikidata-basierte-app-scribe/) / [Tweet](https://twitter.com/wikidata/status/1507335538596106257?s=20&t=YGRGamftI-5B_VwQ_bFRhA))
- March: [Presentation slides](https://docs.google.com/presentation/d/16ld_rCbwJCiAdRrfhF-Fq9Wm_ciHCbk_HCzGQs6TB1Q/edit?usp=sharing) for [Wikidata Data Reuse Days 2022](https://diff.wikimedia.org/event/wikidata-data-reuse-days-2022/)

</p>
</details>

<div align="center">
  <br>
    <a href="https://tech-news.wikimedia.de/en/2022/03/18/lexicographical-data-for-language-learners-the-wikidata-based-app-scribe/"><img height="120"src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikimediaDeutschlandLogo.png" alt="Wikimedia Deutschland logo linking to an article on Scribe in the tech news blog."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://www.mediawiki.org/wiki/New_Developers#Scribe"><img height="120" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikimediaFoundationLogo.png" alt="Wikimedia Foundation logo linking to the MediaWiki new developers page."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>

<div align="center">
  <br>
    <a href="https://summerofcode.withgoogle.com/"><img height="120" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/GSoCLogo.png" alt="Google Summer of Code logo linking to its website."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
    <a href="https://www.outreachy.org/"><img height="90" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/OutreachyLogo.png" alt="Outreachy logo linking to its website."></a>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>

# Powered By [`⇧`](#contents)

### Contributors

Many thanks to all the [Scribe-Data contributors](https://github.com/scribe-org/Scribe-Data/graphs/contributors)! 🚀

<a href="https://github.com/scribe-org/Scribe-Data/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=scribe-org/Scribe-Data" />
</a>

### Blog posts

<details><summary><strong>List of referenced posts</strong></summary>
<p>

- [Building a Recommendation System Using Neural Network Embeddings](https://towardsdatascience.com/building-a-recommendation-system-using-neural-network-embeddings-1ef92e5c80c9) by [WillKoehrsen](https://github.com/WillKoehrsen)

- [Wikipedia Data Science: Working with the World’s Largest Encyclopedia](https://towardsdatascience.com/wikipedia-data-science-working-with-the-worlds-largest-encyclopedia-c08efbac5f5c) by [WillKoehrsen](https://github.com/WillKoehrsen)

</p>
</details>

### Wikimedia Communities

<div align="center">
  <br>
  <a href="https://www.wikidata.org/"><img height="175" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikidataLogo.png" alt="Wikidata logo"></a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <a href="https://www.wikipedia.org/"><img height="190" src="https://raw.githubusercontent.com/scribe-org/Organization/main/resources/images/logos/WikipediaLogo.png" alt="Wikipedia logo"></a>
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <br>
</div>
