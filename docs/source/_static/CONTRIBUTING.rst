Contributing to Scribe-Data
===========================

Thank you for your interest in contributing!

Please take a moment to review this document in order to make the contribution process easy and effective for everyone involved.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open-source project. In return, and in accordance with this project's code of conduct, other contributors will reciprocate that respect in addressing your issue or assessing changes and features.

If you have questions or would like to communicate with the team, please join us in our public Matrix chat rooms <https://matrix.to/#/#scribe_community:matrix.org>_. We'd be happy to hear from you!

.. _contents:

Contents
--------

- First steps as a contributor
- Learning the tech stack
- Development environment
- Testing
- Issues and projects
- Bug reports
- Feature requests
- Pull requests
- Data edits
- Documentation

First steps as a contributor
----------------------------

Thank you for your interest in contributing to Scribe-Data! We look forward to welcoming you to the community and working with you to build tools for language learners to communicate effectively. The following are some suggested steps for people interested in joining our community:

- Please join the public Matrix chat <https://matrix.to/#/#scribe_community:matrix.org>_ to connect with the community
  - Matrix <https://matrix.org/>_ is a network for secure, decentralized communication
  - We suggest using the Element <https://element.io/>_ client and Element X <https://element.io/app>_ for a mobile app
  - The General <https://matrix.to/#/!yQJjLmluvlkWttNhKo:matrix.org?via=matrix.org>_ and Data <https://matrix.to/#/#ScribeData:matrix.org>_ channels are great places to start
  - Feel free to introduce yourself and tell us what your interests are if you're comfortable
- Read through this contributing guide for all the information you need to contribute
- Look into issues marked ``good first issue`` (`open issues labeled "good first issue" <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>`_) and the Projects board (`Scribe-Data projects <https://github.com/orgs/scribe-org/projects/1>`_) to get a better understanding of what you can work on
- Check out our public designs on Figma <https://www.figma.com/file/c8945w2iyoPYVhsqW7vRn6/scribe_public_designs?type=design&node-id=405-464&mode=design&t=E3ccS9Z8MDVSizQ4-0>_ to understand Scribe's goals and direction
- Consider joining our bi-weekly developer sync <https://etherpad.wikimedia.org/p/scribe-dev-sync>_

.. note::

   Those new to Python or wanting to work on their Python skills are more than welcome to contribute! The team would be happy to help you on your development journey.

Learning the tech stack
-----------------------

Scribe is very open to contributions from people in the early stages of their coding journey. The following is a select list of documentation pages to help you understand the technologies we use.

Docs for those new to programming
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

- Mozilla Developer Network Learning Area <https://developer.mozilla.org/en-US/docs/Learn>_
  - Doing MDN sections for HTML, CSS and JavaScript is one of the best ways to get into web development!
- Open Source Guides <https://opensource.guide/>_
  - Guides from GitHub about open-source software including how to start and much more

Python learning docs
~~~~~~~~~~~~~~~~~~~~

- Python getting started guide <https://docs.python.org/3/tutorial/introduction.html>_
- Python getting started resources <https://www.python.org/about/gettingstarted/>_

Development environment
-----------------------

.. important::

   Suggested IDE extensions (VS Code)

   - blokhinnv.wikidataqidlabels
   - charliermarsh.ruff
   - qwtel.sqlite-viewer
   - streetsidesoftware.code-spell-checker

The development environment for Scribe-Data can be installed via the following steps:

1. Fork the Scribe-Data repo <https://github.com/scribe-org/Scribe-Data>_, clone your fork, and configure the remotes.

.. note::

   Consider using SSH

   Alternatively to using HTTPS as in the instructions below, consider SSH to interact with GitHub from the terminal. SSH allows you to connect without a user-pass authentication flow.

   To run git commands with SSH, substitute the HTTPS URL, ``https://github.com/...``, with the SSH one, ``git@github.com:...``.

   Example:

   ``git clone git@github.com:<your-username>/Scribe-Data.git``

   GitHub also has documentation on how to generate an SSH key: Generate a new SSH key <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent>_.

.. code-block:: bash

   # Clone your fork of the repo into the current directory.
   git clone https://github.com/<your-username>/Scribe-Data.git
   # Navigate to the newly cloned directory.
   cd Scribe-Data
   # Assign the original repo to a remote called "upstream".
   git remote add upstream https://github.com/scribe-org/Scribe-Data.git

- Now, if you run ``git remote -v`` you should see two remote repositories named:
  - ``origin`` (forked repository)
  - ``upstream`` (Scribe-Data repository)

2. Create a virtual environment for Scribe-Data (Python >= 3.12), activate it and install dependencies.

.. note::

   First, install ``uv`` if you don't already have it by following the official installation guide: UV installation <https://docs.astral.sh/uv/getting-started/installation/>_.

.. code-block:: bash

   uv sync --all-extras  # create .venv and install all dependencies from uv.lock

   # Unix or macOS:
   source .venv/bin/activate

   # Windows:
   .venv\Scripts\activate.bat  # .venv\Scripts\activate.ps1 (PowerShell)

After activating the virtual environment, set up pre-commit <https://pre-commit.com/>_ by running:

.. code-block:: bash

   pre-commit install
   # uv run pre-commit run --all-files  # lint and fix common problems in the codebase

.. note::

   If you change dependencies in ``pyproject.toml``, regenerate the lock file with:

.. code-block:: bash

   uv lock  # refresh uv.lock for reproducible installs

.. note::

   If you are having issues with pre-commit and want to send along your changes regardless, you can ignore the pre-commit hooks via:

.. code-block:: bash

   git commit --no-verify -m "COMMIT_MESSAGE"

If you face any issues, consider reinstalling Scribe-Data by running the following:

.. code-block:: bash

   # Install the new version of Scribe-Data:
   pip uninstall scribe-data
   pip install -e .  # or pip install scribe-data

   # Update the entry_points and console_scripts:
   python setup.py egg_info

.. note::

   Feel free to contact the team in the Data room on Matrix <https://matrix.to/#/#ScribeData:matrix.org>_ if you're having problems getting your environment setup!

Testing
-------

In addition to the pre-commit hooks that are set up during the development environment section, Scribe-Data also includes a testing suite that should be run before all pull requests and subsequent commits. Please run the following in the project root:

.. code-block:: bash

   pytest

Issues and projects
-------------------

The issue tracker for Scribe-Data <https://github.com/scribe-org/Scribe-Data/issues>_ is the preferred channel for bug reports, feature requests and submitting pull requests. Scribe also organizes related issues into projects <https://github.com/scribe-org/Scribe-Data/projects>_.

.. note::

   Just because an issue is assigned on GitHub doesn't mean the team isn't open to your contribution! Feel free to write in the issues <https://github.com/scribe-org/Scribe-Data/issues>_ and we can potentially reassign it to you.

Be sure to check the ``-next release-`` label <https://github.com/scribe-org/Scribe-Data/labels/-next%20release->_ and the ``-priority-`` label <https://github.com/scribe-org/Scribe-Data/labels/-priority->_ in issues for those that are most important, as well as those marked ``good first issue`` (`good first issue label <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`_) that are tailored for first-time contributors.

Bug reports
-----------

A bug is a demonstrable problem that is caused by the code in the repository. Good bug reports are extremely helpful — thank you!

Guidelines for bug reports:

1. Use the GitHub issue search to check if the issue has already been reported.
2. Check if the issue has been fixed by trying to reproduce it using the latest ``main`` or development branch in the repository.
3. Isolate the problem to make sure that the code in the repository is definitely responsible for the issue.

Great Bug Reports tend to have:

- A quick summary
- Steps to reproduce
- What you expected would happen
- What actually happens
- Notes (why this might be happening, things tried that didn't work, etc)

To make the above steps easier, the Scribe team asks that contributors report bugs using the bug report template <https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=bug_report.yml>_, with these issues further being marked with the Bug type <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue%20state%3Aopen%20type%3ABug>_.

Again, thank you for your time in reporting issues!

Feature requests
----------------

Feature requests are more than welcome! Please take a moment to find out whether your idea fits with the scope and aims of the project. When making a suggestion, provide as much detail and context as possible, and make clear the degree to which you would like to contribute in its development. Feature requests are marked with the Feature type <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue%20state%3Aopen%20type%3AFeature>_, and can be made using the feature request template <https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=feature_request.yml>_.

Pull requests
-------------

Good pull requests — patches, improvements and new features — are the foundation of our community making Scribe-Data. They should remain focused in scope and avoid containing unrelated commits. Note that all contributions to this project will be made under the specified license <https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt>_ and should follow the coding indentation and style standards (contact us <https://matrix.to/#/#scribe_community:matrix.org>_ if unsure).

Please ask first before embarking on any significant pull request (implementing features, refactoring code, etc), otherwise you risk spending a lot of time working on something that the developers might not want to merge into the project. With that being said, major additions are very appreciated!

When making a contribution, adhering to the GitHub flow <https://guides.github.com/introduction/flow/index.html>_ process is the best way to get your work merged:

1. If you cloned a while ago, get the latest changes from upstream:

.. code-block:: bash

   git checkout <dev-branch>
   git pull upstream <dev-branch>

2. Create a new topic branch (off the main project development branch) to contain your feature, change, or fix:

.. code-block:: bash

   git checkout -b <topic-branch-name>

3. Commit your changes in logical chunks, and please try to adhere to Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>_.

.. note::

   The following are tools and methods to help you write good commit messages:

   - commitlint <https://commitlint.io/>_ helps write Conventional Commits
   - Git's interactive rebase <https://docs.github.com/en/github/getting-started-with-github/about-git-rebase>_ cleans up commits

4. Locally merge (or rebase) the upstream development branch into your topic branch:

.. code-block:: bash

   git pull --rebase upstream <dev-branch>

5. Push your topic branch up to your fork:

.. code-block:: bash

   git push origin <topic-branch-name>

6. Open a Pull Request with a clear title and description.

Thank you in advance for your contributions!

Data edits
----------

.. note::

   Please see the Wikidata and Scribe Guide <https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md>_ for an overview of Wikidata <https://www.wikidata.org/>_ and how Scribe uses it.

Scribe does not accept direct edits to the grammar JSON files as they are sourced from Wikidata <https://www.wikidata.org/>_. Edits can be discussed and the Scribe-Data queries will be changed and run before an update. If there is a problem with one of the files, then the fix should be made on Wikidata and not on Scribe. Feel free to let us know that edits have been made by opening an issue <https://github.com/scribe-org/Scribe-Data/issues>_ and we'll be happy to integrate them!

Documentation
-------------

The documentation for Scribe-Data can be found at scribe-data.readthedocs.io <https://scribe-data.readthedocs.io/en/latest/>_. Documentation is an invaluable way to contribute to coding projects as it allows others to more easily understand the project structure and contribute. Issues related to documentation are marked with the documentation label <https://github.com/scribe-org/Scribe-Data/labels/documentation>_.

Function Docstrings
~~~~~~~~~~~~~~~~~~~

Scribe-Data generally follows numpydoc conventions <https://numpydoc.readthedocs.io/en/latest/format.html>_ for documenting functions and Python code in general. Function docstrings should have the following format:

.. code-block:: python

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

Building the Docs
~~~~~~~~~~~~~~~~~

Use the following commands to build the documentation locally:

.. code-block:: bash

   cd docs
   make html

You can then open ``index.html`` within ``docs/build/html`` to check the local version of the documentation.
