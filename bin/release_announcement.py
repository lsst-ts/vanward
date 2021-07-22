#!/usr/bin/env python
import argparse
from datetime import datetime


def main(opts):
    """
    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    if opts.ncsa or opts.tucson:
        upgrade_timezone = "Project Time"
    else:
        upgrade_timezone = "Summit Time"

    upgrade_datetime = datetime.strptime(opts.upgrade_date, "%Y-%m-%d")

    upgrade_site = None
    if opts.ncsa:
        upgrade_site = "NCSA teststand"
    if opts.tucson:
        upgrade_site = "Tucson teststand"
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
    if opts.ncsa:
        announcement.append(
            f" When the deployment is complete, I have the entire test stand until {opts.int_test_time}"
        )
        announcement.append(" to perform my integration stress testing.")
    announcement.append(
        " Nublado users: You have until the deployment start time to log out of your nublado instances."
    )
    announcement.append(
        " After that, at the point the system is shutdown, you will be kicked out of your instance."
    )
    announcement.append(" So, please save your work and log out.")

    print("".join(announcement))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    site_group = parser.add_mutually_exclusive_group()
    site_group.add_argument(
        "-s", "--summit", action="store_true", help="Choose the summit for deployment."
    )
    site_group.add_argument(
        "-n",
        "--ncsa",
        action="store_true",
        help="Choose the NCSA teststand for deployment.",
    )
    site_group.add_argument(
        "-t",
        "--tucson",
        action="store_true",
        help="Choose the Tucson teststand for deployment.",
    )

    parser.add_argument(
        "--int-test-time", help="The date/time when integration testing will end."
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
