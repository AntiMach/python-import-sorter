import sys
from dataclasses import dataclass
from argparse import ArgumentParser
import tomllib
from typing import Literal, Self, Sequence, TextIO


@dataclass
class Args:
    file: str
    groups: list[str]
    format: str | None
    config: str | None

    def __post_init__(self):
        self._load_toml("pyproject.toml", ["tool", "import-sorter"])
        self._load_toml("import-sorter.toml", [])

        if self.config:
            self._load_toml(self.config, [])

    def _load_toml(self, file: str, path: list[str]):
        try:
            fp = open(file, "rb")
        except FileNotFoundError:
            return

        with fp:
            config = tomllib.load(fp)

        for key in path:
            config = config.get(key, {})

        self.groups = config.get("groups", self.groups)
        self.format = config.get("format", self.format)

    @classmethod
    def parse(cls, args: Sequence[str] | None = None) -> Self:
        parser = ArgumentParser()

        parser.add_argument("file")
        parser.add_argument("-g", "--groups", action="extend", nargs="+", default=[])
        parser.add_argument("-f", "--format", default=None)
        parser.add_argument("-c", "--config", default=None)

        return cls(**parser.parse_args(args).__dict__)

    def open_file(self, mode: Literal["r", "w"]) -> TextIO:
        if self.file != "-":
            return open(self.file, mode, encoding="utf-8")

        if mode == "r":
            return sys.stdin

        return sys.stdout
