#!/usr/bin/env python
"""Script to check current cycle versions against GitHub repository tags.

Attributes
----------
CYCLE_REPO : `str`
    The name of the cycle build repository.
ENV_FILE : `str`
    The file containing the cycle versions.
GITHUB_GRAPHQL_ENDPOINT : `str`
    The URL for the GitHub GraphQL endpoint.
RECIPES_REPO : `str`
    The name of the conda recipes repository.
"""
import argparse
import os
import pathlib

import gql
import gql.transport.requests
import yaml

import lsst.ts.vanward.check_helpers as check_helpers

CYCLE_REPO = "ts_cycle_build"
RECIPES_REPO = "ts_recipes"
ENV_FILE = "cycle/cycle.env"
GITHUB_GRAPHQL_ENDPOINT = "https://api.github.com/graphql"


def fixup_version(version_str):
    """Remove long names from tags to match conda versioning.

    Parameters
    ----------
    version_str : `str` or None
        The version to potentially fixup.

    Returns
    -------
    `str` or None
        The fixed version.
    """
    if version_str is None:
        return version_str
    fixed_version = version_str.lstrip("v")
    fixed_version = fixed_version.replace(".alpha.", "a")
    fixed_version = fixed_version.replace(".beta.", "b")
    fixed_version = fixed_version.replace(".rc.", "rc")
    return fixed_version


def graphql_query(org_name, cursor=None):
    """Create a GraphQL query for the GitHub API.

    Parameters
    ----------
    org_name : `str`
        The name of the GitHub organization to create the query for.
    cursor : `str`, optional
        The query pagination cursor if there is more than one page of data.

    Returns
    -------
    `gql.gql`
        The GraphQL query to execute.
    """
    if cursor is None:
        repo_str = "repositories(first: 100)"
    else:
        repo_str = f'repositories(first: 100, after: "{cursor}")'

    return gql.gql(
        f"""
        query {{
          rateLimit {{
            cost
            remaining
            resetAt
          }}
          organization(login: "{org_name}") {{
            {repo_str} {{
              pageInfo {{
                startCursor
                hasNextPage
                endCursor
              }}
              edges {{
                node {{
                  name
                  refs(refPrefix: "refs/tags/", last: 1) {{
                    edges {{
                      node {{
                        name
                      }}
                    }}
                  }}
                }}
              }}
            }}
          }}
        }}
        """
    )


def print_rate_limit(info):
    """Helper for printing the API rate limit information.

    Parameters
    ----------
    info : `dict`
        The API rate limit information from the GraphQL query.
    """
    print(
        f"Rate Limit remaining is {info['remaining']} and resets at {info['resetAt']}"
    )


def read_secrets(secret_file):
    """Get the GitHub token associated with the GraphQL queries.

    Parameters
    ----------
    secret_file : `pathlib.Path`
        Description

    Returns
    -------
    `str`
        The token.
    """
    with open(secret_file) as sfile:
        token = sfile.readline()
    return token.strip()


def get_version_from_recipe(recipe_file):
    """Retrieve a version from a conda meta package.

    Parameters
    ----------
    recipe_file : `file` or `pathlib.Path`
        The conda meta package configuration file.

    Returns
    -------
    `str`
        The container meta package version.
    """
    values = yaml.safe_load(recipe_file)
    return values["package"]["version"]


def main(opts):
    """Function that does all the heavy lifting.

    Parameters
    ----------
    opts : `argparse.Namespace`
        The script command-line arguments and options.
    """

    # Gather the cycle build versions
    software_versions = {}
    with open(opts.cycle_build_dir / CYCLE_REPO / ENV_FILE) as ifile:
        for line in ifile.readlines():
            if line.startswith("#"):
                continue
            line = line.strip()
            parts = line.split("=")
            if parts[0] in check_helpers.IGNORE_LIST:
                continue
            software_versions[parts[0]] = check_helpers.SoftwareVersions(parts[1])

    # Construct and call the repository queries
    gh_token = read_secrets(opts.token_file.expanduser())

    header_token = f"Bearer {gh_token}"
    header = {"Authorization": header_token}
    transport = gql.transport.requests.RequestsHTTPTransport(
        GITHUB_GRAPHQL_ENDPOINT, headers=header, retries=3
    )
    client = gql.Client(transport=transport)

    repository_versions = {}
    for organization in check_helpers.ORG_LIST:
        has_next_page = True
        cursor = None
        while has_next_page:
            results = client.execute(graphql_query(organization, cursor))
            if opts.verbose:
                print_rate_limit(results["rateLimit"])
            has_next_page = results["organization"]["repositories"]["pageInfo"][
                "hasNextPage"
            ]
            cursor = results["organization"]["repositories"]["pageInfo"]["endCursor"]
            repos_list = results["organization"]["repositories"]["edges"]
            for repo in repos_list:
                key = repo["node"]["name"]
                try:
                    version = repo["node"]["refs"]["edges"][0]["node"]["name"]
                except IndexError:
                    version = None
                repository_versions[key] = version

    # Add the repository versions to the ones gathered from the cycle build.
    repository_map_keys = list(check_helpers.REPOSITORY_MAP.keys())
    for package in software_versions:
        if package in repository_map_keys:
            repository_name = check_helpers.REPOSITORY_MAP[package]
        else:
            repository_name = package
        try:
            if package == "love_manager":
                software_versions[package].latest = repository_versions[repository_name]
            else:
                software_versions[package].latest = fixup_version(
                    repository_versions[repository_name]
                )
        except KeyError:
            if repository_name not in check_helpers.RECIPES_HANDLING:
                print(f"Cannot find {repository_name} in repository list.")

    for recipe in check_helpers.RECIPES_HANDLING:
        try:
            with open(
                os.path.join(
                    opts.cycle_build_dir, RECIPES_REPO, recipe, "conda", "meta.yaml"
                )
            ) as mfile:
                software_versions[recipe].latest = get_version_from_recipe(mfile)
        except KeyError:
            print(f"Cannot find {recipe} in repository list.")

    # Show version differences.
    if opts.verbose:
        print()
    all_ok = True
    for package, versions in software_versions.items():
        if not versions.is_latest():
            print(f"{package}: {versions}")
            all_ok = False
    if all_ok:
        print("No software versions are out of date.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-t",
        "--token-file",
        type=pathlib.Path,
        default="~/.gh_token",
        help="Specify path to GitHub token file.",
    )

    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Make script more verbose."
    )

    parser.add_argument(
        "cycle_build_dir",
        type=pathlib.Path,
        help=f"Path to where the {CYCLE_REPO} and {RECIPES_REPO} directories live.",
    )

    args = parser.parse_args()

    main(args)
