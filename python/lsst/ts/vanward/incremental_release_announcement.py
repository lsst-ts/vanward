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

    announcement = [f"Hi all: On {upgrade_datetime.strftime('%A, %B %d')},"]
    announcement.append(
        f" we will be deploying an incremental "
        f"upgrade (Cycle {opts.upgrade_cycle} revision {opts.revision}) to the {upgrade_site}"
    )
    if opts.summit:
        announcement.append(" production domain.")
    else:
        announcement.append(".")
    announcement.append(f" The deployment will begin at {opts.upgrade_time} CLT.")
    components_affected_phrase = (
        f" We will be restarting {opts.components} and all the ScriptQueues."
    )

    announcement.append(components_affected_phrase)

    end_phrase = ""

    if not opts.summit:
        end_phrase = f" We will then use {opts.test_sq} and the aforementioned components for testing."
        announcement.append(end_phrase)
    if opts.summit:
        end_phrase = (
            " These components should be in safe state for CSC shutdown and all operations "
            "on the ScriptQueues paused for restart."
        )
        announcement.append(end_phrase)

    print("".join(announcement))
    print()

    hour_announcement = [
        f"Reminder: At {opts.upgrade_time} CLT (in 1 hour) we will be deploying an incremental upgrade "
        f"(Cycle {opts.upgrade_cycle} revision {opts.revision})."
    ]
    hour_announcement.append(components_affected_phrase)
    hour_announcement.append(end_phrase)

    print("".join(hour_announcement))


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
    parser.add_argument("upgrade_cycle", help="The cycle number for the deployment.")
    parser.add_argument(
        "--revision", required=True, help="The revision number for the deployment."
    )
    parser.add_argument(
        "--components",
        required=True,
        type=str,
        help="A comma separated list of the components being upgraded.",
    )
    parser.add_argument(
        "--test_sq",
        default="MTQueue",
        help="The ScriptQueue to be used for testing after deployment (only for non-summit deployments).",
    )

    args = parser.parse_args()

    main(args)
