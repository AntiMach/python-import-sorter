import os
import sys
import subprocess


def run_program(source: str, args: list[str]):
    if args[0].casefold() in ("python", "python3", "python3.11"):
        args[0] = sys.executable

    result = subprocess.run(args, env=os.environ, input=source, text=True, capture_output=True, encoding="utf-8")

    if result.returncode:
        raise RuntimeError(result.stderr)

    return result.stdout
