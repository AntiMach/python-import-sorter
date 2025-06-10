# Change Log

All notable changes to the "Python Import Sorter" extension will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.1] - 2025-06-10

### Fixed
- The file being completely emptied after failing to format

### Removed
- The notification from a single file format

## [1.1.0] - 2025-06-09

### Added
- A way to format every python file in a workspace
- The `python-import-sorter.exclude` setting
- The need to have the [Python](https://marketplace.visualstudio.com/items?itemName=ms-python.python) extension

### Removed
- The need to have [Python Environments](https://marketplace.visualstudio.com/items?itemName=ms-python.vscode-python-envs) extension

## [1.0.0] - 2025-04-07

### Added
- Initial release
- Automatic import sorting for Python files
- Custom formatter command configuration through `python-import-sorter.format` (not set by default, eg.: `python -m ruff format -`)
- Configurable import grouping through `python-import-sorter.groups` setting
- Configurable arguments through the `python-import-sorter.config` setting
