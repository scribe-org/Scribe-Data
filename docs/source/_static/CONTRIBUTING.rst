Contributing to Scribe-Data
===========================

Thank you for your interest in contributing!

Please take a moment to review this document to make the contribution process is easy and effective for everyone involved.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open-source project. In return, and accordance with this project's `code of conduct <https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md>`__, other contributors will reciprocate that respect in addressing your issue or assessing changes and features.

If you have questions or would like to communicate with the team, please `join us in our public Matrix chat
rooms <https://matrix.to/#/#scribe_community:matrix.org>`__. We'd be happy to hear from you!

Contents
--------

-  `First steps as a contributor <#first-steps-as-a-contributor>`__
-  `Learning the tech stack <#learning-the-tech-stack>`__
-  `Development environment <#development-environment>`__
-  `Issues and projects <#issues-and-projects>`__
-  `Bug reports <#bug-reports>`__
-  `Feature requests <#feature-requests>`__
-  `Pull requests <#pull-requests>`__
-  `Data edits <#data-edits>`__
-  `Documentation <#documentation>`__

First steps as a contributor
----------------------------

Thank you for your interest in contributing to Scribe-Data! We look
forward to welcoming you to the community and working with you to build
a tool for language learners to communicate effectively. :) The
following are some suggested steps for people interested in joining our
community:

-  Please join the `public Matrix chat <https://matrix.to/#/#scribe_community:matrix.org>`__ to connect with the community

    -  `Matrix <https://matrix.org/>`__ is a network for secure, decentralized communication
    -  Scribe would suggest that you use the `Element <https://element.io/>`__ client
    -  The `General <https://matrix.to/#/!yQJjLmluvlkWttNhKo:matrix.org?via=matrix.org>`__ and `Data <https://matrix.to/#/#ScribeData:matrix.org>`__ channels would be great places to start!
    -  Feel free to introduce yourself and tell us what your interests are if you're comfortable :)

-  Read through this contributing guide for all the information you need to contribute
-  Look into issues marked `good first issue <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>`__ and the `Projects board <https://github.com/orgs/scribe-org/projects/1>`__ to get a a better understanding of what you can work on
-  Check out our `public designs on Figma <https://www.figma.com/file/c8945w2iyoPYVhsqW7vRn6/scribe_public_designs?type=design&node-id=405-464&mode=design&t=E3ccS9Z8MDVSizQ4-0>`__ to understand Scribes' goals and direction
-  Consider joining our `bi-weekly developer sync <https://etherpad.wikimedia.org/p/scribe-dev-sync>`__!

..

    | **Note**
    | Those new to Python or wanting to work on their Python skills are more than welcome to contribute! The team would be happy to help you on your development journey :)

Learning the tech stack
-----------------------

Scribe is very open to contributions from people in the early stages of their coding journey! The following is a select list of documentation pages to help you understand the technologies we use.

.. raw:: html

    <details><summary>Docs for those new to programming</summary><p>

-  `Mozilla Developer Network Learning Area <https://developer.mozilla.org/en-US/docs/Learn>`__

    -  Doing MDN sections for HTML, CSS, and JavaScript is the best ways to get into web development!

.. raw:: html

    </p></details>

.. raw:: html

    <details><summary>Python learning docs</summary><p>

-  `Python getting started guide <https://docs.python.org/3/tutorial/introduction.html>`__
-  `Python getting started resources <https://www.python.org/about/gettingstarted/>`__

.. raw:: html

    </p></details><br/>

Development environment
-----------------------

The development environment for Scribe-Data can be installed via the following steps:

- `Fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`__ the `Scribe-Data repo <https://github.com/scribe-org/Scribe-Data>`__, clone your fork, and configure the remotes:

..

.. raw:: html

    <details><summary>Note: Consider using SSH</summary><p>

Alternatively, to use HTTPS as in the instructions below, consider SSH to interact with GitHub from the terminal. SSH allows you to connect without a user-pass authentication flow.

To run git commands with SSH, remember then to substitute the HTTPS URL, ``https://github.com/...``, with the SSH one, ``git@github.com:...``.

-  e.g. Cloning now becomes ``git clone git@github.com:<your-username>/Scribe-Data.git``

GitHub also has documentation on how to `Generate a new SSH key <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent>`__ 🔑

.. raw:: html

    </p></details><br/>

..

.. code:: bash

    # Clone your fork of the repo into the current directory.
    git clone https://github.com/<your-username>/Scribe-Data.git
    # Navigate to the newly cloned directory.
    cd Scribe-Data
    # Assign the original repo to a remote called "upstream".
    git remote add upstream https://github.com/scribe-org/Scibe-Data.git

..

- Now, if you run ``git remote -v`` you should see two remote repositories named:

    -  ``origin`` (forked repository)
    -  ``upstream`` (Scribe-Data repository)

..

- Use `Python venv <https://docs.python.org/3/library/venv.html>`__ to create the local development environment within your Scribe-Data directory:

.. code:: bash

    python3 -m venv venv  # make an environment venv
    pip install --upgrade pip  # make sure that pip is at the latest version
    pip install -r requirements-dev.txt  # install development dependencies
    pip install -e .  # install the local version of Scribe-Data

..

    | **Note**
    | Feel free to contact the team in the `Data room on Matrix <https://matrix.to/#/#ScribeData:matrix.org>`__ if you're having problems getting your environment set up!

Issues and projects
-------------------

The `issue tracker for Scribe-Data <https://github.com/scribe-org/Scribe-Data/issues>`__ is the
preferred channel for `bug reports <#bug-reports>`__, `features requests <#feature-requests>`__ and `submitting pull
requests <#pull-requests>`__. Scribe also organizes related issues into `projects <https://github.com/scribe-org/Scribe-Data/projects>`__.

..

    | **Note**
    | Just because an issue is assigned on GitHub doesn't mean that the team isn't interested in your contribution! Feel free to write `in the issues <https://github.com/scribe-org/Scribe-Data/issues>`__ and we can potentially reassign it to you.

Be sure to check the `-next release- <https://github.com/scribe-org/Scribe-Data/labels/-next%20release->`__
and `-priority- <https://github.com/scribe-org/Scribe-Data/labels/-priority->`__
labels in the `issues <https://github.com/scribe-org/Scribe-Data/issues>`__ for those
that are most important, as well as those marked `good first issue <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`__ that are tailored for first-time contributors.

Bug reports
-----------

A bug is a *demonstrable problem* that is caused by the code in the repository. Good bug reports are extremely helpful - thank you!

Guidelines for bug reports:

1. **Use the GitHub issue search** to check if the issue has already been reported.

2. **Check if the issue has been fixed** by trying to reproduce it using the latest ``main`` or development branch in the repository.

3. **Isolate the problem** to make sure that the code in the repository is *definitely* responsible for the issue.

**Great Bug Reports** tend to have:

-  A quick summary
-  Steps to reproduce
-  What you expected would happen
-  What actually happens
-  Notes (why this might be happening, things tried that didn't work, etc)

To make the above steps easier, the Scribe team asks that contributors report bugs using the `bug report
template <https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=bug_report.yml>`__, with these issues further being marked with the `bug <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3Abug>`__ label.

Again, thank you for your time in reporting issues!

Feature requests
----------------

Feature requests are more than welcome! Please take a moment to find out whether your idea fits with the scope and aims of the project. When making a suggestion, provide as much detail and context as possible, and further, make clear the degree to which you would like to contribute in its development. Feature requests are marked with the
`feature <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3Afeature>`__ label, and can be made using the `feature request <https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=feature_request.yml>`__ template.

Pull requests
-------------

Good pull requests - patches, improvements and new features - are the foundation of our community making Scribe-Data. They should remain focused in scope and avoid containing unrelated commits. Note that all contributions to this project will be made under `the specified license <https://github.com/scribe-org/Scribe-Data/blob/main/LICENSE.txt>`__ and should follow the coding indentation and style standards (`contact us <https://matrix.to/#/#scribe_community:matrix.org>`__ if unsure).

**Please ask first** before embarking on any significant pull request (implementing features, refactoring code, etc), otherwise, you risk spending a lot of time working on something that the developers might not want to merge into the project. With that being said, major additions are very appreciated!

When making a contribution, adhering to the `GitHub flow <https://guides.github.com/introduction/flow/index.html>`__ process is the best way to get your work merged:

1. If you cloned a while ago, get the latest changes from upstream:

.. code:: bash

    git checkout <dev-branch>
    git pull upstream <dev-branch>

2. Create a new topic branch (off the main project development branch) to contain your feature, change, or fix:

.. code:: bash

    git checkout -b <topic-branch-name>

3. Commit your changes in logical chunks, and please try to adhere to `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`__.

..

    | **Note**
    | The following are tools and methods to help you write good commit messages ✨
    | •  `commitlint <https://commitlint.io/>`__ helps write `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`__
    | •  Git's `interactive rebase <https://docs.github.com/en/github/getting-started-with-github/about-git-rebase>`__ cleans up commits

4. Locally merge (or rebase) the upstream development branch into your topic branch:

.. code:: bash

    git pull --rebase upstream <dev-branch>

5. Push your topic branch up to your fork:

.. code:: bash

    git push origin <topic-branch-name>

6. `Open a Pull Request <https://help.github.com/articles/using-pull-requests/>`__ with a clear title and description.

Thank you in advance for your contributions!

Data edits
----------

..

    | **Note**
    | Please see the `Wikidata and Scribe Guide <https://github.com/scribe-org/Organization/blob/main/WIKIDATAGUIDE.md>`__ for an overview of `Wikidata <https://www.wikidata.org/>`__ and how Scribe uses it.

Scribe does not accept direct edits to the grammar JSON files as they are sourced from `Wikidata <https://www.wikidata.org/>`__. Edits can be discussed and the `Scribe-Data <https://github.com/scribe-org/Scribe-Data>`__ queries will be changed and run before an update. If there is a problem with one of the files, then the fix should be made on `Wikidata <https://www.wikidata.org/>`__ and not on Scribe. Feel free to let us know that edits have been made by `opening an issue <https://github.com/scribe-org/Scribe-Data/issues>`__ and we’ll be happy to integrate them!

Documentation
-------------

The documentation for Scribe-Data can be found at `scribe-data.readthedocs.io <https://scribe-data.readthedocs.io/en/latest/>`__. Documentation is an invaluable way to contribute to coding projects as it allows others to more easily understand the project structure and contribute. Issues related to documentation are marked with the `documentation <https://github.com/scribe-org/Scribe-Data/labels/documentation>`__ label.

Use the following commands to build the documentation locally:

.. code:: bash

    cd docs
    make html

You can then open ``index.html`` within ``docs/build/html`` to check the
local version of the documentation.
