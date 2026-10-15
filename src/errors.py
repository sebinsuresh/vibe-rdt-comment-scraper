"""Errors a caller may want to handle explicitly."""


class RedditScraperError(RuntimeError):
    """Base class for all scraper failures."""


class ChromeNotReachable(RedditScraperError):
    pass


class RedditBlocked(RedditScraperError):
    pass


class RedditNotLoggedIn(RedditScraperError):
    pass


class ThreadNotLoaded(RedditScraperError):
    pass


class IncompleteExtraction(RedditScraperError):
    pass
