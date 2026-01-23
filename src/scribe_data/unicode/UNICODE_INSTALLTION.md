# Scribe-Data Unicode Functionality Installation

The Scribe-Data Unicode process is powered by [cldr-json](https://github.com/unicode-org/cldr-json) data from the [Unicode Consortium](https://home.unicode.org/) and [PyICU](https://gitlab.pyicu.org/main/pyicu), a Python extension that wraps the Unicode Consortium's [International Components for Unicode (ICU)](https://github.com/unicode-org/icu) C++ project.

Please see the [installation guide for PyICU](https://gitlab.pyicu.org/main/pyicu) as the extension must be linked to ICU on your machine to work properly.

## macOS Support

Note that some of the commands in the installation guide may be incorrect. On macOS you may need to do the following:

```bash
# Instead of:
export PATH="$(brew --prefix)/opt/icu4c/bin:$(brew --prefix)/opt/icu4c/sbin:$PATH"
export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:$(brew --prefix)/opt/icu4c/lib/pkgconfig"

# Run:
echo "/opt/homebrew/opt/icu4c/bin:/opt/homebrew/opt/icu4c/sbin:$PATH"
echo "PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/homebrew/opt/icu4c/lib/pkgconfig"
```

## Windows Support

This guide provides step-by-step instructions on how to install the PyICU library, which is essential for proper emoji support on Windows.

### Download the PyICU Wheel File

1. Visit the [PyICU Release Page](https://github.com/cgohlke/pyicu-build/releases).
2. Locate and download the wheel (`.whl`) file that matches your Python version. Make sure to select the correct architecture (e.g., `win_amd64` for 64-bit Python).

### Set Up a Virtual Environment

If you haven't already, You can do this with the following command:

> [!NOTE]
> First, install `uv` if you don't already have it by following the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

```bash
uv sync --all-extras  # create .venv and install all dependencies from uv.lock

# Unix or macOS:
source .venv/bin/activate

# Windows:
.venv\Scripts\activate.bat  # .venv\Scripts\activate.ps1 (PowerShell)
```

### Install PyICU

```bash
# Replace 'PyICU-2.13-cp312-cp312-win_amd64.whl' with the actual filename you downloaded.
uv pip install PyICU-2.13-cp312-cp312-win_amd64.whl

# Check the installation details of PyICU.
uv pip show PyICU
```
