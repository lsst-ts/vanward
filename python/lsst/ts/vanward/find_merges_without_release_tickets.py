"""Script to compare release Jira tickets with merged XML branches.

Attributes
----------
XML_DIR : `str`
    The name of the XML repository.
"""
import argparse
import os
import pathlib

import git
from jira import JIRA

from . import ticket_helpers

XML_DIR = "ts_xml"

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

    xml_version = f"{XML_DIR} {opts.xml_version}"

    query = f'project = CAP AND fixVersion = "{xml_version}"'
    issues = js.search_issues(query)
    # print(f"Number of issues: {len(issues)}")
    release_tickets = []
    for issue in issues:
        release_tickets.append(issue.key)
        more_tickets = ticket_helpers.get_linked_tickets(issue, js)
        if more_tickets:
            for ticket in more_tickets:
                release_tickets.append(ticket.key)

    xml_repo = git.Repo(opts.xml_dir / XML_DIR)
    gitc = xml_repo.git
    commits = gitc.log(
        "--merges", "--pretty=oneline", f"{opts.previous_xml_version}...HEAD"
    ).split(os.linesep)
    short_version = opts.previous_xml_version[:-2]
    merge_tickets = []
    for commit in commits:
        branch = commit.split()[-1]
        if opts.xml_version in branch or short_version in branch:
            break
        ticket = branch.split("/")[-1]
        if (
            ticket.startswith("DM")
            or ticket.startswith("CAP")
            or ticket.startswith("TPC")
        ):
            if len(ticket.split("-")) == 2:
                merge_tickets.append(ticket)

    # print(release_tickets)
    # print(merge_tickets)

    print("Missing tickets:")
    missing = 0
    for ticket in merge_tickets:
        if ticket not in release_tickets:
            print(ticket)
            missing += 1
    if not missing:
        print("No missing tickets.")


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--token-file",
        type=pathlib.Path,
        default="~/.jira_auth",
        help="Specify path to Jira credentials file.",
    )

    parser.add_argument(
        "xml_dir",
        type=pathlib.Path,
        help=f"Path to where the {XML_DIR} directory lives.",
    )
    parser.add_argument(
        "xml_version",
        type=str,
        help="Provide the Jira XML version to check. NOTE: Only the numeric part of the label is required.",
    )

    parser.add_argument(
        "previous_xml_version", help="Provide the previous Git XML version."
    )

    args = parser.parse_args()

    main(args)
