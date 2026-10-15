"""Minimal Chrome DevTools Protocol transport: target discovery over HTTP, JSON-RPC over WebSocket."""

import json
import time
import urllib.request

import websocket

WEBSOCKET_ERRORS = (websocket.WebSocketException,)


def list_targets(cdp_url):
    with urllib.request.urlopen(cdp_url.rstrip("/") + "/json") as response:
        return json.load(response)


def open_target(cdp_url, url):
    """Create a new browser tab via the browser-level CDP socket (HTTP /json/new is unreliable across Chrome versions)."""
    with CdpSocket(browser_socket_url(cdp_url)) as socket:
        result = socket.call("Target.createTarget", url=url)
        return result["targetId"]


def wait_for_page_target(cdp_url, target_id, timeout_seconds=10):
    """Poll /json until the new tab's page socket appears; createTarget can win the race against listing."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        for target in list_targets(cdp_url):
            if target.get("id") == target_id:
                return target["webSocketDebuggerUrl"]
        time.sleep(0.3)
    raise LookupError(f"No CDP target with id {target_id} at {cdp_url} after {timeout_seconds}s")


def browser_socket_url(cdp_url):
    with urllib.request.urlopen(cdp_url.rstrip("/") + "/json/version") as response:
        return json.load(response)["webSocketDebuggerUrl"]


class CdpSocket:
    """One JSON-RPC connection to a CDP target (browser-level or page-level)."""

    def __init__(self, ws_url):
        self._ws = websocket.create_connection(ws_url, suppress_origin=True, timeout=30)
        self._next_id = 1

    def call(self, method, **params):
        self._ws.send(json.dumps({"id": self._next_id, "method": method, "params": params}))
        wanted_id = self._next_id
        self._next_id += 1
        while True:
            message = json.loads(self._ws.recv())
            if message.get("id") != wanted_id:
                continue
            if "error" in message:
                raise RuntimeError(f"CDP {method} failed: {message['error']}")
            return message.get("result", {})

    def evaluate(self, expression):
        result = self.call(
            "Runtime.evaluate", expression=expression, returnByValue=True, awaitPromise=True
        )
        if result.get("exceptionDetails"):
            raise RuntimeError(f"Page JS raised: {result['exceptionDetails']}")
        return result["result"].get("value")

    def close(self):
        self._ws.close()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()
