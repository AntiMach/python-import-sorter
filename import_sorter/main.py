import shlex
import subprocess
import sys

from import_sorter.args import Args
from import_sorter.sorting import ImportSorter


def run_program(source: str, args: list[str]):
    result = subprocess.run(args, input=source, text=True, capture_output=True)

    if result.returncode:
        raise RuntimeError(result.stderr)

    return result.stdout


def main():
    args = Args.parse()

    with args.open_file("r") as fp:
        source = fp.read()

    source = ImportSorter(source, args.groups).sort()

    if args.format:
        source = run_program(source, [sys.executable, "-m", *shlex.split(args.format)])

    with args.open_file("w") as fp:
        fp.write(source)


if __name__ == "__main__":
    main()
