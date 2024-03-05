"""Ticket scripts helpers.

Attributes
----------
JIRA_SERVER : `str`
    The URL for the RubinObs project Jira server.
"""
import pathlib

import jira

__all__ = ["get_jira_credentials", "get_linked_tickets", "get_user_ids", "JIRA_SERVER"]


JIRA_SERVER = "https://rubinobs.atlassian.net/"


def get_jira_credentials(token_file: pathlib.Path) -> tuple[str, str]:
    """Get Jira authentication credentials from a file.

    Parameters
    ----------
    token_file : `path.Pathlib`
        The full path of the Jira credentials file.

    Returns
    -------
    `tuple`
        The username and password for authentication as a tuple.
    """
    with open(token_file.expanduser(), "r") as fd:
        uname = fd.readline().strip()  # Can't hurt to be paranoid
        pwd = fd.readline().strip()
    return (uname, pwd)


def get_linked_tickets(
    issue: jira.resources.Issue, server: jira.client.JIRA
) -> list[jira.resources.Issue]:
    """Get ticket links from a specific ticket.

    Parameters
    ----------
    issue : `jira.resources.Issue`
        The Jira ticket to get a list of potential links from.
    server : `jira.client.JIRA`
        The Jira server instance.

    Returns
    -------
    `list`
        The potential list of issue links for the given ticket.
    """
    linked_tickets = []
    links = issue.fields.issuelinks
    for link in links:
        # print(dir(link))
        if link.type.outward == "is triggering":
            continue
        try:
            linked_tickets.append(server.issue(link.inwardIssue.key))
        except AttributeError:
            linked_tickets.append(server.issue(link.outwardIssue.key))
    return linked_tickets


def get_user_ids(users: str, server: jira.client.JIRA) -> str | list[str]:
    """Get Jira user Ids from names.

    Parameters
    ----------
    users : `str`
        The name or names of users to get Ids for. Multiple users should be
        specified as a comma-delimited string.
    server : `jira.client.JIRA`
        The Jira server instance.

    Returns
    -------
    user_ids : `str` or `list[str]`
        The resolved Jira Ids for the users.
    """
    ids = server.search_users(query=users)
    if "," in users:
        id = [x.accountId for x in ids]
    else:
        id = ids[0].accountId

    return id
