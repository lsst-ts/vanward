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
JIRA_TEAM = "Telescope and Site"

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

    for site in SITE_LIST:
        summary = f"Ready {site} deployment configuration for Cycle {opts.cycle_number}"

        issue = js.create_issue(
            project={"key": "DM"},
            issuetype={"name": "Story"},
            summary=summary,
            assignee={"name": opts.assignee},
            components=[{"name": "ts_deployment"}],
            # RubinTeam
            customfield_10056={"value": JIRA_TEAM},
        )

        print(f"{site}: {issue.key}")


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
        "-a",
        "--assignee",
        type=str,
        default="mreuter@lsst.org",
        help="Set the assignee with a Jira username.",
    )

    parser.add_argument(
        "cycle_number", type=int, help="The cycle number to create tickets for."
    )

    args = parser.parse_args()

    main(args)
