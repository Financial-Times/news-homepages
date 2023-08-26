from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

import click
import requests
from retry import retry

from . import utils


@click.command()
@click.argument("handle")
@click.option("-o", "--output-dir", "output_dir", default="./")
@click.option("--timeout", "timeout", default="5")
def cli(handle: str, output_dir: str, timeout: str = "5"):
    """Save the raw robots.txt of the provided site."""
    # Get the site
    site = utils.get_site(handle)

    # Get the robots.txt
    robotstxt = _get_robotstxt(site["url"], int(timeout))

    if robotstxt is None:
        # If there is no robots.txt, we drop out now
        return

    # Set the output path
    output_path = Path(output_dir) / f"{utils.safe_ia_handle(handle)}.robots.txt"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write it out
    with output_path.open("w") as f:
        f.write(robotstxt)


@retry(tries=3, delay=15, backoff=2)
def _get_robotstxt(
    site_url: str,
    timeout: int = 5,
    user_agent: str = "NewsHomepagesBot (https://homepages.news)",
) -> str | None:
    """Get the raw robots.txt for a site."""
    # Create the robots.txt URL
    robotstxt_url = urlparse(site_url)._replace(path="robots.txt").geturl()

    # Set the headers
    headers = {
        "User-Agent": user_agent,
    }

    # Make the request
    r = requests.get(robotstxt_url, timeout=timeout, headers=headers)

    # Check if the request is a 404
    if r.status_code == 404:
        # In this case, there is no robots.txt
        # so we return None
        return None
    else:
        # Otherwise, we return the text,
        # after checking that the request was successful
        assert r.ok
        return r.text


if __name__ == "__main__":
    cli()
