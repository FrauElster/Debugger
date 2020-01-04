from typing import Tuple, Any, Dict
from dataclasses import dataclass
from enum import Enum, auto
from datetime import datetime


class TraceLevel(Enum):
    """
    Determines in what depth the tracer records
    """

    MINIMAL = auto()
    SOME = auto()
    ALL = auto()


@dataclass
class TraceRecord:
    function_name: str
    arguments: Tuple[Any]
    keyword_arguments: Dict[str, Any]
    start_time: datetime
    end_time: datetime = None
