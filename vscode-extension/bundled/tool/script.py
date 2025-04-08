import sys

if sys.version_info < (3, 11):
    sys.stderr.write("Python 3.11+ is required for python-import-sorter to run.")
    sys.exit(1)

from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.resolve() / "libs"))

from import_sorter.__main__ import main

main()
