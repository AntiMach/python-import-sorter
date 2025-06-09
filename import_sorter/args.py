import sys
import shlex
import tomllib
from pathlib import Path
from dataclasses import dataclass
from pathspec import GitIgnoreSpec
from argparse import ArgumentParser
from typing import Self, Iterator, Sequence


@dataclass
class Source:
    content: str


@dataclass(kw_only=True)
class Args:
    files: list[str]
    exclude: list[str]
    groups: list[str]
    format: list[str]
    config: str | None
    no_config: bool
    as_json: bool
    quiet: bool

    def __post_init__(self):
        if self.config:
            self._load_toml(self.config, [])

        if not self.no_config:
            self._load_toml("import-sorter.toml", [])
            self._load_toml("pyproject.toml", ["tool", "import-sorter"])

        self.format = shlex.split(self.format[0]) if len(self.format) == 1 else self.format

    def _config_list(self, value: list[str] | str | None) -> list[str]:
        if isinstance(value, str):
            return shlex.split(value)
        elif isinstance(value, list):
            return value
        return []

    def _load_toml(self, file: str, path: list[str]):
        try:
            fp = open(file, "rb")
        except FileNotFoundError:
            return

        with fp:
            config = tomllib.load(fp)

        for key in path:
            config = config.get(key, {})

        self.exclude.extend(self._config_list(config.get("exclude")))
        self.groups = self.groups or self._config_list(config.get("groups"))
        self.format = self.format or self._config_list(config.get("format"))

    @classmethod
    def parse(cls, args: Sequence[str] | None = None) -> Self:
        exec_file = Path(sys.argv[0])

        if exec_file.stem == "__main__":
            prog = f"python -m {exec_file.parent.stem}"
        else:
            prog = exec_file.name

        parser = ArgumentParser(prog)
        parser.add_argument(
            "files",
            action="extend",
            nargs="+",
            default=[],
            help=(
                "List of files, folders or globs to format. "
                "Specifying folders formats every file recursively, "
                "write '<folder>/*.py' if you're not looking for that. "
                "If '-' is specified, then the program reads from stdin until closed, "
                "and writes to stdout the formatted contents. "
                "Files with syntax errors are not formatted. "
                "Cannot be specified in config."
            ),
        )
        parser.add_argument(
            "-x",
            "--exclude",
            action="extend",
            nargs="+",
            default=[],
            help=(
                ".gitignore like list of exclusions for multiple files. "
                "Negative exclusions (!) only work for specified files. "
                "eg.: '.venv' ignores every file inside .venv folders. "
                "Can be specified in config, as a string or list of strings."
            ),
        )
        parser.add_argument(
            "-g",
            "--groups",
            action="extend",
            nargs="+",
            default=[],
            required=False,
            help=(
                "Import group order for specific packages. eg.: '-g tomllib argparse' "
                "group order: __future__ -> other imports -> tomllib imports -> argparse imports. "
                "Can be specified in config, as a string or list of strings."
            ),
        )
        parser.add_argument(
            "-f",
            "--format",
            action="extend",
            nargs="+",
            default=[],
            required=False,
            help=(
                "Format command arguments. "
                "If the command starts with 'python', use the current executable. "
                "The format should accept a stdio stream. eg.: '-f ruff format -'. "
                "Can be specified in config, as a string or list of strings."
            ),
        )
        parser.add_argument(
            "-c",
            "--config",
            default=None,
            help=(
                "Config toml file to load arguments from. eg.: '-c import-sorter-args.toml' "
                "Cannot be specified in config."
            ),
        )
        parser.add_argument(
            "-n",
            "--no-config",
            action="store_true",
            default=False,
            help=(
                "Disables the default behaviour of loading from specific configs. "
                "By default, the program always tries to read from the current directory's specified config file at "
                "root, then from `pyproject.toml` at [tool.import-sorter], then from `import-sorter.toml` at root. "
                "If this argument is passed, only the specified config file will be used (if specified). "
                "Cannot be specified in config."
            ),
        )
        print_group = parser.add_mutually_exclusive_group()
        print_group.add_argument(
            "-j",
            "--as-json",
            action="store_true",
            default=False,
            help="Print status as json strings separated by newlines. Cannot be specified from config.",
        )
        print_group.add_argument(
            "-q",
            "--quiet",
            action="store_true",
            default=False,
            help="Don't print any status. Cannot be specified from config",
        )

        return cls(**parser.parse_args(args).__dict__)

    def list_files(self) -> Iterator[str]:
        exclude_spec = GitIgnoreSpec.from_lines(self.exclude)

        for f in self._iterate_files(self.files):
            if not exclude_spec.match_file(f):
                yield f

    def _iterate_files(self, files: list[str]):
        for file in files:
            if file == "-":
                yield file
                continue

            path = Path(file)

            if path.is_file() and path.suffix == ".py":
                yield str(path.resolve())
                continue

            for subpath in path.glob("**/*.py") if path.is_dir() else Path().glob(file):
                if subpath.suffix == ".py":
                    yield str(subpath.resolve())
