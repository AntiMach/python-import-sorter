import json
from dataclasses import asdict, dataclass


@dataclass
class State:
    STATE = ""
    TEMPLATE = ""

    def message(self, as_json: bool) -> str:
        if as_json:
            return json.dumps({"state": self.STATE, **asdict(self)})
        else:
            return self.TEMPLATE.format(**asdict(self))


@dataclass
class FoundState(State):
    STATE = "init"
    TEMPLATE = "Found {file}"

    file: str


@dataclass
class FileState(State):
    STATE = "file"
    TEMPLATE = "Formatted {file} ({prog}%)"

    file: str
    prog: float


@dataclass
class DoneState(State):
    STATE = "done"
    TEMPLATE = "Done formatting"


@dataclass
class SyntaxErrorState(State):
    STATE = "file_error"
    TEMPLATE = "File {file} has a syntax error ({prog}%)"

    file: str
    prog: float
    error: str


@dataclass
class ErrorState(State):
    STATE = "error"
    TEMPLATE = "An unexpected error has occurred: {error}"

    error: str
