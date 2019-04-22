from __future__ import absolute_import, unicode_literals

import json
import sys

import click
import git
import requests

from .vendors import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


class Regression(Exception):
    """Raised when Mig3 service rejects the submission request."""


class log_attempt(object):
    def __init__(self, message):
        self._message = message

    def __enter__(self):
        click.echo("{}...".format(self._message), err=True, nl=False)
        return

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type or exc_val or exc_tb:
            click.secho("FAIL\n{exc_type}: {exc_val}".format(**locals()), err=True, fg="red")
            exit(1)
        else:
            click.secho("OK", err=True, fg="green")


class ReportConverter(object):
    def __init__(self, report):
        self.report = report

    def _tests(self):
        for test_document in self.report["included"]:
            module, test = test_document["attributes"]["name"].split("::")
            yield {"module": module, "test": test, "outcome": test_document["attributes"]["outcome"]}

    def convert(self):
        return [test for test in self._tests()]


class JobSubmissionBuilder(object):
    """Build the job submission for Mig3."""

    def __init__(self, project, configuration, test_data):
        self.project = project
        self.configuration = configuration
        self.test_data = test_data

    def _get_version(self):
        repository = git.Repo(search_parent_directories=True)
        return repository.head.object.hexsha

    def build(self):
        return {
            "project_version": self._get_version(),
            "tests": self.test_data,
            "project": self.project,
            "configuration": self.configuration,
            "mig3_version": __version__,
        }


@click.command()
@click.option("-p", "--project", required=True, help="Project ID (from Mig3 service).")
@click.option("-c", "--configuration", required=True, help="Configuration ID (from mig3 service).")
@click.option("--endpoint", required=True, help="Mig3 job submission endpoint.")
@click.option("--token", required=True, help="Mig3 builder authorization token.")
@click.option("--report", default=".report.json", type=click.File(), help="Specify the pytest-json report filename.")
@click.option("-n", "--dry-run", is_flag=True, help="Show report on stdout instead of submitting it to Mig3 service.")
@click.version_option(__version__)
def mig3(project, configuration, endpoint, token, report, dry_run):
    """Validate test results with mig3 service.

    Run this command after running py.test with json results enabled to validate the test outcome:
        py.test --json=.report.json


    The following environment variables can be used in lieu of passing options: MIG3_PROJECT, MIG3_CONFIGURATION,
    MIG3_ENDPOINT, MIG3_TOKEN, MIG3_DRY_RUN

    """
    with log_attempt("Reading report"):
        report_json = json.loads(report.read())

    with log_attempt("Converting test data"):
        test_data = ReportConverter(report_json).convert()

    with log_attempt("Building submission"):
        submission = JobSubmissionBuilder(project, configuration, test_data).build()

    with log_attempt("Sending submission"):
        if not dry_run:
            response = requests.post(
                endpoint, data=submission, headers={"Authorization": "Bearer {token}".format(**locals())}
            )
            if response.status_code != 200:
                raise Regression(response.content)
        else:
            json.dump(submission, sys.stdout)


if __name__ == "__main__":
    mig3(auto_envvar_prefix="MIG3")
