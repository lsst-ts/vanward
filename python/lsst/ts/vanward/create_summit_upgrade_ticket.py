"""Script to create summit upgrade ticket.

Attributes
----------
INPUT_FORMAT : `str`
    The expected format for the date of the summit upgrade.
INPUT_FORMAT_PLAIN : `str`
    The expected formate for the date spelled out in letters.
SUMMIT_COMPONENTS : `list` of `str`
    The Jira components to add to the ticket.
DISCIPLINES : `list` of `str`
    The disciplines needed to carry out the upgrade.
"""
import argparse
import pathlib
from datetime import datetime

from jira import JIRA

from . import ticket_helpers

INPUT_FORMAT = "%Y-%m-%d"
INPUT_FORMAT_PLAIN = "YYYY-mm-dd"
SUMMIT_COMPONENTS = ["AuxTel", "ComCam", "SIT-COM", "Software Updates"]
DISCIPLINES = ["Software"]

__all__ = "runner"


def valid_date(s: str) -> None:
    """Check the validity of the date format.

    Parameters
    ----------
    s : `str`
        The date string to format check.
    """
    try:
        datetime.strptime(s, INPUT_FORMAT)
    except ValueError:
        msg = f"Not a valid format. Expected {INPUT_FORMAT_PLAIN}"
        raise argparse.ArgumentTypeError(msg)


def main(opts: argparse.Namespace) -> None:
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    jira_auth = ticket_helpers.get_jira_credentials(opts.token_file)
    js = JIRA(server=ticket_helpers.JIRA_SERVER, basic_auth=jira_auth)

    summary = f"Control System Cycle {opts.cycle_number} Upgrade"

    issue = js.create_issue(
        project={"key": "SUMMIT"},
        issuetype={"name": "Task"},
        assignee={"name": opts.assignee},
        summary=summary,
        priority={"name": "SUMMIT-1"},
        components=[{"name": v} for v in SUMMIT_COMPONENTS],
        customfield_11303=opts.upgrade_date,
        customfield_11304=opts.upgrade_date,
        customfield_14811=[{"value": v} for v in DISCIPLINES],
    )

    print(f"{issue.key}")


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
        "-a",
        "--assignee",
        type=str,
        default="mareuter",
        help="Set the assignee with a Jira username.",
    )

    parser.add_argument(
        "cycle_number", type=int, help="The cycle number to create tickets for."
    )

    parser.add_argument(
        "upgrade_date",
        type=valid_date,
        help=f"The date in {INPUT_FORMAT_PLAIN} format for the cycle upgrade.",
    )

    args = parser.parse_args()

    main(args)
