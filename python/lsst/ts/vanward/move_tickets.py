"""Script to move SSW tickets from one ts_xml fixVersion to the next."""

import argparse
import pathlib

from jira import JIRA

from . import ticket_helpers

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

    xml_version = f"ts_xml {opts.xml_version}"
    next_xml_version = f"ts_xml {opts.next_xml_version}"
    query = f'project = SSW AND fixVersion = "{xml_version}"'
    issues = js.search_issues(query, maxResults=False)
    keep_ticket_keys = opts.keep_tickets.split(",")

    tickets_to_move = []
    for issue in issues:
        if issue.key not in keep_ticket_keys:
            tickets_to_move.append(issue)

    for issue in tickets_to_move:
        print(f"Moving {issue.key} from {xml_version} to {next_xml_version}")
        issue.update(
            update={
                "fixVersions": [
                    {"remove": {"name": xml_version}},
                    {"add": {"name": next_xml_version}},
                ]
            }
        )


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "xml_version", type=str, help="Provide the current XML version."
    )

    parser.add_argument(
        "next_xml_version",
        type=str,
        help="Provide the next XML version to move tickets to.",
    )

    parser.add_argument(
        "keep_tickets",
        type=str,
        help="A comma-delimited list of Jira tickets to keep on the current XML version.",
    )

    parser.add_argument(
        "-t",
        "--token-file",
        type=pathlib.Path,
        default="~/.auth/jira",
        help="Specify path to Jira credentials file.",
    )

    args = parser.parse_args()

    main(args)
