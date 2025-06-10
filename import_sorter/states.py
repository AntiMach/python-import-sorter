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
class FindState(State):
    STATE = "find"
    TEMPLATE = "Found {file}"

    file: str


@dataclass
class FileFormatState(State):
    STATE = "file_format"
    TEMPLATE = "Formatted {file} ({progress}%)"

    file: str
    progress: float


@dataclass
class FileErrorState(State):
    STATE = "file_error"
    TEMPLATE = "File {file} has a syntax error ({progress}%)"

    file: str
    error: str
    progress: float


@dataclass
class DoneState(State):
    STATE = "done"
    TEMPLATE = "Done formatting"


@dataclass
class ErrorState(State):
    STATE = "error"
    TEMPLATE = "An unexpected error has occurred: {error}"

    error: str
