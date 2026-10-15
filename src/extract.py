"""Pull every comment out of the loaded page and verify the capture is complete."""

import json
from pathlib import Path

from .errors import IncompleteExtraction, ThreadNotLoaded
from .page_state import snapshot

JS_DIR = Path(__file__).parent / "js"


def extract_comments(tab):
    state = snapshot(tab.socket)
    if not state.is_old_reddit_thread:
        raise ThreadNotLoaded(f"Page at {state.url} does not look like an old-reddit thread.")

    comments = json.loads(tab.socket.evaluate((JS_DIR / "extract_comments.js").read_text()))

    # The declared count can lag or exclude removed items, so a mismatch is only
    # conclusive when no 'read more' links remain.
    declared = state.declared_comment_total
    if declared is not None and len(comments) != declared and state.more_link_count == 0:
        raise IncompleteExtraction(
            f"Extracted {len(comments)} comments but the post declares {declared}; "
            "no 'read more' links remain, so the page itself is short."
        )
    return comments
