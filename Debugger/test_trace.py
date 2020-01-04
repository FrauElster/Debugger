from datetime import datetime
from typing import List

from Debugger.trace import trace, TraceExporter, TraceRecord
from Debugger.types import TimeProvider


class MockExporter(TraceExporter):
    def __init__(self):
        self.records: List[TraceRecord] = []

    def export(self, records: List[TraceRecord]):
        self.records = records


class MockTimeProvider(TimeProvider):
    def __init__(self, time_stamps: List[datetime] = None):
        # the index gets incremented before being used
        self.current_index = -1
        self.time_stamps: List[datetime] = time_stamps if time_stamps is not None else []

    def get_current_time(self) -> datetime:
        if not self.time_stamps:
            return datetime.now()

        self.current_index += 1
        if self.current_index >= len(self.time_stamps):
            self.current_index = 0
        return self.time_stamps[self.current_index]


def test_records_method_call():
    p = MockExporter()

    @trace(exporter=p)
    def method():
        pass

    method()

    assert len(p.records) == 1
    r = p.records[0]
    assert r is not None
    assert r.function_name == "method"
    assert len(r.arguments) == 0
    assert len(r.keyword_arguments) == 0


def test_records_arguments():
    p = MockExporter()

    @trace(exporter=p)
    def method(arg):
        pass

    method("Test")

    assert len(p.records) == 1
    r = p.records[0]
    assert r is not None
    assert r.function_name == "method"
    assert len(r.arguments) == 1
    a = r.arguments[0]
    assert a == "Test"
    assert len(r.keyword_arguments) == 0


def test_records_keyword_arguments():
    p = MockExporter()

    @trace(exporter=p)
    def method(arg):
        pass

    method(arg="Test")

    assert len(p.records) == 1
    r = p.records[0]
    assert r is not None
    assert r.function_name == "method"
    assert len(r.arguments) == 0
    assert len(r.keyword_arguments) == 1
    assert "arg" in r.keyword_arguments
    kwa = r.keyword_arguments["arg"]
    assert kwa == "Test"


def my_method():
    pass


def test_records_transitive_method_calls():
    p = MockExporter()

    @trace(exporter=p)
    def method():
        my_method()

    method()

    assert len(p.records) == 2

    r = p.records[0]
    assert r is not None
    assert r.function_name == "method"
    assert len(r.arguments) == 0
    assert len(r.keyword_arguments) == 0

    r = p.records[1]
    assert r is not None
    assert r.function_name == "my_method"
    assert len(r.arguments) == 0
    assert len(r.keyword_arguments) == 0


def my_arg_method(arg, kwarg=None):
    pass


def test_records_transitive_method_calls_with_arguments():
    p = MockExporter()

    @trace(exporter=p)
    def method():
        my_arg_method("Test", kwarg="Hello")

    method()

    assert len(p.records) == 2

    r = p.records[0]
    assert r is not None
    assert r.function_name == "method"
    assert len(r.arguments) == 0
    assert len(r.keyword_arguments) == 0

    r = p.records[1]
    assert r is not None
    assert r.function_name == "my_arg_method"
    assert len(r.arguments) == 1
    a = r.arguments[0]
    assert a == "Test"
    assert len(r.keyword_arguments) == 1
    assert "kwarg" in r.keyword_arguments
    kwa = r.keyword_arguments["kwarg"]
    assert kwa == "Hello"


def test_records_start_and_end_times():
    p = MockExporter()
    time_stamps = [
        datetime(2020, 1, 1),
        datetime(2020, 1, 2),
        datetime(2020, 1, 3),
        datetime(2020, 1, 4)
    ]
    t = MockTimeProvider(time_stamps)

    @trace(exporter=p, time_provider=t)
    def method():
        my_arg_method("Test", kwarg="Hello")

    method()

    assert len(p.records) == 2

    r = p.records[0]
    assert r is not None
    assert r.start_time is not None
    assert r.start_time == datetime(2020, 1, 1)
    assert r.end_time is not None
    assert r.end_time == datetime(2020, 1, 4)

    r = p.records[1]
    assert r is not None
    assert r.start_time is not None
    assert r.start_time == datetime(2020, 1, 2)
    assert r.end_time is not None
    assert r.end_time == datetime(2020, 1, 3)
