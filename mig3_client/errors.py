import click


class SubmissionError(click.ClickException):
    """Base class for error cases when submitting to Mig3 service."""

    def show(self, file=None):
        click.secho(f"{self.__class__.__name__}: {self.format_message()}", err=True, fg="red")


class Regression(SubmissionError):
    """The submission failed due to a detected regression."""


class RequestError(SubmissionError):
    """The submission failed due to a reason other than a regression."""

    exit_code = 2
