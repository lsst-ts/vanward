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
    if opts.tucson or opts.base:
        upgrade_timezone = "Project Time"
    else:
        upgrade_timezone = "Summit Time"

    upgrade_datetime = datetime.strptime(opts.upgrade_date, "%Y-%m-%d")

    upgrade_site = None
    if opts.tucson:
        upgrade_site = "Tucson test stand"
    if opts.base:
        upgrade_site = "Base test stand"
    if opts.summit:
        upgrade_site = "summit"

    announcement = [f"Hi all: On {upgrade_datetime.strftime('%A, %B %d')},"]
    announcement.append(
        f" we will be deploying Cycle {opts.upgrade_cycle} to the {upgrade_site}"
    )
    if opts.summit:
        announcement.append(" for the production domain.")
    else:
        announcement.append(".")
    announcement.append(
        f" The deployment will begin at {opts.upgrade_time} {upgrade_timezone}."
    )
    announcement.append(
        " Once the minimal system is up, another announcement will be made so that all"
    )
    announcement.append(" services can be brought up.")
    if not opts.summit:
        if opts.system_ready_time is not None and opts.int_test_time is not None:
            system_ready_datetime = datetime.strptime(
                opts.system_ready_time, "%Y-%m-%dT%H:%M"
            )
            int_test_datetime = datetime.strptime(opts.int_test_time, "%Y-%m-%dT%H:%M")

            announcement.append(" All systems must be ready for integration testing by")
            announcement.append(
                f" {system_ready_datetime.strftime('%A, %B %d at %H:%M')} {upgrade_timezone}."
            )
            announcement.append(
                " Once the systems are ready, the integration testing team has the entire test stand until"
            )
            announcement.append(
                f" {int_test_datetime.strftime('%A, %B %d at %H:%M')} {upgrade_timezone}"
            )
            announcement.append(" to perform the integration stress testing.")
    announcement.append(
        " Nublado users: You have until the deployment start time to log out of your nublado instances."
    )
    announcement.append(
        " After that, at the point the system is shutdown, you will be kicked out of your instance."
    )
    announcement.append(" So, please save your work and log out.")

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
        "--system-ready-time",
        help="The date/time (YYYY-mm-ddTHH:MM) when the system must be ready for testing.",
    )

    parser.add_argument(
        "--int-test-time",
        help="The date/time (YYYY-mm-ddTHH:MM) when integration testing will end.",
    )

    parser.add_argument(
        "upgrade_date", help="The date of the deployment in YYYY-mm-dd format."
    )
    parser.add_argument(
        "upgrade_time", help="The local time of the deployment in HH:MM format."
    )
    parser.add_argument("upgrade_cycle", help="The cycle number for the deployment.")

    args = parser.parse_args()

    main(args)
