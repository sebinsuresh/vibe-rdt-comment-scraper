# reddit-scraper

Scrapes every comment (and reply) from a Reddit thread by driving an already-running,
logged-in Chrome over the DevTools Protocol.

## Run

```bash
pip install -r requirements.txt
```

Start Chrome headful with a Reddit-logged-in profile:

```bash
google-chrome --remote-debugging-port=9222 --user-data-dir=/path/to/dedicated-profile
```

Then:

```python
from reddit_scraper import scrape_thread

data = scrape_thread("https://www.reddit.com/r/subreddit/comments/id/slug/")
# data["post"], data["comments"]
```

See NOTES.md for design observations and known limitations. Scraping Reddit outside
its official API may violate the ToS; use responsibly.
