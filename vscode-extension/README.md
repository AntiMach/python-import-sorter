# Python Import sorter

A python utilitly for sorting python imports the right way.

CLI Written in Python, extension written in TypeScript.

*[Repository](https://github.com/AntiMach/python-import-sorter)*

## Features

Format the whole document or selected sections of it.

Use builtin VSCode formatting options to format the document (Format Document, Format Selection, Editor Formatter, etc.)

## Requirements

To run this extension, you must have *Python 3.11* or higher and the *[Python Enviroments](https://github.com/AntiMach/python-import-sorter)* extension installed.

## Extension Settings

This extension provides the following configurations:

* `python-import-sorter.groups`: Specifies the imports to group by.
* `python-import-sorter.format`: Specifies the formatter command to run after sorting imports.
* `python-import-sorter.config`: Specifies the path to a config file.

## Known Issues

Unknown.

## Release Notes

### [1.0.0]

- Initial release
- Automatic import sorting for Python files
- Custom formatter command configuration through `python-import-sorter.format` (not set by default, eg.: `python -m ruff format -`)
- Configurable import grouping through `python-import-sorter.groups` setting
- Configurable arguments through the `python-import-sorter.config` setting