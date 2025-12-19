import argparse
from datetime import datetime

__all__ = ["runner"]


def main(opts: argparse.Namespace) -> None:
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    upgrade_datetime = datetime.strptime(opts.upgrade_date, "%Y-%m-%d")

    upgrade_site = None
    if opts.tucson:
        upgrade_site = "Tucson test stand"
    if opts.base:
        upgrade_site = "Base test stand"
    if opts.summit:
        upgrade_site = "Summit"

    announcement = [
        f"Hi all: On {upgrade_datetime.strftime('%A, %B %d')} at {opts.upgrade_time} CLT,"
    ]
    announcement.append(
        f" the Kafka brokers at the {upgrade_site} will restart, due to a scheduled TLS certificate renewal."
        f" Note that the specified time may vary slightly, depending on when the system picks up the change."
        f" After rollout starts, the Control System components will lose heartbeats."
        f" The system should recover on its own within 20 to 40 minutes."
    )
    print("".join(announcement))


def runner() -> None:

    parser = argparse.ArgumentParser()
    site_group = parser.add_mutually_exclusive_group()
    site_group.add_argument(
        "-s", "--summit", action="store_true", help="Choose the summit for deployment."
    )
    site_group.add_argument(
        "-t",
        "--tucson",
        action="store_true",
        help="Choose the Tucson test stand for deployment.",
    )
    site_group.add_argument(
        "-b",
        "--base",
        action="store_true",
        help="Choose the Base test stand for deployment.",
    )
    parser.add_argument(
        "upgrade_date", help="The date of the deployment in YYYY-mm-dd format."
    )
    parser.add_argument(
        "upgrade_time", help="The local time of the deployment in HH:MM format."
    )

    args = parser.parse_args()

    main(args)
