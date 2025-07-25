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


def prepare_template(opts: argparse.Namespace) -> str:
    script_dir = pathlib.Path(__file__).resolve().parent
    templates_dir = script_dir / "templates"
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template("cycle_upgrade_page.html")
    template_vars = opts.__dict__
    template_vars["now"] = datetime.datetime.now().strftime("%Y-%m-%d")
    return template.render(template_vars)


def main(opts: argparse.Namespace) -> None:
    confluence_auth = ticket_helpers.get_jira_credentials(opts.token_file)
    cycle = opts.cycle
    confluence = Confluence(
        url=ticket_helpers.JIRA_SERVER,
        username=confluence_auth[0],
        password=confluence_auth[1],
    )
    page = confluence.get_page_by_title(space=SPACE_KEY, title=f"Cycle {cycle} Upgrade")
    body = prepare_template(opts)

    payload: dict[str, Any] = {
        "title": f"Cycle {cycle} Upgrade",
        "type": "page",
        "body": {"storage": {"value": body, "representation": "storage"}},
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
            full_page = confluence.get(f"/rest/api/content/{page['id']}?expand=version")
            new_version = full_page["version"]["number"] + 1
            payload["version"]["number"] = new_version
            confluence.put(f"/rest/api/content/{page['id']}", data=payload)
        else:
            payload["version"] = {"number": 1}
            payload["space"] = {"key": SPACE_KEY}
            payload["ancestors"] = [{"id": PARENT_PAGE_ID}]
            confluence.post("/rest/api/content/", data=payload)
    except Exception as e:
        print(f"Error creating/updating page: {e}")
        raise


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
        "--cycle", help="Number of the Cycle to create/update the page for."
    )

    parser.add_argument(
        "--xml-close",
        default=None,
        help="The date when the XML work for the Cycle closes in YYYY-MM-DD format.",
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
    args = parser.parse_args()

    main(args)
