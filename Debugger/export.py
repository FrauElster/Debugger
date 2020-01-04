from typing import List
from .types import TraceRecord
from datetime import datetime


class TraceExporter:
    """
    Collects all informations and does shit with it
    """

    def persist(self, records: List[TraceRecord]):
        pass


class ChromeJsonExporter(TraceExporter):
    def __init__(self, file_name):
        self.file_name = file_name

    def persist(self, records: List[TraceRecord]):
        times = list(map(lambda elem: elem.start_time, records))
        begin_time = min(times) if times else datetime.now()
        lines = ["[\n"]
        for record in records:
            # TODO convert to correct time format
            time_stamp = record.start_time - begin_time
            time_stamp_micros = time_stamp.total_seconds() / 1_000_000
            duration = record.end_time - record.start_time
            duration_micros = duration.total_seconds() / 1_000_000
            line = "{"
            line += f"\"name\": \"{record.function_name}\","
            line += f" \"cat\": \"PERF\","
            line += f" \"ph\": \"X\","
            line += f" \"pid\": 0,"
            line += f" \"tid\": 0,"
            line += f" \"ts\": {time_stamp_micros}"
            line += f" \"dur\": {duration_micros}"
            line += "}\n"
            lines.append(line)

        lines.append("]\n")

        with open(self.file_name, "w+") as f:
            f.writelines(lines)
