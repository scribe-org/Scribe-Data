Contributing to Scribe-Data
===========================

Thank you for your interest in contributing!

Please take a moment to review this document in order to make the contribution process easy and effective for everyone involved.

Following these guidelines helps to communicate that you respect the time of the developers managing and developing this open-source project. In return, and in accordance with this project's `code of conduct <https://github.com/scribe-org/Scribe-Data/blob/main/.github/CODE_OF_CONDUCT.md>`_, other contributors will reciprocate that respect in addressing your issue or assessing changes and features.

If you have questions or would like to communicate with the team, please `join us in our public Matrix chat rooms <https://matrix.to/#/#scribe_community:matrix.org>`_. We'd be happy to hear from you!

Contents
--------
.. contents::
   :local:
   :depth: 2

First steps as a contributor
----------------------------

Thank you for your interest in contributing to Scribe-Data! We look forward to welcoming you to the community and working with you to build tools for language learners to communicate effectively :) The following are some suggested steps for people interested in joining our community:

- Please join the `public Matrix chat <https://matrix.to/#/#scribe_community:matrix.org>`_ to connect with the community.

  - `Matrix <https://matrix.org/>`_ is a network for secure, decentralized communication.
  - Scribe would suggest that you use the `Element <https://element.io/>`_ client.
  - The `General <https://matrix.to/#/!yQJjLmluvlkWttNhKo:matrix.org?via=matrix.org>`_ and `Data <https://matrix.to/#/#ScribeData:matrix.org>`_ channels would be great places to start!
  - Feel free to introduce yourself and tell us what your interests are if you're comfortable :)

- Read through this contributing guide for all the information you need to contribute.
- Look into issues marked `good first issue <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aopen+is%3Aissue+label%3A%22good+first+issue%22>`_ and the `Projects board <https://github.com/orgs/scribe-org/projects/1>`_ to get a better understanding of what you can work on.
- Check out our `public designs on Figma <https://www.figma.com/file/c8945w2iyoPYVhsqW7vRn6/scribe_public_designs?type=design&node-id=405-464&mode=design&t=E3ccS9Z8MDVSizQ4-0>`_ to understand Scribes's goals and direction.
- Consider joining our `bi-weekly developer sync <https://etherpad.wikimedia.org/p/scribe-dev-sync>`_!

  .. note::
     Those new to Python or wanting to work on their Python skills are more than welcome to contribute! The team would be happy to help you on your development journey.

Learning the tech stack
-----------------------

Scribe is very open to contributions from people in the early stages of their coding journey! The following is a select list of documentation pages to help you understand the technologies we use.

Docs for those new to programming:

- `Mozilla Developer Network Learning Area <https://developer.mozilla.org/en-US/docs/Learn>`_:

  - Doing MDN sections for HTML, CSS, and JavaScript is the best way to get into web development!

Python learning docs:

- `Python getting started guide <https://docs.python.org/3/tutorial/introduction.html>`_
- `Python getting started resources <https://www.python.org/about/gettingstarted/>`_

Development environment
-----------------------

The development environment for Scribe-Data can be installed via the following steps:

1. `Fork <https://docs.github.com/en/get-started/quickstart/fork-a-repo>`_ the `Scribe-Data repo <https://github.com/scribe-org/Scribe-Data>`_, clone your fork, and configure the remotes.

   .. note::
      Consider using SSH. Alternatively to using HTTPS as in the instructions below, consider SSH to interact with GitHub from the terminal. SSH allows you to connect without a user-pass authentication flow. To run git commands with SSH, remember then to substitute the HTTPS URL, ``https://github.com/...``, with the SSH one, ``git@github.com:...``. GitHub also has their documentation on how to `Generate a new SSH key <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent>`_.

      .. code-block:: bash

         # Clone your fork of the repo into the current directory in the terminal.
         git clone https://github.com/<your-username>/Scribe-Data.git
         # Navigate to the newly cloned directory.
         cd Scribe-Data
         # Assign the original repo to a remote called "upstream".
         git remote add upstream https://github.com/scribe-org/Scribe-Data.git

- Now, if you run ``git remote -v``, you should see two remote repositories named:
  
  - ``origin`` (your fork of the repository)
  - ``upstream`` (the original Scribe-Data repository)

2. Use `Python venv <https://docs.python.org/3/library/venv.html>`_ to create a local development environment within your Scribe-Data directory.

   .. code-block:: bash

      python3 -m venv venv  # Create a virtual environment named venv.
      source venv/bin/activate  # Activate the virtual environment.
      pip install --upgrade pip  # Upgrade pip to the latest version.
      pip install -r requirements.txt  # Install dependencies from the requirements.txt file.

   .. note::
      If you encounter any issues setting up your development environment, feel free to reach out to the team in the `Data room on Matrix <https://matrix.to/#/#ScribeData:matrix.org>`_ for assistance.

Issues and projects
-------------------

The `issue tracker for Scribe-Data <https://github.com/scribe-org/Scribe-Data/issues>`_ is the preferred channel for :ref:`bug reports`, :ref:`features requests`, and :ref:`submitting pull requests`. Scribe also organizes related issues into `projects <https://github.com/scribe-org/Scribe-Data/projects>`_.

.. note::
   Just because an issue is assigned on GitHub doesn't mean that the team isn't interested in your contribution! Feel free to comment on the issue, and we can potentially reassign it to you.

Be sure to check the `-next release- <https://github.com/scribe-org/Scribe-Data/labels/-next%20release->`_ and `-priority- <https://github.com/scribe-org/Scribe-Data/labels/-priority->`_ labels in the issues for those that are most important, as well as those marked `good first issue <https://github.com/scribe-org/Scribe-Data/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22>`_ that are tailored for first-time contributors.

Bug reports
-----------

A bug is a *demonstrable problem* that is caused by the code in the repository. Good bug reports are extremely helpful - thank you!

Guidelines for bug reports:

1. **Use the GitHub issue search** - Check if the issue has already been reported.
2. **Check if the issue has been fixed** - Try to reproduce it using the latest `main` branch or development branch in the repository.
3. **Isolate the problem** - Make sure that the code in the repository is *definitely* responsible for the issue.

**Great Bug Reports** tend to have:

- A quick summary.
- Steps to reproduce.
- What you expected would happen.
- What actually happens.
- Notes (why this might be happening, things tried that didn't work, etc).

Report bugs using the `bug report template <https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=bug&template=bug_report.yml>`_, which helps in providing all necessary information.

Feature requests
----------------

Feature requests are more than welcome! Before making a suggestion, please ensure it fits the scope and aims of the project. Provide as much detail and context as possible, and clarify how you'd like to contribute to its development.

Use the `feature request template <https://github.com/scribe-org/Scribe-Data/issues/new?assignees=&labels=feature&template=feature_request.yml>`_ to submit your ideas. These are marked with the `feature` label for easy identification.

Pull requests
-------------

Good pull requests—patches, improvements, and new features—are crucial for the community and help make Scribe-Data better. They should remain focused in scope and avoid containing unrelated commits.

**Please ask first** by opening an issue to discuss significant changes. This way, you avoid spending time on something that the maintainers might not want to merge into the project.

Adhere to the `GitHub flow <https://guides.github.com/introduction/flow/index.html>`_ for the best chance of getting your work merged:

1. Get the latest changes from `upstream` if you've cloned a while ago.
2. Create a new topic branch to contain your feature, change, or fix.
3. Commit your changes in logical chunks. Use `Conventional Commits <https://www.conventionalcommits.org/en/v1.0.0/>`_ for commit messages.
4. Locally merge (or rebase) the upstream development branch into your topic branch.
5. Push your topic branch up to your fork.
6. Open a Pull Request with a clear title and description via the GitHub website.

Data edits
----------

Scribe relies on data from `Wikidata <https://www.wikidata.org/>`, and thus direct edits to the data files in the repository are not accepted. If you find an issue with the data, please make the correction directly in Wikidata. You can then open an issue to notify the Scribe-Data team, and we'll update our data accordingly.

Documentation
-------------

Documentation is crucial for understanding and contributing to the project. The Scribe-Data documentation is available at `scribe-data.readthedocs.io <https://scribe-data.readthedocs.io/en/latest/>`_. Contributions to improve documentation are highly encouraged.

To build the documentation locally, use the following commands:

.. code-block:: bash

   cd docs
   make html

This will generate HTML files in `docs/build/html`. Open `index.html` to view the documentation locally.
