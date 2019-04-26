import json
from unittest import mock

from mig3_client import mig3

ALL_ARGUMENTS = {
    "configuration": "--configuration c",
    "endpoint": "--endpoint e",
    "project": "--project p",
    "token": "--token t",
}


def test_no_project(cli_runner):
    """Should require project id"""
    arguments = ALL_ARGUMENTS.copy()
    del arguments["project"]

    result = cli_runner.invoke(mig3, " ".join(arguments.values()))

    assert result.exception
    assert "Missing option" in result.output
    assert "-p" in result.output
    assert "--project" in result.output


def test_no_configuration(cli_runner):
    """Should require configuration id"""
    arguments = ALL_ARGUMENTS.copy()
    del arguments["configuration"]

    result = cli_runner.invoke(mig3, " ".join(arguments.values()))

    assert result.exception
    assert "Missing option" in result.output
    assert "-c" in result.output
    assert "--configuration" in result.output


def test_no_endpoint(cli_runner):
    """Should require endpoint"""
    arguments = ALL_ARGUMENTS.copy()
    del arguments["endpoint"]

    result = cli_runner.invoke(mig3, " ".join(arguments.values()))

    assert result.exception
    assert "Missing option" in result.output
    assert "--endpoint" in result.output


def test_no_token(cli_runner):
    """Should require token"""
    arguments = ALL_ARGUMENTS.copy()
    del arguments["token"]

    result = cli_runner.invoke(mig3, " ".join(arguments.values()))

    assert result.exception
    assert "Missing option" in result.output
    assert "--token" in result.output


def test_no_report(cli_runner):
    """Should require json report"""
    with cli_runner.isolated_filesystem():
        result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert result.exception
    assert "Invalid value" in result.output
    assert "--report" in result.output


def test_invalid_report(cli_runner):
    """Should fail with useful error"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write("Decidedly not JSON content.")
        result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert result.exception
    assert "Reading report...FAIL" in result.output
    assert "JSONDecodeError" in result.output


def test_happy_path(cli_runner, simple_report):
    """Should complete with successful exit code"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write(json.dumps(simple_report))

        with mock.patch.multiple("mig3_client", requests=mock.DEFAULT, git=mock.DEFAULT) as patches:
            patches["requests"].post().status_code = 200

            result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert not result.exception, result.output
    assert result.exit_code == 0, result.status_code
    assert "Reading report...OK" in result.output
    assert "Converting test data...OK" in result.output
    assert "Building submission...OK" in result.output
    assert "Sending submission...OK" in result.output


def test_valid_report_with_regression(cli_runner, simple_report):
    """Should submit report to Mig3 service"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write(json.dumps(simple_report))

        with mock.patch.multiple("mig3_client", requests=mock.DEFAULT, git=mock.DEFAULT) as patches:
            patches["requests"].post().status_code = 200

            result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert not result.exception, result.output
    assert "Reading report...OK" in result.output
    assert "Converting test data...OK" in result.output
    assert "Building submission...OK" in result.output
    assert "Sending submission...OK" in result.output
