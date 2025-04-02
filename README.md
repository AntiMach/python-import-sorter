# Import Sorter

## Overview

`import_sorter.py` is a Python script designed to automatically sort and format import statements in Python files. It groups imports based on predefined or custom categories and ensures a clean, structured order for better code readability and maintainability.

## Features

- Sorts `import` and `from ... import ...` statements by line length first, then alphabetically
- Groups imports according to predefined or custom groups
- Uses `ruff format` or a user-specified formatter to ensure proper formatting
- Modifies the target file in place

## Installation

Ensure you have Python installed (version 3.7 or higher recommended).

You may also want to install `ruff` for formatting:

```sh
pip install ruff
```

## Usage

Run the script with:

```sh
python import_sorter.py <file>
```

### Options

- `-f, --formatter` : Specify a custom formatter (default is `ruff format`).
- `-g, --groups` : Define custom import groups.

Example:

```sh
python import_sorter.py my_script.py -f black -g numpy pandas
```

## How It Works

1. Parses the target Python file to extract import statements.
2. Categorizes imports into predefined (`__future__`, standard, third-party, etc.) or user-defined groups.
3. Sorts and formats the imports within each group.
4. Writes the modified content back to the file.

## Contributions

Feel free to contribute by submitting pull requests or reporting issues.
