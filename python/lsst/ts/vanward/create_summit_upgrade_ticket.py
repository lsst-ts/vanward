"""Script to create summit upgrade ticket.

Attributes
----------
INPUT_DATE_FORMAT : `str`
    The expected format for the date of the summit upgrade.
INPUT_DATE_FORMAT_PLAIN : `str`
    The expected format for the date spelled out in letters.
SUMMIT_COMPONENTS : `list` of `str`
    The Jira components to add to the ticket.
DISCIPLINES : `list` of `str`
    The disciplines needed to carry out the upgrade.
LABELS : `list` of `str`
    The labels to annotate the ticket with.
"""

import argparse
import os
import pathlib
import re
from datetime import datetime, time

from jira import JIRA

from . import ticket_helpers

INPUT_DATE_FORMAT = "%Y-%m-%d"
INPUT_DATE_FORMAT_PLAIN = "YYYY-mm-dd"
INPUT_TIME_FORMAT_PLAIN = "HH:MM"
SUMMIT_COMPONENTS = ["AuxTel", "ComCam", "SIT-COM", "Software Updates"]
DISCIPLINES = ["Software"]
LABELS = ["SoftwareRelease"]

__all__ = "runner"


def valid_date(s: str) -> str:
    """Check the validity of the date format.

    Parameters
    ----------
    s : `str`
        The date string to format check.

    Returns
    -------
    `str`
        The original string if it passed the formatting check.
    """
    try:
        datetime.strptime(s, INPUT_DATE_FORMAT)
        return s
    except ValueError:
        msg = f"Not a valid format. Expected {INPUT_DATE_FORMAT_PLAIN}"
        raise argparse.ArgumentTypeError(msg)


def valid_time(t: str) -> str:
    """Check the validity of the time format.

    Parameters
    ----------
    t : `str`
        The time string to format check.

    Returns
    -------
    `str`
        The original string if it passed the formatting check.
    """
    try:
        time.fromisoformat(t)
        return t
    except ValueError:
        msg = f"Not a valid format. Expected {INPUT_TIME_FORMAT_PLAIN}"
        raise argparse.ArgumentTypeError(msg)


def valid_version(v: str) -> str:
    """Check the validity of the version format.

    Parameters
    ----------
    v : `str`
        The version string to format check.

    Returns
    -------
    `str`
        The original string if it passed the formatting check.
    """
    version = re.compile(r"\d+\.\d+\.?\d*")
    result = version.match(v)
    if result is None:
        msg = "Not a valid format. Expected X.Y[.Z]"
        raise argparse.ArgumentTypeError(msg)
    else:
        return v


def parse_cscs(cscs: str) -> str:
    """Parse the CSCs from a comma-delimited string.

    Parameters
    ----------
    cscs : `str`
        The comma-delimited string of CSCs.

    Returns
    -------
    `str`
        A formatted string of CSC names.
    """
    if cscs != "":
        items = cscs.split(",")
        if len(items) == 1:
            return f" and {items[0]}"
        else:
            return f", {', '.join(items[:-1])} and {items[-1]}"
    else:
        msg = "Must specify at least one CSC for an incremental upgrade."
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

    revision = opts.revision
    if revision == 0:
        summary = f"Control System Cycle {opts.cycle_number} Upgrade"
        cycle_text = f"Control Software (Cycle {opts.cycle_number})"
        description = [
            f"Upgrade of {cycle_text} and XML ({opts.xml_version}) on the summit.",
            f"To occur at {opts.start_time} CLT - all systems will be unusable at this time.",
        ]
    elif revision > 0:
        summary = (
            f"Incremental XML Upgrade (Cycle {opts.cycle_number} Revision {revision})"
        )
        cycle_text = f"ScriptQueues{parse_cscs(opts.cscs)}"
        description = [
            f"Upgrade of {cycle_text} for XML ({opts.xml_version}) on the summit.",
            f"To occur at {opts.start_time} CLT.",
        ]
    else:
        msg = "Not a valid revision number. Must be 0 or greater."
        raise argparse.ArgumentTypeError(msg)

    assignee = ticket_helpers.get_user_ids(opts.assignee, js)
    task_participants = ticket_helpers.get_user_ids(opts.task_participants, js)
    issue = js.create_issue(
        project={"key": "SUMMIT"},
        issuetype={"name": "Task"},
        assignee={"id": assignee},
        summary=summary,
        description=(os.linesep * 2).join(description),
        labels=LABELS,
        priority={"name": "SUMMIT-1"},
        components=[{"name": v} for v in SUMMIT_COMPONENTS],
        # Start date
        customfield_10059=opts.upgrade_date,
        # End date
        customfield_10061=opts.upgrade_date,
        # Task or Event Participants
        customfield_10151=[{"id": n} for n in task_participants],
        # Discipline
        customfield_10141=[{"value": v} for v in DISCIPLINES],
    )

    print(f"{issue.key}")


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
        default="mreuter",
        help="Set the assignee with a Jira username.",
    )

    parser.add_argument(
        "--task-participants",
        type=str,
        default="mreuter,rbovill,aibsen",
        help="A comma-delimited string of Jira usernames for the participants involved in the deployment.",
    )

    parser.add_argument(
        "-s",
        "--start-time",
        type=valid_time,
        default="09:00",
        help=f"The time the deployment is to begin. \
               Always refers to CLT and in {INPUT_TIME_FORMAT_PLAIN} format.",
    )

    parser.add_argument(
        "-r",
        "--revision",
        type=int,
        default=0,
        help="The revision within the cycle. If 0, the ticket will be for a full upgrade, \
            otherwise it will be for an incremental upgrade.",
    )

    parser.add_argument(
        "--cscs",
        type=str,
        default="",
        help="A comma-delimited string of CSCs affected. Only relevant for incremental upgrades.",
    )

    parser.add_argument(
        "cycle_number", type=int, help="The cycle number to create upgrade ticket for."
    )

    parser.add_argument(
        "xml_version",
        help="The XML version being deployed in X.Y[.Z] format.",
    )

    parser.add_argument(
        "upgrade_date",
        help=f"The date in {INPUT_DATE_FORMAT_PLAIN} format for the cycle upgrade.",
    )

    args = parser.parse_args()

    main(args)
