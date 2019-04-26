from mig3_client import ReportConverter


def test_simple_report(simple_report):
    """Should be simplest possible report."""
    assert len(simple_report["included"]) == 1


def test_basic_convert(simple_report):
    """Should convert tests from simplest possible report."""
    converter = ReportConverter(simple_report)
    assert len(converter.convert()) == 1


def test_convert_module_name(simple_report):
    """Should extract module name from report item."""
    result = ReportConverter(simple_report).convert()
    converted_test = result[0]
    assert converted_test.get("module") == "tests/test_examples.py", converted_test


def test_convert_test_name(simple_report):
    """Should extract test name from report item."""
    result = ReportConverter(simple_report).convert()
    converted_test = result[0]
    assert converted_test.get("test") == "test_success", converted_test


def test_convert_outcome(simple_report):
    """Should extract outcome from report item."""
    result = ReportConverter(simple_report).convert()
    converted_test = result[0]
    assert converted_test.get("outcome") == "passed", converted_test
