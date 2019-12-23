from typing import List

from Debugger.trace import trace, TracePersistor, TraceRecord


class MockPersistor(TracePersistor):
    def __init__(self):
        self.records: List[TraceRecord] = []

    def persist(self, records: List[TraceRecord]):
        self.records = records


def test_records_method_call():
    p = MockPersistor()

    @trace(persistor=p)
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
    p = MockPersistor()

    @trace(persistor=p)
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
    p = MockPersistor()

    @trace(persistor=p)
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