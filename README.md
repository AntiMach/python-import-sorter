# Import Sorter

## Overview

`import_sorter` is designed to automatically sort and format import statements of Python code.
It groups imports based on predefined or custom categories and ensures a clean,
structured order for better code readability and maintainability.

## Features

- Sorts `import` and `from ... import ...` statements by line length first, then alphabetically
- Groups imports according to predefined or custom groups
- Uses `ruff format` or a user-specified formatter to ensure proper formatting
- Modifies the target file in place

## Installation

Ensure you have Python installed (version 3.11 or higher recommended).

You may also want to install `ruff` for formatting:

```sh
pip install ruff
```

## Usage

Run the script with:

```sh
python -m import_sorter.main <file>
```

### Options

- `-g, --groups` : Define custom import groups (optional, multiple).
- `-f, --format` : Specify a formatter to use after sorting (optional).

Example:

```sh
python -m import_sorter.main my_script.py -g numpy pandas -f "ruff format -"
```

## How It Works

1. Parses the target Python file to extract import statements.
2. Categorizes imports into predefined (`__future__`, standard, third-party, etc.) or user-defined groups.
3. Sorts and formats the imports within each group.
4. Writes the modified content back to the file.

## Contributions

Feel free to contribute by submitting pull requests or reporting issues.
