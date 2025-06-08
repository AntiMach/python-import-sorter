import os
import sys
import subprocess
from pathlib import Path
from typing import Literal

from import_sorter.args import Args
from import_sorter.sorting import ImportSorter


def run_program(source: str, args: list[str]):
    if args[0].casefold() in ("python", "python3", "python3.11"):
        args[0] = sys.executable

    result = subprocess.run(args, env=os.environ, input=source, text=True, capture_output=True)

    if result.returncode:
        raise RuntimeError(result.stderr)

    return result.stdout


def open_file(file: Path | Literal["-"], mode: Literal["r", "w"]):
    if file == "-":
        return sys.stdin if mode == "r" else sys.stdout
    
    return file.open(mode, encoding="utf-8")


def main():
    args = Args.parse()

    for file in args.list_files():
        with open_file(file, "r") as fp:
            source = fp.read()

        source = ImportSorter(source, args.groups).sort()

        if args.format:
            source = run_program(source, args.format.split())

        with open_file(file, "w") as fp:
            fp.write(source)


if __name__ == "__main__":
    main()
