"""Scraper module for fetching redditor data via the Reddit API (PRAW)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import praw


class RedditorScraper:
    """Fetches comment and submission history for one or more Reddit users."""

    def __init__(self, reddit: praw.Reddit) -> None:
        self.reddit = reddit

    def scrape(self, username: str, limit: int | None = 100) -> dict[str, Any]:
        """Return scraped data for a single redditor.

        Parameters
        ----------
        username:
            The Reddit username to scrape (without the ``u/`` prefix).
        limit:
            Maximum number of comments and submissions to fetch.
            Pass ``None`` to fetch as many as the API allows (~1000).

        Returns
        -------
        dict with keys:
            - ``username``  – the Reddit username
            - ``link_karma`` – the user's current link karma
            - ``comment_karma`` – the user's current comment karma
            - ``created_utc`` – account creation timestamp (UTC)
            - ``comments`` – list of dicts, each representing one comment
            - ``submissions`` – list of dicts, each representing one submission
        """
        redditor = self.reddit.redditor(username)

        comments = []
        for comment in redditor.comments.new(limit=limit):
            comments.append(
                {
                    "id": comment.id,
                    "body": comment.body,
                    "score": comment.score,
                    "subreddit": str(comment.subreddit),
                    "created_utc": datetime.fromtimestamp(
                        comment.created_utc, tz=timezone.utc
                    ),
                }
            )

        submissions = []
        for submission in redditor.submissions.new(limit=limit):
            submissions.append(
                {
                    "id": submission.id,
                    "title": submission.title,
                    "score": submission.score,
                    "subreddit": str(submission.subreddit),
                    "created_utc": datetime.fromtimestamp(
                        submission.created_utc, tz=timezone.utc
                    ),
                    "num_comments": submission.num_comments,
                }
            )

        return {
            "username": username,
            "link_karma": redditor.link_karma,
            "comment_karma": redditor.comment_karma,
            "created_utc": datetime.fromtimestamp(
                redditor.created_utc, tz=timezone.utc
            ),
            "comments": comments,
            "submissions": submissions,
        }

    def scrape_many(
        self, usernames: list[str], limit: int | None = 100
    ) -> list[dict[str, Any]]:
        """Scrape data for multiple redditors.

        Parameters
        ----------
        usernames:
            List of Reddit usernames to scrape.
        limit:
            Passed through to :meth:`scrape` for each user.

        Returns
        -------
        List of scraped data dicts, one per username.
        """
        return [self.scrape(username, limit=limit) for username in usernames]
