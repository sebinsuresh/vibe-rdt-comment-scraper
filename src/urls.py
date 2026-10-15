"""Normalize any reddit URL into an old-reddit thread URL with a sort order."""

import re
from urllib.parse import urlparse, urlunparse

ALLOWED_SORTS = {"top", "new", "best", "controversial", "old"}


def to_old_reddit_sorted_url(url, sort="top"):
    if sort not in ALLOWED_SORTS:
        raise ValueError(f"sort must be one of {sorted(ALLOWED_SORTS)}, got: {sort!r}")

    parsed = urlparse(url)
    path = parsed.path.rstrip("/")

    match = re.match(r"^(/r/[^/]+/comments/.+)$", path)
    if not match:
        raise ValueError(f"Expected a /r/<sub>/comments/<id>/<slug> post URL, got: {url}")

    old_netloc = re.sub(r"^(www|np|m)\.", "old.", parsed.netloc)
    if not old_netloc.startswith("old."):
        old_netloc = "old.reddit.com"
    return urlunparse((parsed.scheme or "https", old_netloc, match.group(1), "", f"sort={sort}", ""))
