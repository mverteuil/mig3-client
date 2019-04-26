from mig3_client import JobSubmissionBuilder


def test_minimum_viable_submission():
    """Should produce a valid submission"""
    submission = JobSubmissionBuilder("p", "c", []).build()
    assert submission is not None
