# Python Import Sorter

Automatically sort Python imports in your VSCode environment.

## Features

-   Automatically sorts Python imports on file save
-   Uses customizable formatter commands (defaults to `ruff format`)
-   Configurable import grouping
-   Activates only for Python files

## Requirements

-   VS Code 1.98.0 or higher
-   Python environment with your preferred formatter installed

## Installation

1. Open VS Code
2. Press `Ctrl+P` (or `Cmd+P` on macOS)
3. Type `ext install antimach.python-import-sorter`
4. Press Enter

## Extension Settings

This extension contributes the following settings:

-   `python-import-sorter.formatter`: Specify the formatter command to run (default: `ruff format`)
-   `python-import-sorter.groups`: Package names to group imports by (array of strings)

## Configuration Examples

In your `settings.json`:

```json
{
    "python-import-sorter.formatter": "ruff format",
    "python-import-sorter.groups": ["stdlib", "django", "third-party", "first-party", "local"]
}
```

## Usage

The extension activates automatically for Python files. Your imports will be sorted whenever you save a Python file.

## Known Issues

Please report any issues on the [GitHub repository](https://github.com/AntiMach/python-import-sorter/issues).

## Release Notes

### 0.0.1

-   Initial release
-   Basic import sorting functionality
-   Custom formatter support
-   Configurable import grouping
