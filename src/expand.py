"""Expand collapsed/hidden comment threads until the page shows everything it has."""

import time

from .errors import IncompleteExtraction
from .page_state import snapshot

CLICK_FIRST_MORELINK_JS = """(() => {
  const link = document.querySelector('.commentarea a.morelink');
  if (!link) return false;
  link.click();
  return true;
})()"""


def expand_all_comments(tab, max_rounds=200, settle_seconds=1.0):
    """Click each 'read more' link one at a time; Reddit loads each batch asynchronously.

    Raises if the morelink count stalls: silently returning here would let the
    caller report a partial capture as complete.
    """
    stalled_rounds = 0
    previous_count = -1
    for _ in range(max_rounds):
        state = snapshot(tab.socket)
        if state.more_link_count == 0:
            return
        if state.more_link_count == previous_count:
            stalled_rounds += 1
            if stalled_rounds >= 5:
                raise IncompleteExtraction(
                    f"Expansion stalled with {state.more_link_count} 'read more' links "
                    "still unclickable."
                )
        else:
            stalled_rounds = 0
        previous_count = state.more_link_count

        tab.socket.evaluate(CLICK_FIRST_MORELINK_JS)
        time.sleep(settle_seconds)

    raise IncompleteExtraction(f"Expansion exceeded {max_rounds} rounds.")
