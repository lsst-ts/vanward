"""Script to move bucket ticket links from one Jira ticket to another.
"""
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

    current = js.issue(opts.current_ticket)
    keep_ticket_keys = opts.keep_tickets.split(",")

    links = current.fields.issuelinks
    move_links = []
    for link in links:
        link_key = ticket_helpers.get_link_key(link)
        if link_key not in keep_ticket_keys:
            move_links.append(link)

    for move_link in move_links:
        link_key = ticket_helpers.get_link_key(move_link)
        js.create_issue_link(move_link.type, opts.next_ticket, link_key)
        js.delete_issue_link(move_link.id)


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "current_ticket",
        type=str,
        help="The Jira key of the current version's bucket ticket.",
    )

    parser.add_argument(
        "next_ticket",
        type=str,
        help="The Jira key of the next version's bucket ticket.",
    )

    parser.add_argument(
        "keep_tickets",
        type=str,
        help="A comma-delimited list of Jira tickets to keep on the current version's bucket ticket.",
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
