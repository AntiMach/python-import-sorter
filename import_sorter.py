import sys
import shlex
import subprocess
from pathlib import Path
from typing import Iterable
from argparse import ArgumentParser
from ast import alias, parse, Import, unparse, ImportFrom


ImportLike = Import | ImportFrom

DEFAULT_IMPORT_GROUPS = "__future__", ""


def alias_key(x: alias, /):
    real_name = unparse(x)
    return len(real_name), real_name


def import_key(x: ImportLike, /):
    if isinstance(x, Import):
        module = ""
        unparsed = unparse(x)
    elif isinstance(x, ImportFrom):
        module = x.module or ""
        unparsed = unparse(x)
    else:
        raise NotImplementedError

    return len(unparsed), len(module), unparsed, module


def sort_aliases(aliases: Iterable[alias]):
    return sorted(aliases, key=alias_key)


def sort_imports(imports: Iterable[ImportLike]):
    return sorted(imports, key=import_key)


def format_file(content: str, formatter: str):
    result = subprocess.run(
        [sys.executable, "-m", *shlex.split(formatter), "-"],
        input=content,
        text=True,
        capture_output=True,
    )
    return content if result.returncode else result.stdout


def main():
    parser = ArgumentParser()

    parser.add_argument("file")
    parser.add_argument("-f", "--formatter", default="ruff format")
    parser.add_argument("-g", "--groups", action="extend", nargs="+", default=[])

    args = parser.parse_args()

    file_path: Path | None = None if args.file == "-" else Path(args.file)
    formatter: str = args.formatter
    groups: list[str] = args.groups

    with file_path.open("r", encoding="utf-8") if file_path else sys.stdin as fp:
        file_text = fp.read()

    import_groups: dict[str, dict[str, ImportLike]] = {group: {} for group in (*DEFAULT_IMPORT_GROUPS, *groups)}

    def add_stmt(stmt: ImportLike, group: str, module: str):
        imports = import_groups.get(group, import_groups[""])

        if old_stmt := imports.get(module):
            old_stmt.names.extend(stmt.names)
        else:
            imports[module] = stmt

    target_line = 0

    for stmt in parse(file_text).body:
        if isinstance(stmt, Import):
            for name in stmt.names:
                add_stmt(Import([name]), "", f"i+{name.name}")

        elif isinstance(stmt, ImportFrom):
            module = stmt.module or ""
            group, *_ = (stmt.module or "").split(".")
            add_stmt(
                ImportFrom(stmt.module, sort_aliases(stmt.names), stmt.level),
                group,
                f"f+{module}",
            )

        else:
            break

        target_line = stmt.end_lineno or stmt.lineno

    content = ""

    for imports in import_groups.values():
        for import_stmt in sort_imports(imports.values()):
            content += unparse(import_stmt)
            content += "\n"
        if imports:
            content += "\n"

    for line in file_text.splitlines()[target_line:]:
        content += line
        content += "\n"

    content = format_file(content, formatter)

    with file_path.open("w", encoding="utf-8") if file_path else sys.stdout as fp:
        fp.write(content)


if __name__ == "__main__":
    main()
