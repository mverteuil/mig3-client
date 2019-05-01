from __future__ import absolute_import, unicode_literals

import json
import sys

import click
import git
import requests

from .errors import Regression, RequestError
from .vendors import poetry_version

__version__ = poetry_version.extract(source_file=__file__)


class log_attempt(object):
    """Log message and result for code block contained in the context to stderr.

    Parameters
    ----------
    message : str
        Indicates what is being attempted to the user

    Examples
    --------
    with log_attempt("Removing temporary files"):
        for file in glob.glob("*.tmp"):
            os.remove(file)

    """

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
    """Convert JSON contents from pytest-json output format to Mig3 submission format.

    Parameters
    ----------
    report : dict
        Report contents, expects caller to parse JSON document into python dict before passing.

    """

    def __init__(self, report):
        self.report = report

    def _tests(self):
        for test_document in self.report["included"]:
            module, test = test_document["attributes"]["name"].split("::")
            yield {"module": module, "test": test, "outcome": test_document["attributes"]["outcome"]}

    def convert(self):
        """Convert the pytest-json tests objects into Mig3 objects."""
        return [test for test in self._tests()]


class JobSubmissionBuilder(object):
    """Build the job submission for Mig3.

    Parameters
    ----------
    target : str
        Target configuration ID
    test_data : list
        Test results to submit to Mig3 service. Generally the result of `ReportConverter.convert()`.

    """

    def __init__(self, target, number, test_data):
        self.target = target
        self.number = number
        self.test_data = test_data

    def _get_version_info(self):
        repository = git.Repo(search_parent_directories=True)
        return {"author": repository.head.object.author.email, "hash": repository.head.object.hexsha}

    def build(self):
        return {
            "version": self._get_version_info(),
            "tests": self.test_data,
            "target": self.target,
            "number": self.number,
            "mig3_client": __version__,
        }


@click.command()
@click.option("-t", "--target", required=True, help="Target ID (from Mig3 service).")
@click.option("-b", "--build", required=True, help="Unique job, task, workflow, build, &c number.")
@click.option("--endpoint", required=True, help="Mig3 build submission endpoint.")
@click.option("--token", required=True, help="Mig3 builder authorization token.")
@click.option("--report", default=".report.json", type=click.File(), help="Specify the pytest-json report filename.")
@click.option("-n", "--dry-run", is_flag=True, help="Show report on stdout instead of submitting it to Mig3 service.")
@click.version_option(__version__)
def mig3(target, build, endpoint, token, report, dry_run):
    """Validate test results with mig3 service.

    Run this command after running py.test with json results enabled to validate the test outcome:
        py.test --json=.report.json

    The following environment variables can be used in lieu of passing options: MIG3_TARGET, MIG3_ENDPOINT, MIG3_TOKEN

    """
    with log_attempt("Reading report"):
        report_json = json.loads(report.read())

    with log_attempt("Converting test data"):
        test_data = ReportConverter(report_json).convert()

    with log_attempt("Building submission"):
        submission = JobSubmissionBuilder(target, build, test_data).build()

    if dry_run:
        json.dump(submission, sys.stdout, indent=2)
    else:
        with log_attempt("Sending submission"):
            headers = {"Authorization": "Bearer {token}".format(**locals())}
            response = requests.post(endpoint, json=submission, headers=headers)
            if response.status_code != 201:
                if response.status_code == 409:
                    raise Regression(response.content)
                else:
                    raise RequestError(response.content)


if __name__ == "__main__":
    mig3(auto_envvar_prefix="MIG3")
