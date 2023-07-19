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
    cycle_text = f"Control Software (Cycle {opts.cycle_number})"
    description = [
        f"Upgrade of {cycle_text} and XML ({opts.xml_version}) on the summit.",
        f"To occur at {opts.start_time} CLT - all systems will be unusable at this time.",
    ]

    issue = js.create_issue(
        project={"key": "SUMMIT"},
        issuetype={"name": "Task"},
        assignee={"name": opts.assignee},
        summary=summary,
        description=(os.linesep * 2).join(description),
        labels=LABELS,
        priority={"name": "SUMMIT-1"},
        components=[{"name": v} for v in SUMMIT_COMPONENTS],
        customfield_11303=opts.upgrade_date,
        customfield_11304=opts.upgrade_date,
        customfield_14707=[{"name": n} for n in opts.task_participants.split(",")],
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
        "--task-participants",
        type=str,
        default="mareuter,rbovill",
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
