from mig3_client import mig3


def test_no_project(cli_runner):
    """Should require project id"""
    result = cli_runner.invoke(mig3)
    assert result.exception
    assert "Missing option" in result.output
    assert "--project" in result.output
