import shutil
from subprocess import Popen


def main():
    shutil.rmtree("./bundled/libs", ignore_errors=True)
    exit(
        Popen(
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
    )


if __name__ == "__main__":
    main()
