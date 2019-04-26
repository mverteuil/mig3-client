import json

import pathlib2 as pathlib
import pytest
from click.testing import CliRunner


@pytest.fixture
def simple_report():
    """Example of parsed pytest-json report contents."""
    current_folder = pathlib.Path(__file__).resolve().parent
    return json.loads((current_folder / "simple_report.json").read_text())


@pytest.fixture
def converted_tests():
    """Example of pytest-json report output converted to Mig3 spec."""
    return [{"module": "tests/test_converter.py", "test": "test_simple_convert"}]


@pytest.fixture
def cli_runner():
    """Create a Click CLI runner."""
    return CliRunner()
