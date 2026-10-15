"""Own one Chrome tab pointed at a Reddit thread, driven over CDP."""

import time
from contextlib import contextmanager

from . import cdp
from .errors import ChromeNotReachable, ThreadNotLoaded

PAGE_READY_JS = "document.readyState === 'complete'"


class ThreadTab:
    def __init__(self, socket, target_id, cdp_url):
        self.socket = socket
        self.target_id = target_id
        self.cdp_url = cdp_url

    def wait_until_loaded(self, timeout_seconds=20):
        if not wait_until(lambda: self.socket.evaluate(PAGE_READY_JS), timeout_seconds):
            raise ThreadNotLoaded(f"Page did not finish loading within {timeout_seconds}s.")

    def close_quietly(self):
        try:
            self.socket.close()
        except Exception:
            pass
        try:
            with cdp.CdpSocket(cdp.browser_socket_url(self.cdp_url)) as browser:
                browser.call("Target.closeTarget", targetId=self.target_id)
        except Exception:
            pass


@contextmanager
def open_thread_tab(cdp_url, url):
    """Open `url` in a new tab of the running Chrome and yield a connected ThreadTab."""
    target_id = None
    try:
        target_id = cdp.open_target(cdp_url, url)
        page_ws = cdp.wait_for_page_target(cdp_url, target_id)
        socket = cdp.CdpSocket(page_ws)
    except (OSError, LookupError) + cdp.WEBSOCKET_ERRORS as error:
        if target_id is not None:
            close_target(cdp_url, target_id)
        raise ChromeNotReachable(
            f"Could not reach Chrome at {cdp_url}. Start it headful with "
            f"--remote-debugging-port (see NOTES.md). Original error: {error}"
        ) from error

    tab = ThreadTab(socket, target_id, cdp_url)
    try:
        yield tab
    finally:
        tab.close_quietly()


def close_target(cdp_url, target_id):
    try:
        with cdp.CdpSocket(cdp.browser_socket_url(cdp_url)) as browser:
            browser.call("Target.closeTarget", targetId=target_id)
    except Exception:
        pass


def wait_until(condition, timeout_seconds=20, poll_seconds=0.5):
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        if condition():
            return True
        time.sleep(poll_seconds)
    return False
