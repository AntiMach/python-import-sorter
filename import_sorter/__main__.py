import os
import sys
import subprocess
import traceback
from typing import Literal

from import_sorter.args import Args
from import_sorter.sorting import ImportSorter
from import_sorter.states import DoneState, ErrorState, FileState, InitState


def run_program(source: str, args: list[str]):
    if args[0].casefold() in ("python", "python3", "python3.11"):
        args[0] = sys.executable

    result = subprocess.run(args, env=os.environ, input=source, text=True, capture_output=True, encoding="utf-8")

    if result.returncode:
        raise RuntimeError(result.stderr)

    return result.stdout


def open_file(file: str, mode: Literal["r", "w"]):
    if file == "-":
        return sys.stdin if mode == "r" else sys.stdout

    return open(file, mode, encoding="utf-8")


def main():
    as_json = False

    try:
        args = Args.parse()
        as_json = args.json

        files = set()

        for file in args.list_files():
            files.add(file)
            InitState(len(files)).log(as_json)

        for file in files:
            with open_file(file, "r") as fp:
                source = fp.read()

            source = ImportSorter(source, args.groups).sort()

            if args.format:
                source = run_program(source, args.format.split())

            FileState(file).log(as_json)

            with open_file(file, "w") as fp:
                fp.write(source)

        DoneState().log(as_json)

    except Exception as exc:
        ErrorState("\n".join(traceback.format_exception(exc))).log(as_json)


if __name__ == "__main__":
    main()
