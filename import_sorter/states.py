import sys
import json
from dataclasses import asdict, dataclass


@dataclass
class StateLog:
    STATE = ""

    def message(self) -> str:
        assert self.__doc__ is not None
        return self.__doc__.format(**asdict(self))

    def json(self) -> str:
        return json.dumps({"state": self.STATE, **asdict(self)})

    def log(self, as_json: bool = False):
        print(self.json() if as_json else self.message(), file=sys.stderr)


@dataclass
class InitState(StateLog):
    "Formatting {count} files"

    STATE = "init"

    count: int


@dataclass
class FileState(StateLog):
    "Formatted {file}"

    STATE = "file"

    file: str


@dataclass
class DoneState(StateLog):
    "Done formatting"

    STATE = "done"


@dataclass
class ErrorState(StateLog):
    "An unexpected error has occurred: {error}"

    STATE = "error"

    error: str
