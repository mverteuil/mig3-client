import json

import mock

from mig3_client import mig3

ALL_ARGUMENTS = {"target": "--target t", "build": "--build b", "endpoint": "--endpoint e", "token": "--token token"}


def test_no_build_number(cli_runner):
    """Should require build number"""
    arguments = ALL_ARGUMENTS.copy()
    del arguments["build"]

    result = cli_runner.invoke(mig3, " ".join(arguments.values()))

    assert result.exception
    assert "Missing option" in result.output
    assert "-b" in result.output
    assert "--build" in result.output


def test_no_target_configuration(cli_runner):
    """Should require target id"""
    arguments = ALL_ARGUMENTS.copy()
    del arguments["target"]

    result = cli_runner.invoke(mig3, " ".join(arguments.values()))

    assert result.exception
    assert "Missing option" in result.output
    assert "-t" in result.output
    assert "--target" in result.output


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
    assert "JSON" in result.output


def test_happy_path(cli_runner, simple_report):
    """Should complete with successful exit code"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write(json.dumps(simple_report))

        with mock.patch.multiple("mig3_client", requests=mock.DEFAULT, git=mock.DEFAULT) as patches:
            patches["requests"].post().status_code = 201

            result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert not result.exception, result.output
    assert result.exit_code == 0, result.status_code
    assert "Reading report...OK" in result.output
    assert "Converting test data...OK" in result.output
    assert "Building submission...OK" in result.output
    assert "Sending submission...OK" in result.output


def test_valid_report_with_regression(cli_runner, simple_report):
    """Should fail with exit code 1 on regressions reported from Mig3 service"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write(json.dumps(simple_report))

        with mock.patch.multiple("mig3_client", requests=mock.DEFAULT, git=mock.DEFAULT) as patches:
            # Simulate 409 Conflict response
            patches["requests"].post().status_code = 409
            result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert result.exception, result.output
    assert result.exit_code == 1, result.exit_code
    assert "Reading report...OK" in result.output
    assert "Converting test data...OK" in result.output
    assert "Building submission...OK" in result.output
    assert "Sending submission...FAIL" in result.output


def test_valid_report_with_bad_endpoint(cli_runner, simple_report):
    """Should fail with useful error"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write(json.dumps(simple_report))

        with mock.patch.multiple("mig3_client", requests=mock.DEFAULT, git=mock.DEFAULT) as patches:
            # Simulate 404 Not Found response
            patches["requests"].post().status_code = 404
            patches["requests"].post().content = "Page not found"
            result = cli_runner.invoke(mig3, args=" ".join(ALL_ARGUMENTS.values()))

    assert result.exception, result.output
    assert result.exit_code == 1, result.exit_code
    assert "Reading report...OK" in result.output
    assert "Converting test data...OK" in result.output
    assert "Building submission...OK" in result.output
    assert "Sending submission...FAIL" in result.output
    assert "RequestError" in result.output
    assert "Page not found" in result.output


def test_valid_report_with_dry_run(cli_runner, simple_report):
    """Should display submission on stdout"""
    with cli_runner.isolated_filesystem():
        with open(".report.json", "w") as f:
            f.write(json.dumps(simple_report))

        with mock.patch("mig3_client.git") as patched_git:
            patched_git.Repo().head.object.hexsha = "a1" * 20
            patched_git.Repo().head.object.author.email = "user@example.com"

            arguments = ALL_ARGUMENTS.copy()
            arguments["dry_run"] = "-n"
            result = cli_runner.invoke(mig3, args=" ".join(arguments.values()))

    assert not result.exception, result.output
    assert result.exit_code == 0, result.exit_code
    assert "Reading report...OK" in result.output
    assert "Converting test data...OK" in result.output
    assert "Building submission...OK" in result.output
    assert "Sending submission..." not in result.output
    assert '"author":' in result.output, result.output
