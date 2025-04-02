from pathlib import Path
import shutil


def main():
    Path("./bundled/libs").mkdir(parents=True, exist_ok=True)
    shutil.copy("../import_sorter.py", "./bundled/libs/import_sorter.py")


if __name__ == "__main__":
    main()
