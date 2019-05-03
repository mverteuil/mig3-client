# -*- coding: utf-8 -*-
import click


class SubmissionError(click.ClickException):
    """Base class for error cases when submitting to Mig3 service."""

    def show(self, file=None):
        """Flush this error to stderr or given file."""
        click.secho(
            "{class_name}: {message}".format(class_name=self.__class__.__name__, message=self.format_message()),
            err=True,
            fg="red",
        )


class Regression(SubmissionError):
    """The submission failed due to a detected regression."""


class RequestError(SubmissionError):
    """The submission failed due to a reason other than a regression."""

    exit_code = 2
