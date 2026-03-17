"""Script to create site configuration Jira tickets.

Attributes
----------
SITE_LIST : `list`
    List of sites for ticket summary.
JIRA_TEAM : `str`
    The Jira team for the configuration tickets.
"""

import argparse
import pathlib

from jira import JIRA

from . import ticket_helpers

SITE_LIST = ["Tucson test stand", "Base test stand", "summit"]
JIRA_TEAM = "Deployment"

__all__ = ["runner"]


def main(opts: argparse.Namespace) -> None:
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    jira_auth = ticket_helpers.get_jira_credentials(opts.token_file)
    js = JIRA(server=ticket_helpers.JIRA_SERVER, basic_auth=jira_auth)

    release_name = f"ts_xml {opts.release}"
    release_description = ""
    if opts.cycle:
        release_description = f"for Cycle {opts.cycle}"
        if opts.revision:
            release_description += f" revision {opts.revision}"

    js.create_version(
        name=release_name,
        project="CAP",
        description=release_description,
    )
    print(f"Created release '{release_name}' in CAP project.")

    issue_fields = dict(
        project={"key": "CAP"},
        issuetype={"name": "Story"},
        summary=f"Catch all ticket for OSW work for XML {opts.release}",
        fixVersions=[{"name": release_name}],
        components=[{"name": "None"}],
    )

    if opts.assignee:
        assignee = ticket_helpers.get_user_ids(opts.assignee, js)
        issue_fields["assignee"] = {"id": assignee}

    issue = js.create_issue(**issue_fields)
    print(f"Created ticket {issue.key}: {issue.fields.summary}")


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--token-file",
        type=pathlib.Path,
        default="~/.auth/jira",
        help="Specify path to Jira credentials file.",
    )

    parser.add_argument(
        "release",
        type=str,
        help="The version of the ts_xml release.",
    )

    parser.add_argument(
        "-c",
        "--cycle",
        type=int,
        default=None,
        help="The cycle number to create the release for.",
    )

    parser.add_argument(
        "-r",
        "--revision",
        type=int,
        default=None,
        help="The revision for the cycle, relevant for incremental upgrades.",
    )

    parser.add_argument(
        "-a",
        "--assignee",
        type=str,
        default="aibsen@lsst.org",
        help="The assignee for the catch-all ticket. Default: aibsen@lsst.org.",
    )

    args = parser.parse_args()

    main(args)
