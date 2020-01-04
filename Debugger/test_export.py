import tempfile
from .export import ChromeJsonExporter
from .types import TraceRecord
from datetime import datetime


def assert_can_persist_records(expected_lines, records):
    with tempfile.NamedTemporaryFile(suffix=".json") as f:
        exporter = ChromeJsonExporter(f.name)
        exporter.persist(records)

        lines = f.readlines()
        assert len(expected_lines) == len(lines)
        for l1, l2 in zip(expected_lines, lines):
            assert l1 == l2


class TestChromeExporter:
    def test_can_export_zero_records(self):
        records = []
        expected_lines = [b'[\n', b']\n']
        assert_can_persist_records(expected_lines, records)

    def test_can_export_one_records(self):
        records = [
            TraceRecord("method", tuple(), dict(), datetime(2020, 1, 1), datetime(2020, 1, 2))
        ]
        expected_lines = [
            b'[\n',
            b'{"name": "method", "cat": "abc", "ph": "X", "pid": 0, "tid": 0, "ts": 0.0, "dur": 86400000000.0}\n',
            b']\n'
        ]
        assert_can_persist_records(expected_lines, records)

    def test_can_export_two_or_more_records(self):
        records = [
            TraceRecord("method", tuple(), dict(), datetime(2020, 1, 1), datetime(2020, 1, 4)),
            TraceRecord("method", tuple(), dict(), datetime(2020, 1, 2), datetime(2020, 1, 3))
        ]
        expected_lines = [
            b'[\n',
            b'{"name": "method", "cat": "abc", "ph": "X", "pid": 0, "tid": 0, "ts": 0.0, "dur": 259200000000.0},\n',
            b'{"name": "method", "cat": "abc", "ph": "X", "pid": 0, "tid": 0, "ts": 86400000000.0, '
            b'"dur": 86400000000.0}\n',
            b']\n'
        ]
        assert_can_persist_records(expected_lines, records)
