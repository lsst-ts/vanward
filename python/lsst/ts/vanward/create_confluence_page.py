"""Script to create/update Cycle upgrade Confluence page."""

import argparse
import datetime
import pathlib
from typing import Any

from atlassian import Confluence
from jinja2 import Environment, FileSystemLoader

from . import ticket_helpers

SPACE_KEY = "LSSTCOM"
PARENT_PAGE_ID = "53752125"

__all__ = ["runner"]


def prepare_template(opts: argparse.Namespace, template_name: str) -> str:
    script_dir = pathlib.Path(__file__).resolve().parent
    templates_dir = script_dir / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template(template_name)
    template_vars = opts.__dict__.copy()
    template_vars["now"] = datetime.datetime.now().strftime("%Y-%m-%d")
    return template.render(template_vars)


def main(opts: argparse.Namespace) -> None:
    confluence_auth = ticket_helpers.get_jira_credentials(opts.token_file)
    cycle = opts.cycle_number
    revision = int(opts.revision)

    confluence = Confluence(
        url=ticket_helpers.JIRA_SERVER,
        username=confluence_auth[0],
        password=confluence_auth[1],
    )
    page = confluence.get_page_by_title(space=SPACE_KEY, title=f"Cycle {cycle} Upgrade")

    if revision > 0:
        new_html = prepare_template(opts, "incremental_upgrade_section.html")
    else:
        new_html = prepare_template(opts, "cycle_upgrade_page.html")

    payload: dict[str, Any] = {
        "title": f"Cycle {cycle} Upgrade",
        "type": "page",
        "body": {"storage": {"value": "", "representation": "storage"}},
        "version": {},
        "metadata": {
            "properties": {
                "content-appearance-draft": {"value": "full-width"},
                "content-appearance-published": {"value": "full-width"},
            }
        },
    }
    try:
        if page:
            page = confluence.get_page_by_id(page["id"], expand="version,body.storage")
            current_body = page["body"]["storage"]["value"]
            current_version = page["version"]["number"]
            combined_body = (
                (current_body + "\n" + new_html) if revision > 0 else new_html
            )
            payload["body"]["storage"]["value"] = combined_body
            payload["version"]["number"] = current_version + 1
            confluence.put(f"/rest/api/content/{page['id']}", data=payload)
        else:
            payload["version"] = {"number": 1}
            payload["space"] = {"key": SPACE_KEY}
            payload["ancestors"] = [{"id": PARENT_PAGE_ID}]
            payload["body"]["storage"]["value"] = new_html
            confluence.post("/rest/api/content/", data=payload)
    except Exception as e:
        print(f"Error creating/updating page: {e}")
        raise


def runner() -> None:
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "cycle_number", help="Number of the Cycle to create/update the page for."
    )

    parser.add_argument(
        "--revision",
        type=int,
        default=0,
        help="Revision number. If > 0, append incremental upgrade section.",
    )

    parser.add_argument(
        "-t",
        "--token-file",
        type=pathlib.Path,
        default="~/.auth/jira",
        help="Specify path to Jira credentials file.",
    )

    parser.add_argument(
        "--xml-close",
        default=None,
        help="The date when the XML work for the Cycle closes in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--release-date",
        default=None,
        help="The date for the set up of the release branch in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--artifact-build",
        default=None,
        help="The date for the artifact build in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--container-build",
        default=None,
        help="The date for the container build week in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--bts-deploy",
        default=None,
        help="The date for the BTS test and deployment week in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--summit-deploy",
        default=None,
        help="The date for the Summit deployment in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--tts-deploy",
        default=None,
        help="The date for the TTS deployment in YYYY-MM-DD format.",
    )

    parser.add_argument(
        "--add-request-section",
        action="store_true",
        help="Append the request for incremental upgrades section to the end of the page.",
    )

    args = parser.parse_args()

    main(args)
