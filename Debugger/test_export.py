from .export import ChromeJsonExporter


def test_chrome_json_export():
    records = []
    exporter = ChromeJsonExporter()
    exporter.persist(records)
