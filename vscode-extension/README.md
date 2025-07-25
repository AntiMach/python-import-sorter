# Python Import sorter

A python utilitly for sorting python imports the right way.

CLI Written in Python, extension written in TypeScript.

*[Repository](https://github.com/AntiMach/python-import-sorter)*

## Features

Format the whole document or selected sections of it.

Use builtin VSCode formatting options to format the document (Format Document, Format Selection, Editor Formatter, etc.)

## Requirements

To run this extension, you must have *Python 3.11* or higher and the *[Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python)* extension installed.

## Extension Settings

This extension provides the following configurations:

* `python-import-sorter.groups`: Specifies the imports to group by.
* `python-import-sorter.format`: Specifies the formatter command to run after sorting imports.
* `python-import-sorter.config`: Specifies the path to a config file.
* `python-import-sorter.exclude`: Specifies the files/directories/globs to ignore when formatting multiple files.

## Configuration Priority

Configuration can be provided in several ways. The priority is as follows (highest to lowest):

1. Arguments from the file specified with `python-import-sorter.config`
2. `import-sorter.toml` at the current project's root.
3. `[tool.import-sorter]` section of `pyproject.toml` at the project's root.

## Known Issues

- Formats with comments around them (except after all top level imports) get completely removed.

## Release Notes

### [1.1.3]
- Fixed empty files causing the formatter to hang

### [1.1.2]
- Updated the bundled version of import-sorter

### [1.1.1]
- Fixed the file being completely emptied after failing to format
- Removed the notification from a single file format

### [1.1.0]
- Added a way to format every python file in a workspace
- Added a the `python-import-sorter.exclude` setting
- Added the need to have the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension
- Removed the need to have [Python Environments](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs) extension

### [1.0.0]

- Initial release
- Automatic import sorting for Python files
- Custom formatter command configuration through `python-import-sorter.format` (not set by default, eg.: `ruff format -`)
- Configurable import grouping through `python-import-sorter.groups` setting
- Configurable arguments through the `python-import-sorter.config` setting