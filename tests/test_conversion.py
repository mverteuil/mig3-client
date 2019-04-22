from mig3_client import ReportConverter


def test_simple_report(simple_report):
    """Should be simplest possible report."""
    assert len(simple_report["included"]) == 1


def test_simple_convert(simple_report):
    """Should build submission from simplest possible report."""
    converter = ReportConverter(simple_report)
    assert len(converter.convert()) == 1
