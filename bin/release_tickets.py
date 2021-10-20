#!/usr/bin/env python
"""Script to check on Jira tickets associated with a given XML release.

Attributes
----------
CLOSED_TICKET_STATUS : `list`
    The acceptable states for closed Jira tickets.
"""
import argparse
import pathlib

from jira import JIRA

import lsst.ts.vanward.ticket_helpers as ticket_helpers

CLOSED_TICKET_STATUS = ["Done", "Won't Fix", "Invalid", "Resolved"]


def main(opts):
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    jira_auth = ticket_helpers.get_jira_credentials(opts.token_file)
    js = JIRA(server=ticket_helpers.JIRA_SERVER, basic_auth=jira_auth)

    xml_version = f"ts_xml {opts.xml_version}"

    query = f'project = CAP AND fixVersion = "{xml_version}"'
    issues = js.search_issues(query)
    print(f"Number of issues: {len(issues)}")
    for issue in issues:
        print(f"{issue.key} ({issue.fields.assignee}): {issue.fields.status}")
        more_tickets = ticket_helpers.get_linked_tickets(issue, js)
        if more_tickets:
            for ticket in more_tickets:
                if f"{ticket.fields.status}" not in CLOSED_TICKET_STATUS:
                    xmldone = "xmldone" in ticket.fields.labels
                else:
                    xmldone = True
                if xmldone:
                    donechar = "\u2713"
                else:
                    donechar = "\u2717"
                print(
                    f" * {ticket} ({ticket.fields.assignee}): {ticket.fields.status} ({donechar})"
                )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--token-file",
        type=pathlib.Path,
        default="~/.jira_auth",
        help="Specify path to Jira credentials file.",
    )

    parser.add_argument(
        "xml_version", type=str, help="Provide the XML version to check."
    )

    args = parser.parse_args()

    main(args)
