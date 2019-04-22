import json

import pathlib2 as pathlib
import pytest
from click.testing import CliRunner


@pytest.fixture
def simple_report():
    current_folder = pathlib.Path(__file__).resolve().parent
    return json.loads((current_folder / "simple_report.json").read_text())


@pytest.fixture
def cli_runner():
    return CliRunner()
