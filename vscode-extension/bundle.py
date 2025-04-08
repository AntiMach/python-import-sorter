import shutil
from subprocess import Popen


def main():
    shutil.rmtree("./bundled/libs", ignore_errors=True)

    res = Popen(
        [
            "python",
            "-m",
            "pip",
            "install",
            "-t",
            "./bundled/libs",
            "--no-cache-dir",
            "--implementation",
            "py",
            "--no-deps",
            "--upgrade",
            "..",
        ],
    ).wait()

    if res:
        exit(res)

    shutil.rmtree("./bundled/libs/bin")


if __name__ == "__main__":
    main()
