import sys
import traceback
from typing import Literal, Iterator

from import_sorter.args import Args
from import_sorter.sorting import sort_imports
from import_sorter.external import run_program
from import_sorter.states import State, DoneState, FindState, ErrorState, FileErrorState, FileFormatState


def open_file(file: str, mode: Literal["r", "w"]):
    if file == "-":
        return sys.stdin if mode == "r" else sys.stdout

    return open(file, mode, encoding="utf-8")


def state_machine(args: Args) -> Iterator[State]:
    try:
        files = set()

        # Find files to format
        for file in args.list_files():
            if file not in files:
                files.add(file)
                yield FindState(file)

        # Format files
        for i, file in enumerate(files, 1):
            progress = i * 100 / len(files)

            with open_file(file, "r") as fp:
                source = fp.read()

            try:
                source = sort_imports(source, args.groups)
            except SyntaxError:
                yield FileErrorState(file, traceback.format_exc(3), progress)
                continue

            if args.format:
                try:
                    source = run_program(source, args.format)
                except Exception:
                    yield FileErrorState(file, traceback.format_exc(3), progress)
                    continue

            with open_file(file, "w") as fp:
                fp.write(source)

            yield FileFormatState(file, progress)

        # Signal the processing is done
        yield DoneState()

    except Exception:
        # Signal the processing errored out
        yield ErrorState(traceback.format_exc())


def main():
    args = Args.parse()

    for state in state_machine(args):
        if not args.quiet and (message := state.message(args.as_json)):
            print(message, file=sys.stderr)


if __name__ == "__main__":
    main()
