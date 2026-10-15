"""Classify what kind of page Chrome is currently showing (thread, block page, login wall, ...)."""

import json
from dataclasses import dataclass

PAGE_SNAPSHOT_JS = """(() => JSON.stringify({
  url: location.href,
  bodyText: document.body ? document.body.innerText.slice(0, 2000) : '',
  hasCommentArea: !!document.querySelector('.commentarea'),
  hasPostThing: !!document.querySelector('.thing.link'),
  loggedInUser: (document.querySelector('#header-bottom-right .user') || { textContent: null }).textContent,
  declaredCommentCount: (document.querySelector('.thing.link .comments') || { textContent: null }).textContent,
  moreLinkCount: document.querySelectorAll('.commentarea a.morelink').length,
}))()"""


@dataclass
class PageState:
    url: str
    body_text: str
    has_comment_area: bool
    has_post_thing: bool
    logged_in_user: str | None
    declared_comment_count: str | None
    more_link_count: int

    @property
    def is_old_reddit_thread(self):
        return self.has_comment_area and self.has_post_thing

    @property
    def is_blocked(self):
        return "blocked by network security" in self.body_text.lower()

    @property
    def logged_in(self):
        return self.logged_in_user is not None

    @property
    def declared_comment_total(self):
        digits = "".join(ch for ch in (self.declared_comment_count or "") if ch.isdigit())
        return int(digits) if digits else None


def snapshot(socket):
    raw = json.loads(socket.evaluate(PAGE_SNAPSHOT_JS))
    return PageState(
        url=raw["url"],
        body_text=raw["bodyText"],
        has_comment_area=raw["hasCommentArea"],
        has_post_thing=raw["hasPostThing"],
        logged_in_user=raw["loggedInUser"],
        declared_comment_count=raw["declaredCommentCount"],
        more_link_count=raw["moreLinkCount"],
    )
