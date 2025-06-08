import os
import sys
import shlex
import subprocess

from import_sorter.args import Args
from import_sorter.sorting import ImportSorter


def run_program(source: str, args: list[str]):
    if args[0].casefold() in ("python", "python3", "python3.11"):
        args[0] = sys.executable

    result = subprocess.run(args, env=os.environ, input=source, text=True, capture_output=True)

    if result.returncode:
        raise RuntimeError(result.stderr)

    return result.stdout


def main():
    args = Args.parse()
    python_files = args.get_python_files()

    if len(python_files) == 1 and python_files[0] == "-":
        with args.open_file("r") as fp:
            source = fp.read()

        source = ImportSorter(source, args.groups).sort()

        if args.format:
            source = run_program(source, shlex.split(args.format))

        with args.open_file("w") as fp:
            fp.write(source)
    else:
        for file_path in python_files:
            with open(file_path, "r", encoding="utf-8") as fp:
                source = fp.read()

            source = ImportSorter(source, args.groups).sort()

            if args.format:
                source = run_program(source, shlex.split(args.format))

            with open(file_path, "w", encoding="utf-8") as fp:
                fp.write(source)


if __name__ == "__main__":
    main()
