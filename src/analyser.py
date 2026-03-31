"""Analyser module for computing statistics on scraped redditor data."""

from __future__ import annotations

from typing import Any

import pandas as pd


class RedditorAnalyser:
    """Computes statistics for a single redditor from scraped data.

    Parameters
    ----------
    data:
        A dict as returned by :meth:`~src.scraper.RedditorScraper.scrape`.
    """

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = data
        self._comments_df = pd.DataFrame(data.get("comments", []))
        self._submissions_df = pd.DataFrame(data.get("submissions", []))

        if not self._comments_df.empty:
            self._comments_df["created_utc"] = pd.to_datetime(
                self._comments_df["created_utc"], utc=True
            )
        if not self._submissions_df.empty:
            self._submissions_df["created_utc"] = pd.to_datetime(
                self._submissions_df["created_utc"], utc=True
            )

    # ------------------------------------------------------------------
    # Basic stats
    # ------------------------------------------------------------------

    @property
    def username(self) -> str:
        return self._data["username"]

    @property
    def total_karma(self) -> int:
        """Sum of link karma and comment karma."""
        return self._data.get("link_karma", 0) + self._data.get("comment_karma", 0)

    @property
    def link_karma(self) -> int:
        return self._data.get("link_karma", 0)

    @property
    def comment_karma(self) -> int:
        return self._data.get("comment_karma", 0)

    # ------------------------------------------------------------------
    # Comment analysis
    # ------------------------------------------------------------------

    def comments_per_month(self) -> pd.DataFrame:
        """Return a DataFrame with comment counts grouped by year-month.

        Returns
        -------
        DataFrame with columns ``year_month`` (period) and ``count``.
        """
        if self._comments_df.empty:
            return pd.DataFrame(columns=["year_month", "count"])

        df = self._comments_df.copy()
        df["year_month"] = df["created_utc"].dt.tz_convert(None).dt.to_period("M")
        result = (
            df.groupby("year_month")
            .size()
            .reset_index(name="count")
            .sort_values("year_month")
        )
        return result

    def average_comment_karma(self) -> float:
        """Return the average karma (score) per comment."""
        if self._comments_df.empty:
            return 0.0
        return float(self._comments_df["score"].mean())

    def top_subreddits_by_comments(self, n: int = 5) -> pd.DataFrame:
        """Return the *n* subreddits where the user comments most.

        Returns
        -------
        DataFrame with columns ``subreddit`` and ``count``, sorted descending.
        """
        if self._comments_df.empty:
            return pd.DataFrame(columns=["subreddit", "count"])

        result = (
            self._comments_df.groupby("subreddit")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )
        return result

    # ------------------------------------------------------------------
    # Submission analysis
    # ------------------------------------------------------------------

    def submissions_per_month(self) -> pd.DataFrame:
        """Return a DataFrame with submission counts grouped by year-month.

        Returns
        -------
        DataFrame with columns ``year_month`` (period) and ``count``.
        """
        if self._submissions_df.empty:
            return pd.DataFrame(columns=["year_month", "count"])

        df = self._submissions_df.copy()
        df["year_month"] = df["created_utc"].dt.tz_convert(None).dt.to_period("M")
        result = (
            df.groupby("year_month")
            .size()
            .reset_index(name="count")
            .sort_values("year_month")
        )
        return result

    def average_submission_score(self) -> float:
        """Return the average score per submission."""
        if self._submissions_df.empty:
            return 0.0
        return float(self._submissions_df["score"].mean())

    def top_subreddits_by_submissions(self, n: int = 5) -> pd.DataFrame:
        """Return the *n* subreddits where the user posts most.

        Returns
        -------
        DataFrame with columns ``subreddit`` and ``count``, sorted descending.
        """
        if self._submissions_df.empty:
            return pd.DataFrame(columns=["subreddit", "count"])

        result = (
            self._submissions_df.groupby("subreddit")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(n)
            .reset_index(drop=True)
        )
        return result

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def summary(self) -> dict[str, Any]:
        """Return a dict summarising all key statistics for the redditor."""
        return {
            "username": self.username,
            "link_karma": self.link_karma,
            "comment_karma": self.comment_karma,
            "total_karma": self.total_karma,
            "total_comments_scraped": len(self._comments_df),
            "total_submissions_scraped": len(self._submissions_df),
            "average_comment_karma": self.average_comment_karma(),
            "average_submission_score": self.average_submission_score(),
            "comments_per_month": self.comments_per_month().to_dict(orient="records"),
            "submissions_per_month": self.submissions_per_month().to_dict(
                orient="records"
            ),
            "top_subreddits_by_comments": self.top_subreddits_by_comments().to_dict(
                orient="records"
            ),
            "top_subreddits_by_submissions": self.top_subreddits_by_submissions().to_dict(
                orient="records"
            ),
        }
