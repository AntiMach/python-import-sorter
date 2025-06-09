# Python Import Sorter

## Overview

`python-import-sorter` is designed to automatically sort and format import statements of Python code.
It groups imports based on predefined or custom categories and ensures a clean, structured order for better code readability and maintainability.

## Features

- Sorts `import` and `from ... import ...` statements by line length first, then alphabetically  
- Groups imports based on predefined or custom categories  
- Supports post-sorting formatting using external tools  
- Works in-place or with standard input/output (`stdin`/`stdout`)


## Installation

Ensure you have Python 3.11+ installed.

You may also want to install a formatter like `ruff` for formatting:

```sh
pip install ruff
```

To install `python-import-sorter` directly from the repository:

```sh
pip install git+https://github.com/AntiMach/python-import-sorter
```

## Usage

Run the tool via Python:

```sh
python -m import_sorter <file>
```

Or, if installed via `pip`, use the CLI directly:

```sh
import-sorter <file>
```

### Options

- `-g, --groups` : Define custom import groups (can be used multiple times)
- `-f, --format` : Specify a formatter to run after sorting (optional)
- `-c, --config` : Path to a config file with predefined arguments

Example:

```sh
import-sorter my_script.py -g numpy pandas -f "ruff format -"
```

### Configuration Priority

Arguments can be provided in several ways. The priority is as follows (highest to lowest):

1. Command-line arguments (`--groups`, `--format`, etc.)
2. Arguments from the file specified with `--config`
3. `import-sorter.toml` in the current working directory.
4. `[tool.import-sorter]` section of `pyproject.toml` at the current working directory.

## Contributions

Feel free to contribute by submitting pull requests or reporting issues.



