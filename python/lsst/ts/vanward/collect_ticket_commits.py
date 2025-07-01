"""Script to find commit sha hashes for Jira tickets."""

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


def confirm_tickets_in_bucket(
    current: object, ticket_list: list[str], js: JIRA
) -> tuple:
    """Confirm that the provided tickets are in the current bucket ticket.

    Parameters
    ----------
    current : `object`
        The current bucket ticket object.
    ticket_list : `list[str]`
        A list of Jira ticket keys.
    js : `JIRA`
        The JIRA client instance.

    Returns
    -------
    tuple
        A tuple containing a list of linked tickets
        and a list of not found tickets.
    """
    linked_tickets = ticket_helpers.get_linked_tickets(current, js)
    linked_ticket_keys = {ticket.key for ticket in linked_tickets}
    found_tickets = []
    not_found = []

    for ticket in ticket_list:
        if ticket in linked_ticket_keys:
            found_tickets.append(js.issue(ticket))
        else:
            not_found.append(ticket)

    return found_tickets, not_found


def get_merge_commits(xml_repo: git.Repo, previous_xml_version: str) -> set[git.Commit]:
    """Get all merge commits from the previous XML version to develop.

    Parameters
    ----------
    xml_repo : `git.Repo`
        The git Repo object for ts_xml.
    previous_xml_version : `str`
        The previous XML version tag.

    Returns
    -------
    set
        A set of git.Commits objects.
    """
    merge_commits = set()

    # get all merge commits from the previous XML version to develop
    for commit in xml_repo.iter_commits(
        f"{previous_xml_version}..develop",
        merges=True,
    ):
        merge_commits.add(commit)
        branch_name = f"tickets/{extract_ticket_key(commit.message)}"
        # if the branches merged into develop have other branches merged
        # into them, check them too
        try:
            if branch_name in xml_repo.refs or fetch_remote_branch(
                xml_repo, branch_name
            ):
                for child_commit in xml_repo.iter_commits(
                    f"{previous_xml_version}..{branch_name}",
                    merges=True,
                ):
                    merge_commits.add(child_commit)
        except Exception:
            continue
    return merge_commits


def match_commits_to_tickets(
    merge_commits: set[git.Commit], linked_tickets_keys: set[str]
) -> tuple[list[git.Commit], set[str]]:
    """Match commits to tickets.

    Parameters
    ----------
    merge_commits : `set`
        A set of merge commits.
    linked_tickets_keys : `set`
        A set of linked Jira ticket keys.

    Returns
    -------
    tuple
        A tuple containing a list of relevant commits
        and a set of ticket keys with commits.
    """
    relevant_commits = []
    tickets_with_commits = set()

    for commit in merge_commits:
        commit_key = extract_ticket_key(commit.message)
        for ticket_key in linked_tickets_keys:
            if ticket_key in commit_key:
                tickets_with_commits.add(ticket_key)
                relevant_commits.append(commit)

    return relevant_commits, tickets_with_commits


def main(opts: argparse.Namespace) -> None:
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    jira_auth = ticket_helpers.get_jira_credentials(opts.token_file)
    js = JIRA(server=ticket_helpers.JIRA_SERVER, basic_auth=jira_auth)
    current = js.issue(opts.current_bucket_ticket)

    # Check that the provided tickets are in the current bucket ticket
    ticket_list = opts.tickets.split(",")
    linked_tickets, not_found = confirm_tickets_in_bucket(current, ticket_list, js)

    xml_repo = git.Repo(opts.xml_dir / XML_DIR)
    # get all merge commits from the previous XML version to develop
    # and the ones merged into them
    merge_commits = get_merge_commits(xml_repo, opts.previous_xml_version)

    # get the keys of the linked tickets
    linked_tickets_keys = {ticket.key for ticket in linked_tickets}

    # match commits to ticket
    relevant_commits, tickets_with_commits = match_commits_to_tickets(
        merge_commits, linked_tickets_keys
    )

    tickets_with_no_commits = linked_tickets_keys - tickets_with_commits

    if not_found:
        print(
            f"The following tickets were not found in the bucket ticket: {', '.join(not_found)}"
        )

    if tickets_with_no_commits:
        print(
            f"No commits found for the following tickets: {', '.join(tickets_with_no_commits)}"
        )

    print("Found commits for the following tickets:")
    for relevant_commit in relevant_commits:
        print(
            f"{extract_ticket_key(relevant_commit.message)}: {relevant_commit.hexsha}"
        )


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "current_bucket_ticket",
        type=str,
        help="The Jira key of the current version's bucket ticket.",
    )

    parser.add_argument(
        "tickets", help="A comma separated list of tickets to get commits from."
    )

    parser.add_argument(
        "xml_dir",
        type=pathlib.Path,
        help=f"Path to where the {XML_DIR} directory lives.",
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
