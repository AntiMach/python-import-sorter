import sys
import glob
import tomllib
from pathlib import Path
from dataclasses import dataclass
from argparse import ArgumentParser
from typing import Self, TextIO, Literal, Sequence


@dataclass
class Args:
    file: str
    groups: list[str]
    format: str | None
    config: str | None
    recursive: bool = False

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

        parser.add_argument("file")
        parser.add_argument("-g", "--groups", action="extend", nargs="+", default=[])
        parser.add_argument("-f", "--format", default=None)
        parser.add_argument("-c", "--config", default=None)
        parser.add_argument(
            "-r", "--recursive", action="store_true", help="Format all Python files in directory recursively"
        )

        return cls(**parser.parse_args(args).__dict__)

    def open_file(self, mode: Literal["r", "w"]) -> TextIO:
        if self.file != "-":
            return open(self.file, mode, encoding="utf-8")

        return sys.stdin if mode == "r" else sys.stdout

    def get_python_files(self) -> list[str]:
        if self.file == "-":
            return ["-"]

        file_path = Path(self.file)

        if file_path.is_file():
            return [str(file_path)]
        elif file_path.is_dir():
            if self.recursive:
                return [str(p) for p in file_path.rglob("*.py")]
            else:
                return [str(p) for p in file_path.glob("*.py")]
        else:
            matches = glob.glob(self.file, recursive=self.recursive)
            python_files = [f for f in matches if f.endswith(".py")]
            return python_files or [self.file]
