import logging
from typing import List

from Debugger.trace import trace, TraceExporter, TraceRecord


class MockExporter(TraceExporter):
    def __init__(self):
        self.records: List[TraceRecord] = []

    def persist(self, records: List[TraceRecord]):
        self.records = records


def test_records_method_call():
    logger = logging.getLogger(__name__)
    logger.info("test")
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
