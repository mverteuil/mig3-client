import mock
from mig3_client import JobSubmissionBuilder


def test_minimum_viable_submission():
    """Should produce a valid submission"""
    submission = JobSubmissionBuilder("p", "c", []).build()
    assert submission is not None


def test_configuration_id():
    """Should contain configuration ID used to initialize the builder"""
    submission = JobSubmissionBuilder("p", "c", []).build()
    assert submission.get("configuration") == "c", submission


def test_project_id():
    """Should contain project ID used to initialize the builder"""
    submission = JobSubmissionBuilder("p", "c", []).build()
    assert submission.get("project") == "p", submission


def test_tests():
    """Should contain tests used to initialize the builder"""
    submission = JobSubmissionBuilder("p", "c", ["anything"]).build()
    assert submission.get("tests") == ["anything"], submission


def test_version_details():
    """Should contain version details from git head commit"""
    with mock.patch("mig3_client.git") as patched_git:
        patched_git.Repo().head.object.hexsha = "a1" * 20
        patched_git.Repo().head.object.author.email = "user@example.com"

        submission = JobSubmissionBuilder("p", "c", []).build()

    assert submission.get("version", {}).get("hash") == ("a1" * 20), submission
