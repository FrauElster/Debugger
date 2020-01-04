from typing import List
from .types import TraceRecord


class TraceExporter:
    def persist(self, records: List[TraceRecord]):
        pass


class ChromeJsonExporter(TraceExporter):
    def persist(self, records: List[TraceRecord]):
        pass
