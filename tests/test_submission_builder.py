import mock

from mig3_client import JobSubmissionBuilder


def test_minimum_viable_submission(converted_tests):
    """Should produce something"""
    submission = JobSubmissionBuilder("t", "b", converted_tests).build()
    assert submission is not None


def test_configuration_id(converted_tests):
    """Should contain target configuration ID used to initialize the builder"""
    submission = JobSubmissionBuilder("t", "b", converted_tests).build()
    assert submission.get("target") == "t", submission


def test_build_number(converted_tests):
    """Should contain build number used to initialize the builder"""
    submission = JobSubmissionBuilder("t", "b", converted_tests).build()
    assert submission.get("number") == "b", submission


def test_tests():
    """Should contain test results used to initialize the builder"""
    submission = JobSubmissionBuilder("t", "b", ["anything"]).build()
    assert submission.get("results") == ["anything"], submission


def test_version_details(converted_tests):
    """Should contain version details from git head commit"""
    with mock.patch("mig3_client.git") as patched_git:
        patched_git.Repo().head.object.hexsha = "a1" * 20
        patched_git.Repo().head.object.author.email = "user@example.com"

        submission = JobSubmissionBuilder("t", "b", converted_tests).build()

    assert submission.get("version", {}).get("hash") == ("a1" * 20), submission
    assert submission.get("version", {}).get("author") == ("user@example.com"), submission
