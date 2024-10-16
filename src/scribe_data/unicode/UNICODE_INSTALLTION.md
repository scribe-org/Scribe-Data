# Scribe-Data Unicode Functionality Installation

The Scribe-Data Unicode process is powered by [cldr-json](https://github.com/unicode-org/cldr-json) data from the [Unicode Consortium](https://home.unicode.org/) and [PyICU](https://gitlab.pyicu.org/main/pyicu), a Python extension that wraps the Unicode Consortium's [International Components for Unicode (ICU)](https://github.com/unicode-org/icu) C++ project.

Please see the [installation guide for PyICU](https://gitlab.pyicu.org/main/pyicu#installing-pyicu) as the extension must be linked to ICU on your machine to work properly.

Note that some of the commands may be incorrect. On macOS you may need to do the following:

```bash
# Instead of:
export PATH="$(brew --prefix)/opt/icu4c/bin:$(brew --prefix)/opt/icu4c/sbin:$PATH"
export PKG_CONFIG_PATH="$PKG_CONFIG_PATH:$(brew --prefix)/opt/icu4c/lib/pkgconfig"

# Run:
echo "/opt/homebrew/opt/icu4c/bin:/opt/homebrew/opt/icu4c/sbin:$PATH"
echo "PKG_CONFIG_PATH=$PKG_CONFIG_PATH:/opt/homebrew/opt/icu4c/lib/pkgconfig"
```
