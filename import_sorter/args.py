import sys
import tomllib
from pathlib import Path
from typing import Self, Sequence
from dataclasses import dataclass
from argparse import ArgumentParser


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

        if not self.groups:
            self.groups = config.get("groups", [])

        if not self.format:
            self.format = config.get("format")

    @classmethod
    def parse(cls, args: Sequence[str] | None = None) -> Self:
        exec_file = Path(sys.argv[0])

        if exec_file.stem == "__main__":
            prog = f"python -m {exec_file.parent.stem}"
        else:
            prog = exec_file.name

        parser = ArgumentParser(prog)
        parser.add_argument("files", action="extend", nargs="+", default=[])
        parser.add_argument("-x", "--exclude", action="extend", nargs="+", default=[])
        parser.add_argument("-g", "--groups", action="extend", nargs="+", default=[])
        parser.add_argument("-f", "--format", default=None)
        parser.add_argument("-c", "--config", default=None)

        return cls(**parser.parse_args(args).__dict__)
    
    def list_files(self):
        excludes = {match for exclude in self.exclude for match in Path().glob(exclude)}

        for file in self.files:
            if file == "-":
                yield "-"
                continue

            for match in Path().glob(file):
                if match not in excludes:
                    yield match

