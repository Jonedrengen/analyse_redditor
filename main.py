"""CLI entry point for analyse_redditor.

Usage
-----
    python main.py <username1> [<username2> ...]

Environment variables (or .env file)
-------------------------------------
    REDDIT_CLIENT_ID     – Reddit app client ID
    REDDIT_CLIENT_SECRET – Reddit app client secret
    REDDIT_USER_AGENT    – User-agent string for the Reddit API
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone

import praw
from dotenv import load_dotenv

from src.analyser import RedditorAnalyser
from src.scraper import RedditorScraper


def _build_reddit() -> praw.Reddit:
    """Create a read-only Reddit instance from environment variables."""
    load_dotenv()
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    user_agent = os.environ.get(
        "REDDIT_USER_AGENT", "analyse_redditor/1.0"
    )

    if not client_id or not client_secret:
        print(
            "Error: REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET must be set.\n"
            "Copy .env.example to .env and fill in your credentials.",
            file=sys.stderr,
        )
        sys.exit(1)

    return praw.Reddit(
        client_id=client_id,
        client_secret=client_secret,
        user_agent=user_agent,
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scrape and analyse Reddit user profiles."
    )
    parser.add_argument(
        "usernames",
        nargs="+",
        metavar="USERNAME",
        help="One or more Reddit usernames to analyse.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=100,
        metavar="N",
        help="Max comments/submissions to fetch per user (default: 100).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="output_json",
        help="Output results as JSON instead of plain text.",
    )
    return parser.parse_args(argv)


def _print_summary(summary: dict) -> None:
    """Pretty-print a summary dict to stdout."""
    print(f"\n{'=' * 50}")
    print(f"  u/{summary['username']}")
    print(f"{'=' * 50}")
    print(f"  Link karma     : {summary['link_karma']:,}")
    print(f"  Comment karma  : {summary['comment_karma']:,}")
    print(f"  Total karma    : {summary['total_karma']:,}")
    print(
        f"  Avg comment karma : {summary['average_comment_karma']:.2f}"
    )
    print(
        f"  Avg submission score : {summary['average_submission_score']:.2f}"
    )
    print(f"\n  Comments per month (most recent first):")
    for row in reversed(summary["comments_per_month"]):
        print(f"    {row['year_month']}: {row['count']}")
    print(f"\n  Top subreddits by comments:")
    for row in summary["top_subreddits_by_comments"]:
        print(f"    r/{row['subreddit']}: {row['count']}")
    print(f"\n  Top subreddits by submissions:")
    for row in summary["top_subreddits_by_submissions"]:
        print(f"    r/{row['subreddit']}: {row['count']}")


def _default_serialiser(obj):
    if hasattr(obj, "isoformat"):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serialisable")


def main(argv: list[str] | None = None) -> None:
    args = _parse_args(argv)
    reddit = _build_reddit()
    scraper = RedditorScraper(reddit)

    results = []
    for username in args.usernames:
        print(f"Scraping u/{username}…", file=sys.stderr)
        data = scraper.scrape(username, limit=args.limit)
        analyser = RedditorAnalyser(data)
        summary = analyser.summary()
        results.append(summary)

    if args.output_json:
        print(json.dumps(results, indent=2, default=_default_serialiser))
    else:
        for summary in results:
            _print_summary(summary)


if __name__ == "__main__":
    main()
