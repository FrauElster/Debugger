from typing import Tuple, Any, Dict
from dataclasses import dataclass
from enum import Enum, auto


class TraceLevel(Enum):
    MINIMAL = auto()
    SOME = auto()
    ALL = auto()


@dataclass
class TraceRecord:
    function_name: str
    arguments: Tuple[Any]
    keyword_arguments: Dict[str, Any]
