# Contributing to Scribe-Data

Thank you for your interest in contributing!

Please take a moment to review this document in order to make the contribution process easy and effective for everyone involved.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open-source project. In return, and in accordance with this project's [code of conduct](https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md), other contributors will reciprocate that respect in addressing your issue or assessing changes and features.

If you have questions or would like to communicate with the team, please [join us in our public Matrix chat rooms](https://matrix.to/#/#scribe_community:matrix.org). We'd be happy to hear from you!

<a id="contents"></a>

## Contents

- [First steps as a contributor](#first-steps)
- [Learning the tech stack](#learning-the-tech)
- [Development environment](#dev-env)
- [Testing](#testing)
- [Issues and projects](#issues-projects)
- [Bug reports](#bug-reports)
- [Feature requests](#feature-requests)
- [Pull requests](#pull-requests)
- [Data edits](#data-edits)
- [Documentation](#documentation)

<a id="first-steps"></a>

## First steps as a contributor [`⇧`](#contents)

Thank you for your interest in contributing to Scribe-Data! We look forward to welcoming you to the community and working with you to build tools for language learners to communicate effectively :) The following are some suggested steps for people interested in joining our community:

- Please join the [public Matrix chat](https://matrix.to/#/#scribe_community:matrix.org) to connect with the community
  - [Matrix](https://matrix.org/) is a network for secure, decentralized communication
  - Scribe would suggest that you use the [Element](https://element.io/) client
  - The [General](https://matrix.to/#/!yQJjLmluvlkWttNhKo:matrix.org?via=matrix.org) and [Data](https://matrix.to/#/#ScribeData:matrix.org) channels would be great places to start!
  - Feel free to introduce yourself and tell us what your interests are if you're comfortable :)
- Read through this contributing guide for all the information you need to contribute
- Look into issues marked [`good first issue`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22) and the [Projects board](https://github.com/orgs/scribe-org/projects/1) to get a better understanding of what you can work on
- Check out our [public designs on Figma](https://www.figma.com/file/c8945w2iyoPYVhsqW7vRn6/scribe_public_designs?type=design&node-id=405-464&mode=design&t=E3ccS9Z8MDVSizQ4-0) to understand Scribes's goals and direction
- Consider joining our [bi-weekly developer sync](https://etherpad.wikimedia.org/p/scribe-dev-sync)!

> [!NOTE]
> Those new to Python or wanting to work on their Python skills are more than welcome to contribute! The team would be happy to help you on your development journey :)

<a id="learning-the-tech"></a>

## Learning the tech stack [`⇧`](#contents)

Scribe is very open to contributions from people in the early stages of their coding journey! The following is a select list of documentation pages to help you understand the technologies we use.

<details><summary>Docs for those new to programming</summary>
<p>

- [Mozilla Developer Network Learning Area](https://developer.mozilla.org/en-US/docs/Learn)
  - Doing MDN sections for HTML, CSS and JavaScript is the best ways to get into web development!
- [Open Source Guides](https://opensource.guide/)
  - Guides from GitHub about open-source software including how to start and much more!

</p>
</details>

<details><summary>Python learning docs</summary>
<p>

- [Python getting started guide](https://docs.python.org/3/tutorial/introduction.html)
- [Python getting started resources](https://www.python.org/about/gettingstarted/)

</p>
</details>

<a id="dev-env"></a>

## Development environment [`⇧`](#contents)

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

> [!NOTE]
> If you are having issues with pre-commit and want to send along your changes regardless, you can ignore the pre-commit hooks via the following:
>
> ```bash
> git commit --no-verify -m "COMMIT_MESSAGE"
> ```

If you face any issues, consider reinstalling Scribe-data by running the following:

```bash
# Install the new version of Scribe-Data:
pip uninstall scribe-data
pip install .  # or pip install scribe-data

# Update the entry_points and console_scripts:
python setup.py egg_info
```

Note that you may need to run this command every time you make any change to the code to have them be reflected in the development Scribe-Data:

```bash
pip install -e .
```

> [!NOTE]
> Feel free to contact the team in the [Data room on Matrix](https://matrix.to/#/#ScribeData:matrix.org) if you're having problems getting your environment setup!

<a id="testing"></a>

## Testing [`⇧`](#contents)

In addition to the [pre-commit](https://pre-commit.com/) hooks that are set up during the [development environment section](#dev-env), Scribe-Data also includes a testing suite that should be ran before all pull requests and subsequent commits. Please run the following in the project root:

```bash
pytest
```

<a id="issues-projects"></a>

## Issues and projects [`⇧`](#contents)

The [issue tracker for Scribe-Data](https://github.com/scribe-org/Scribe-Data/issues) is the preferred channel for [bug reports](#bug-reports), [features requests](#feature-requests) and [submitting pull requests](#pull-requests). Scribe also organizes related issues into [projects](https://github.com/scribe-org/Scribe-Data/projects).

> [!NOTE]\
> Just because an issue is assigned on GitHub doesn't mean that the team isn't interested in your contribution! Feel free to write [in the issues](https://github.com/scribe-org/Scribe-Data/issues) and we can potentially reassign it to you.

Be sure to check the [`-next release-`](https://github.com/scribe-org/Scribe-Data/labels/-next%20release-) and [`-priority-`](https://github.com/scribe-org/Scribe-Data/labels/-priority-) labels in the [issues](https://github.com/scribe-org/Scribe-Data/issues) for those that are most important, as well as those marked [`good first issue`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22) that are tailored for first time contributors.

<a id="bug-reports"></a>

## Bug reports [`⇧`](#contents)

A bug is a _demonstrable problem_ that is caused by the code in the repository. Good bug reports are extremely helpful - thank you!

Guidelines for bug reports:

1. **Use the GitHub issue search** to check if the issue has already been reported.

2. **Check if the issue has been fixed** by trying to reproduce it using the latest `main` or development branch in the repository.

3. **Isolate the problem** to make sure that the code in the repository is _definitely_ responsible for the issue.

**Great Bug Reports** tend to have:

- A quick summary
- Steps to reproduce
- What you expected would happen
- What actually happens
- Notes (why this might be happening, things tried that didn't work, etc)

To make the above steps easier, the Scribe team asks that contributors report bugs using the [bug report template](https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=bug_report.yml), with these issues further being marked with the [`bug`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3Abug) label.

Again, thank you for your time in reporting issues!

<a id="feature-requests"></a>

## Feature requests [`⇧`](#contents)

Feature requests are more than welcome! Please take a moment to find out whether your idea fits with the scope and aims of the project. When making a suggestion, provide as much detail and context as possible, and further make clear the degree to which you would like to contribute in its development. Feature requests are marked with the [`feature`](https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3Afeature) label, and can be made using the [feature request](https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=feature_request.yml) template.

<a id="pull-requests"></a>

## Pull requests [`⇧`](#contents)

Good pull requests - patches, improvements and new features - are the foundation of our community making Scribe-Data. They should remain focused in scope and avoid containing unrelated commits. Note that all contributions to this project will be made under [the specified license](https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt) and should follow the coding indentation and style standards ([contact us](https://matrix.to/#/#scribe_community:matrix.org) if unsure).

**Please ask first** before embarking on any significant pull request (implementing features, refactoring code, etc), otherwise you risk spending a lot of time working on something that the developers might not want to merge into the project. With that being said, major additions are very appreciated!

When making a contribution, adhering to the [GitHub flow](https://guides.github.com/introduction/flow/index.html) process is the best way to get your work merged:

1. If you cloned a while ago, get the latest changes from upstream:

   ```bash
   git checkout <dev-branch>
   git pull upstream <dev-branch>
   ```

2. Create a new topic branch (off the main project development branch) to contain your feature, change, or fix:

   ```bash
   git checkout -b <topic-branch-name>
   ```

3. Commit your changes in logical chunks, and please try to adhere to [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

> [!NOTE]
> The following are tools and methods to help you write good commit messages ✨
>
> - [commitlint](https://commitlint.io/) helps write [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/)
> - Git's [interactive rebase](https://docs.github.com/en/github/getting-started-with-github/about-git-rebase) cleans up commits

4. Locally merge (or rebase) the upstream development branch into your topic branch:

   ```bash
   git pull --rebase upstream <dev-branch>
   ```

5. Push your topic branch up to your fork:

   ```bash
   git push origin <topic-branch-name>
   ```

6. [Open a Pull Request](https://help.github.com/articles/using-pull-requests/) with a clear title and description.

Thank you in advance for your contributions!

<a id="data-edits"></a>

## Data edits [`⇧`](#contents)

> [!NOTE]\
> Please see the [Wikidata and Scribe Guide](https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md) for an overview of [Wikidata](https://www.wikidata.org/) and how Scribe uses it.

Scribe does not accept direct edits to the grammar JSON files as they are sourced from [Wikidata](https://www.wikidata.org/). Edits can be discussed and the [Scribe-Data](https://github.com/scribe-org/Scribe-Data) queries will be changed and ran before an update. If there is a problem with one of the files, then the fix should be made on [Wikidata](https://www.wikidata.org/) and not on Scribe. Feel free to let us know that edits have been made by [opening an issue](https://github.com/scribe-org/Scribe-Data/issues) and we'll be happy to integrate them!

<a id="documentation"></a>

## Documentation [`⇧`](#contents)

The documentation for Scribe-Data can be found at [scribe-data.readthedocs.io](https://scribe-data.readthedocs.io/en/latest/). Documentation is an invaluable way to contribute to coding projects as it allows others to more easily understand the project structure and contribute. Issues related to documentation are marked with the [`documentation`](https://github.com/scribe-org/Scribe-Data/labels/documentation) label.

### Function Docstrings

Scribe-Data generally follows [numpydoc conventions](https://numpydoc.readthedocs.io/en/latest/format.html) for documenting functions and Python code in general. Function docstrings should have the following format:

```py
def example_function(argument: argument_type) -> return_type:
    """
    An example docstring for a function so others understand your work.

    Parameters
    ----------
    argument : argument_type
        Description of your argument.

    Returns
    -------
    return_value : return_type
        Description of your return value.

    Raises
    ------
    ErrorType
        Description of the error and the condition that raises it.
    """

    ...

    return return_value
```

### Building the Docs

Use the following commands to build the documentation locally:

```bash
cd docs
make html
```

You can then open `index.html` within `docs/build/html` to check the local version of the documentation.
