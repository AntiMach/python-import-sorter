import libcst as cst
from libcst.display import dump as cst_dump
from typing import cast, TypeVar, Callable, Iterable, Sequence, ParamSpec, OrderedDict


P = ParamSpec("P")
T = TypeVar("T")


def list_generator(func: Callable[P, Iterable[T]]) -> Callable[P, list[T]]:
    def wrapped(*args: P.args, **kwargs: P.kwargs) -> list[T]:
        return list(func(*args, **kwargs))

    return wrapped


class ImportSorter(cst.CSTTransformer):
    DEFAULT_IMPORT_GROUPS = "__future__", ""

    def __init__(self, import_groups: list[str]):
        super().__init__()
        self.import_groups = import_groups
        self.import_stmts: list[cst.SimpleStatementLine] = []
        self.last_import_idx = 0
        self.found_non_import = False

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        if not self.import_stmts:
            return updated_node

        # Split all imports, while retaining comments
        import_stmts = [
            new_import_stmt
            for import_stmt in self.import_stmts
            for new_import_stmt in self.__split_semicolons(import_stmt)
        ]

        # Remove duplicate imports
        import_stmts = [import_stmt for import_stmt in self.__merge_remove_imports(import_stmts)]

        # # Sort imports
        # sorted_imports = sorted(
        #     self.import_stmts,
        #     key=lambda x: (len(cst_dump(x)), cst_dump(x)),
        # )

        # sorted_import_froms = []

        # for import_node in sorted_imports:
        #     import_from = import_node.body[0]

        #     if not isinstance(import_from, cst.ImportFrom):
        #         sorted_import_froms.append(import_node)
        #         continue

        #     if isinstance(import_from.names, cst.ImportStar):
        #         sorted_import_froms.append(import_node)
        #         continue

        #     sorted_names = sorted(import_from.names, key=lambda x: len(cst_dump(x)))
        #     sorted_import_froms.append(import_node.with_changes(body=[import_from.with_changes(names=sorted_names)]))

        # Replace the body up to the first non-import with sorted imports
        return updated_node.with_changes(body=[*import_stmts, *updated_node.body[self.last_import_idx :]])

    # region Statement Splitters

    def __split_semicolons(self, stmt: cst.SimpleStatementLine):
        imports = cast(Sequence[cst.Import | cst.ImportFrom], stmt.body)
        first_import = imports[0]
        last_import = imports[-1]

        for node in imports:
            yield from self.__split_multi_imports(
                [node.with_changes(semicolon=cst.MaybeSentinel.DEFAULT)],
                stmt.leading_lines if node is first_import else [],
                stmt.trailing_whitespace if node is last_import else cst.TrailingWhitespace(),
            )

    def __split_multi_imports(
        self,
        body: Sequence[cst.Import | cst.ImportFrom],
        leading_lines: Sequence[cst.EmptyLine],
        trailing_whitespace: cst.TrailingWhitespace,
    ):
        node = body[0]

        if not isinstance(node, cst.Import):
            yield cst.SimpleStatementLine(body, leading_lines, trailing_whitespace)
            return

        first_name = node.names[0]
        last_name = node.names[-1]

        for name in node.names:
            yield cst.SimpleStatementLine(
                [cst.Import(names=[name.with_changes(comma=cst.MaybeSentinel.DEFAULT)])],
                leading_lines if name is first_name else [],
                trailing_whitespace if name is last_name else cst.TrailingWhitespace(),
            )

    # endregion

    # region Import Merger/Remover

    def __merge_remove_imports(self, stmts: list[cst.SimpleStatementLine]):
        result: OrderedDict[str, cst.SimpleStatementLine] = OrderedDict()

        for stmt in stmts:
            body = cast(cst.Import | cst.ImportFrom, stmt.body[0])

            if isinstance(body, cst.Import):
                name = "i:" + (body.names[0].evaluated_alias or body.names[0].evaluated_name)
                result.setdefault(name, stmt)
                continue

            name = "if:" + cst_dump(body.module or cst.Dot())

            if not (from_import := result.get(name)):
                result[name] = stmt
                continue

            prev_body = cast(cst.ImportFrom, from_import.body[0])

            if isinstance(prev_body.names, cst.ImportStar):
                continue

            if isinstance(body.names, cst.ImportStar):
                result[name] = stmt
                continue

            result[name] = from_import.with_changes(
                body=[prev_body.with_changes(names=[*prev_body.names, *body.names])]
            )

    # endregion

    # region Statement Visitors

    def visit_BaseCompoundStatement(self, node: cst.BaseCompoundStatement) -> bool | None:
        self.found_non_import = True
        return False

    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> bool | None:
        if self.found_non_import:
            # We previously encountered a non import statement
            return False

        if not node.body:
            # This statement has no body
            self.last_import_idx += 1
            return False

        if isinstance(node.body[0], (cst.Import, cst.ImportFrom)):
            # This statement is an import
            self.last_import_idx += 1
            self.import_stmts.append(node)
            return True

        # This is not an import statement
        self.found_non_import = True

        return False

    # endregion


def sort_imports(source_code: str, import_groups: list[str]) -> str:
    """Sort imports in the provided Python source code."""
    return cst.parse_module(source_code).visit(ImportSorter(import_groups)).code


def main():
    # Example usage
    sample_code = """
import a; import b # comment 1

from a import (
    b,
    c as d, # comment 2
    # comment 3
    e
); from b import c; import abc

# Some comment before some import
import a, b, c
import d, e

# Some comment after all imports
class Thing:
    ...
"""

    print(sort_imports(sample_code, []))


if __name__ == "__main__":
    main()
