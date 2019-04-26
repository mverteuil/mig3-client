class SubmissionError(Exception):
    """Base class for error cases when submitting to Mig3 service."""


class RequestError(SubmissionError):
    """The submission failed due to a reason other than a regression."""


class Regression(SubmissionError):
    """The submission failed due to a detected regression."""
