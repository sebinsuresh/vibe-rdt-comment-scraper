# NOTES — how this works and what was observed

Working notes for whoever iterates on this next. Claims below are dated observations
from one environment, not verified constants — Reddit and Chrome change. Re-check
before trusting one as a constraint.

## What it does

`scrape_thread(url)` opens the thread in a **new tab of an already-running Chrome**
(via CDP), expands every "read more" link, extracts the full comment tree, and
returns `{post, comments}`. It never logs in, never launches Chrome, and has no
headless path — if Chrome isn't reachable it raises `ChromeNotReachable` with
instructions.

## Setup that was in use when this was built (2026-10)

- Chrome running headful with `--remote-debugging-port=9222` and a dedicated
  `--user-data-dir` (a profile dir of your choosing), on an X display.
- That profile was logged in to Reddit (cookie `reddit_session` on `.reddit.com`).
- Only dependency: `websocket-client` (see requirements.txt).

## Observations (treat as hypotheses to re-verify)

- **Headless Chrome got a network-security block page** ("You've been blocked by
  network security", 🐴 title) on `old.reddit.com`, even with a logged-in profile's
  cookies. Headful on the same profile worked. One observation, one machine —
  headless may work elsewhere, but assume headful until proven otherwise.
- **`?sort=top` on old.reddit may end up showing `www.reddit.com` in `location.href`
  while still serving old-reddit DOM** (a `redesign_optout` cookie was present in the
  profile). The page-state check keys on DOM shape (`.commentarea` + `.thing.link`),
  not the URL, so this is harmless — but don't "fix" it by asserting on the URL.
- **Deleted/removed comments have `data-fullname=null`, and their bylink can point at
  an unrelated comment's permalink** (observed: a deleted comment's bylink carried the
  id of the reply below it). So the slug is NOT a safe id — the extraction JS
  synthesizes `t1_missing_<index>` ids instead, assigned before parent links are
  wired, so replies to deleted comments stay attached and ids can't collide.
- **Comment count check:** the post's declared "N comments" matched the DOM comment
  count after expansion in the one thread tested (147/147). The check is kept because
  a mismatch has historically meant hidden replies, but Reddit's declared count can
  lag or exclude removed items — that's why a mismatch only raises when no
  `morelink` remains. If it still false-alarms, loosen it.
- **`Target.createTarget` over the browser WebSocket** is used to open tabs because
  the HTTP `/json/new` endpoint's verb requirements have varied across Chrome
  versions. The new target may not appear in `/json` immediately after creation, so
  `wait_for_page_target` polls before connecting.
- **Expansion loop:** clicking one `a.morelink` at a time with a 1s settle was enough
  for a ~150-comment thread. Large threads may need the settle time or round limit
  raised; a stall now raises `IncompleteExtraction` rather than returning quietly.

## Login behavior

- Not logged in → `RedditNotLoggedIn` with a message telling the user to log in in
  that Chrome window. The scraper deliberately does not attempt login or touch
  credentials.
- Whether logged-out old.reddit serves full comments at all varies; it has been
  increasingly gated. The explicit error exists so failures are legible rather than
  silently partial.

## Deliberate non-goals (for now)

- No CLI/UI (API only, by request). No headless fallback. No Reddit API/OAuth path.
  No rate-limit/backoff strategy beyond the expansion settle delay.
