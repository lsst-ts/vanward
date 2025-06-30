"""Script to find tickets in bucket ticket related to XML
chaneges for specific components."""

import argparse
import os
import pathlib

import git
from jira import JIRA

from . import ticket_helpers

XML_DIR = "ts_xml"

__all__ = ["runner"]


def fetch_remote_branch(repo: git.Repo, branch: str) -> bool:
    """Fetch a single branch from origin. Returns True if branch exists.

    Parameters
    ----------
    repo : `git.Repo`
        The git Repo object for ts_xml.

    Returns
    -------
    `bool`
        True if the branch exists on the remote, False otherwise.
    """
    remote_ref = f"origin/{branch}"
    try:
        repo.remotes.origin.fetch(f"{branch}:{remote_ref}")
        return True
    except Exception:
        return False


def extract_ticket_key(message: str) -> str:
    """Extract the ticket key from a merge pull request commit message.

    Parameters
    ----------
    str : `message`
        The git commit message.

    Returns
    -------
    `str`
        The name of the jira ticket.
    """
    return message.split(os.linesep)[0].split("/")[-1]


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

    xml_repo = git.Repo(opts.xml_dir / XML_DIR)
    components = {c.strip().lower() for c in opts.components.split(",")}
    linked_tickets = ticket_helpers.get_linked_tickets(current, js)
    merge_commits = set()

    # get all merge commits from the previous XML version to develop
    for commit in xml_repo.iter_commits(
        f"{opts.previous_xml_version}..develop",
        merges=True,
    ):
        merge_commits.add(commit)
        branch_name = f"tickets/{extract_ticket_key(commit.message)}"
        # if the branches merged into develop have other branches merged
        # into them, check them too
        try:
            if fetch_remote_branch(xml_repo, branch_name):
                for child_commit in xml_repo.iter_commits(
                    f"{opts.previous_xml_version}..{branch_name}",
                    merges=True,
                ):
                    merge_commits.add(child_commit)
        except Exception:
            continue

    relevant_commits = []
    # check if the files changed relate to the components
    for commit in merge_commits:
        for file in commit.stats.files.keys():
            file_lower = file.lower()
            if any(comp in file_lower for comp in components):
                relevant_commits.append(commit)
                break

    relevant_commits_keys = {
        extract_ticket_key(commit.message) for commit in relevant_commits
    }
    # keep tickets that are linked to the relevant commits
    # or have components in their summary
    tickets_to_keep = []
    for ticket in linked_tickets:
        ticket_summary = ticket.fields.summary.lower()
        if any(ticket.key in commit for commit in relevant_commits_keys) or any(
            comp in ticket_summary for comp in components
        ):
            tickets_to_keep.append(ticket)

    tickets_to_keep_keys = [ticket.key for ticket in tickets_to_keep]
    print(",".join(tickets_to_keep_keys))


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "current_ticket",
        type=str,
        help="The Jira key of the current version's bucket ticket.",
    )

    parser.add_argument(
        "xml_dir",
        type=pathlib.Path,
        help=f"Path to where the {XML_DIR} directory lives.",
    )

    parser.add_argument(
        "components",
        type=str,
        help="A comma-delimited list of CSC components considered in an incremental upgrade.",
    )

    parser.add_argument(
        "previous_xml_version", help="Provide the previous Git XML version."
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
