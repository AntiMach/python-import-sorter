import ast
from typing import Iterable, Sequence


ImportLike = ast.Import | ast.ImportFrom


class ImportSorter:
    DEFAULT_IMPORT_GROUPS = "__future__", ""

    source: str
    groups: dict[str, dict[str, ImportLike]]

    def __init__(self, source: str, groups: Sequence[str]):
        self.source = source
        self.groups = {group: {} for group in (*self.DEFAULT_IMPORT_GROUPS, *groups)}

    # region Sorting

    def sort(self) -> str:
        last_line = 0

        for stmt in ast.parse(self.source).body:
            if self._read_stmt(stmt):
                last_line = stmt.lineno - 1
                break

        new_source = ""

        for imports in self.groups.values():
            for import_stmt in self._sort_imports(imports.values()):
                new_source += ast.unparse(import_stmt)
                new_source += "\n"
            if imports:
                new_source += "\n"

        new_source += "\n"

        for line in self.source.splitlines()[last_line:]:
            new_source += line
            new_source += "\n"

        return new_source

    def _read_stmt(self, stmt: ast.stmt) -> bool | None:
        if isinstance(stmt, ast.Import):
            for name in stmt.names:
                self._add_stmt(ast.Import([name]), "", f"i+{name.name}")

        elif isinstance(stmt, ast.ImportFrom):
            module = stmt.module or ""
            group, *_ = (stmt.module or "").split(".")
            self._add_stmt(
                ast.ImportFrom(stmt.module, self._sort_aliases(stmt.names), stmt.level),
                group,
                f"f+{module}",
            )

        else:
            return True

    def _add_stmt(self, stmt: ImportLike, group: str, module: str):
        import_group = self.groups.get(group, self.groups[""])

        if old_stmt := import_group.get(module):
            old_stmt.names.extend(stmt.names)
        else:
            import_group[module] = stmt

    # endregion

    # region Sorters

    def _sort_aliases(self, aliases: Iterable[ast.alias]):
        return sorted(aliases, key=self._alias_key)

    def _sort_imports(self, imports: Iterable[ImportLike]):
        return sorted(imports, key=self._import_key)

    def _alias_key(self, x: ast.alias, /):
        real_name = ast.unparse(x)
        return len(real_name), real_name

    def _import_key(self, x: ImportLike, /):
        if isinstance(x, ast.Import):
            module = ""
            unparsed = ast.unparse(x)
        elif isinstance(x, ast.ImportFrom):
            module = x.module or ""
            unparsed = ast.unparse(x)
        else:
            raise NotImplementedError

        return len(unparsed), len(module), unparsed, module

    # endregion
