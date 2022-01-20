#!/usr/bin/env python

"""Script to check the current cycle versions of TSSW software against the
conda repository.

Attributes
----------
CYCLE_REPO : `str`
    The name of the cycle build repository.
ENV_FILE : `str`
    The file containing the cycle versions.

Notes
-----
This script requires conda to be installed.
"""

import argparse
import pathlib
from subprocess import run

import json

CYCLE_REPO = "ts_cycle_build"
ENV_FILE = "cycle/cycle.env"


def main(opts):
    """Read the CYCLE env file and look up the specified TSSW packages and
    versions in the conda repository. Finally print a list of the packages and
    the versions that could not be found.

    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """
    sal_version = "0.0"
    xml_version = "0.0"
    packages_not_found = {}
    packages_to_skip = [
        "ts-xml",
        "ts-sal",
        "ts-idl-git",
        "ts-dds-community",
        "ts-dds-community-conda-build",
        "ts-dds-private",
        "ts-dds-private-conda-build",
        "ts-pointing-common",
        "ts-m1m3support",
        "ts-cRIOcpp",
        "ts-mtaos",
        "ts-wep",
        "ts-phosim",
        "ts-observing-utilities",
        "ts-config-atcalsys",
        "ts-config-attcs",
        "ts-config-eas",
        "ts-config-latiss",
        "ts-config-mtcalsys",
        "ts-config-mttcs",
        "ts-config-ocs",
    ]

    with open(opts.cycle_build_dir / CYCLE_REPO / ENV_FILE) as c:
        lines = c.readlines()

    print("Searching TSSW conda packages. Please be patient. This may take a while.")
    for line in lines:
        line = line.strip()
        if line[0:3] == "ts_":
            line = line.replace("_", "-").replace("=", "==")
            items = line.split("==")
            if "ts-xml==" in line:
                xml_version = items[1]
            if "ts-sal==" in line:
                sal_version = items[1]
            if "ts-idl==" in line:
                line = line + f"_{xml_version}" + f"_{sal_version}"
            if "ts-ATMCSSimulator==" in line:
                line = line.replace("ts-ATMCSSimulator", "ts-atmcs-simulator")
                items[0] = items[0].replace("ts-ATMCSSimulator", "ts-atmcs-simulator")

            if items[0] not in packages_to_skip:
                proc = run(
                    [
                        "conda",
                        "search",
                        "--json",
                        "-c",
                        "lsstts",
                        "--platform",
                        "linux-64",
                        f"{line}",
                    ],
                    text=True,
                    capture_output=True,
                )
                conda_info = json.loads(proc.stdout)
                if not items[0].lower() in conda_info:
                    packages_not_found[line] = conda_info

    if len(packages_not_found):
        print("Didn't find these packages and versions:")
        print([key for key in packages_not_found.keys()])
    else:
        print("Done. All packages were found with the provided version.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Make script more verbose."
    )

    parser.add_argument(
        "cycle_build_dir",
        type=pathlib.Path,
        help=f"Path to where the {CYCLE_REPO} directory lives.",
    )

    args = parser.parse_args()

    main(args)
