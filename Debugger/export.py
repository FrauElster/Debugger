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
    """
    Exports a recorded trace to json that Google Chromes tracing tool can read.
    The json format is described here:
    https://docs.google.com/document/d/1CvAClvFfyA5R-PhYUmn5OOQtYMH4h6I0nSsKchNAySU/edit#
    """

    def __init__(self, file_name):
        self.file_name = file_name

    def persist(self, records: List[TraceRecord]):
        times = list(map(lambda elem: elem.start_time, records))
        begin_time = min(times) if times else datetime.now()
        lines = ["[\n"]
        for record in records:
            time_stamp = record.start_time - begin_time
            time_stamp_micros = time_stamp.total_seconds() * 1_000_000
            if record.end_time is None:
                duration_micros = 0.0
            else:
                duration = record.end_time - record.start_time
                duration_micros = duration.total_seconds() * 1_000_000
            line = "{"
            line += f"\"name\": \"{record.function_name}\","
            line += f" \"cat\": \"abc\","
            line += f" \"ph\": \"X\","
            line += f" \"pid\": 0,"
            line += f" \"tid\": 0,"
            line += f" \"ts\": {time_stamp_micros},"
            line += f" \"dur\": {duration_micros}"
            line += "},\n"
            lines.append(line)

        if len(lines) > 1:
            # removing trailing comma after last element (to make it valid json)
            line = lines[-1]
            new_line = line[:-2] + "\n"
            lines[-1] = new_line

        lines.append("]\n")

        with open(self.file_name, "w+") as f:
            f.writelines(lines)
