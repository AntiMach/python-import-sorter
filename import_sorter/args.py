import sys
import tomllib
from pathlib import Path
from dataclasses import dataclass
from pathspec import GitIgnoreSpec
from argparse import ArgumentParser
from typing import Iterator, Self, Sequence


@dataclass
class Source:
    content: str


@dataclass(kw_only=True)
class Args:
    files: list[str]
    exclude: list[str]
    groups: list[str]
    format: str | None
    config: str | None
    json: bool

    def __post_init__(self):
        if self.config:
            self._load_toml(self.config, [])

        self._load_toml("import-sorter.toml", [])
        self._load_toml("pyproject.toml", ["tool", "import-sorter"])

    def _load_toml(self, file: str, path: list[str]):
        try:
            fp = open(file, "rb")
        except FileNotFoundError:
            return

        with fp:
            config = tomllib.load(fp)

        for key in path:
            config = config.get(key, {})

        self.exclude.extend(config.get("exclude", []))
        self.groups = self.groups or config.get("groups", [])
        self.format = self.format or config.get("format")
        self.json = self.json or config.get("json", False)

    @classmethod
    def parse(cls, args: Sequence[str] | None = None) -> Self:
        exec_file = Path(sys.argv[0])

        if exec_file.stem == "__main__":
            prog = f"python -m {exec_file.parent.stem}"
        else:
            prog = exec_file.name

        parser = ArgumentParser(prog)
        parser.add_argument("files", action="extend", nargs="+", default=[])
        parser.add_argument("-x", "--exclude", action="extend", nargs="*", default=[])
        parser.add_argument("-g", "--groups", action="extend", nargs="*", default=[])
        parser.add_argument("-f", "--format", default=None)
        parser.add_argument("-c", "--config", default=None)
        parser.add_argument("-j", "--json", action="store_true", default=False)

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
