"""Public API: scrape thread data from any Reddit post URL via a logged-in Chrome."""

import json
import time
from pathlib import Path

from .errors import RedditBlocked, RedditNotLoggedIn, ThreadNotLoaded
from .expand import expand_all_comments
from .extract import extract_comments
from .page_state import snapshot
from .session import open_thread_tab
from .urls import to_old_reddit_sorted_url

JS_DIR = Path(__file__).parent / "js"

DEFAULT_CDP_URL = "http://localhost:9222"


def scrape_thread(url, cdp_url=DEFAULT_CDP_URL, sort="top"):
    """Return {post, comments} for a Reddit thread, with every comment and reply expanded.

    Requires a headful Chrome with a Reddit-logged-in profile listening on `cdp_url`.
    """
    with open_thread_tab(cdp_url, to_old_reddit_sorted_url(url, sort)) as tab:
        tab.wait_until_loaded()
        state = wait_for_classifiable_page(tab)

        if state.is_blocked:
            raise RedditBlocked(
                "Reddit served a network-security block page. This usually means the "
                "browser is headless or the profile is flagged; see NOTES.md."
            )
        if not state.is_old_reddit_thread:
            raise ThreadNotLoaded(f"Thread did not render within 15s: {url}")
        if not state.logged_in:
            raise RedditNotLoggedIn(
                "The Chrome profile on this CDP port is not logged in to Reddit. "
                "Open old.reddit.com in that Chrome window and log in, then re-run."
            )

        expand_all_comments(tab)
        comments = extract_comments(tab)
        post = json.loads(tab.socket.evaluate((JS_DIR / "extract_post.js").read_text()))
        post["url"] = url
        return {"post": post, "comments": comments}


def wait_for_classifiable_page(tab, timeout_seconds=15):
    """old.reddit can sit on an interstitial for a moment; wait until the page is a thread or a block page."""

    def classifiable():
        state = snapshot(tab.socket)
        return state if (state.is_old_reddit_thread or state.is_blocked) else None

    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        found = classifiable()
        if found:
            return found
        time.sleep(0.5)
    return snapshot(tab.socket)
