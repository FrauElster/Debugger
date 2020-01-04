import tempfile
from .export import ChromeJsonExporter


class TestChromeExporter:
    def test_can_export_zero_records(self):
        records = []
        with tempfile.NamedTemporaryFile(suffix=".json") as f:
            exporter = ChromeJsonExporter(f.name)
            exporter.persist(records)

            lines = f.readlines()
            expected_lines = [b'[\n', b']\n']
            assert len(expected_lines) == len(lines)
            for l1, l2 in zip(expected_lines, lines):
                assert l1 == l2
