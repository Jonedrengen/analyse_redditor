"""Unit tests for src.analyser.RedditorAnalyser."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from src.analyser import RedditorAnalyser


def _make_comment(score: int, subreddit: str, year: int, month: int) -> dict:
    return {
        "id": f"c_{year}{month:02d}",
        "body": "test comment",
        "score": score,
        "subreddit": subreddit,
        "created_utc": datetime(year, month, 1, tzinfo=timezone.utc),
    }


def _make_submission(score: int, subreddit: str, year: int, month: int) -> dict:
    return {
        "id": f"s_{year}{month:02d}",
        "title": "test post",
        "score": score,
        "subreddit": subreddit,
        "created_utc": datetime(year, month, 1, tzinfo=timezone.utc),
        "num_comments": 3,
    }


@pytest.fixture()
def sample_data() -> dict:
    return {
        "username": "test_user",
        "link_karma": 500,
        "comment_karma": 1500,
        "created_utc": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "comments": [
            _make_comment(10, "python", 2024, 1),
            _make_comment(20, "python", 2024, 1),
            _make_comment(5, "learnpython", 2024, 2),
            _make_comment(30, "python", 2024, 3),
            _make_comment(15, "gaming", 2024, 3),
        ],
        "submissions": [
            _make_submission(100, "python", 2024, 1),
            _make_submission(50, "gaming", 2024, 2),
            _make_submission(200, "python", 2024, 3),
        ],
    }


@pytest.fixture()
def analyser(sample_data) -> RedditorAnalyser:
    return RedditorAnalyser(sample_data)


@pytest.fixture()
def empty_analyser() -> RedditorAnalyser:
    return RedditorAnalyser(
        {
            "username": "empty_user",
            "link_karma": 0,
            "comment_karma": 0,
            "created_utc": datetime(2022, 6, 1, tzinfo=timezone.utc),
            "comments": [],
            "submissions": [],
        }
    )


# ---------------------------------------------------------------------------
# Basic stats
# ---------------------------------------------------------------------------


def test_username(analyser):
    assert analyser.username == "test_user"


def test_total_karma(analyser):
    assert analyser.total_karma == 2000


def test_link_karma(analyser):
    assert analyser.link_karma == 500


def test_comment_karma(analyser):
    assert analyser.comment_karma == 1500


# ---------------------------------------------------------------------------
# Comment analysis
# ---------------------------------------------------------------------------


def test_comments_per_month_row_count(analyser):
    df = analyser.comments_per_month()
    # 3 distinct months: 2024-01, 2024-02, 2024-03
    assert len(df) == 3


def test_comments_per_month_counts(analyser):
    df = analyser.comments_per_month()
    counts = dict(zip(df["year_month"].astype(str), df["count"]))
    assert counts["2024-01"] == 2
    assert counts["2024-02"] == 1
    assert counts["2024-03"] == 2


def test_average_comment_karma(analyser):
    # (10 + 20 + 5 + 30 + 15) / 5 = 16.0
    assert analyser.average_comment_karma() == pytest.approx(16.0)


def test_top_subreddits_by_comments(analyser):
    df = analyser.top_subreddits_by_comments(n=2)
    assert len(df) <= 2
    assert df.iloc[0]["subreddit"] == "python"
    assert df.iloc[0]["count"] == 3


# ---------------------------------------------------------------------------
# Submission analysis
# ---------------------------------------------------------------------------


def test_submissions_per_month_row_count(analyser):
    df = analyser.submissions_per_month()
    assert len(df) == 3


def test_average_submission_score(analyser):
    # (100 + 50 + 200) / 3 ≈ 116.67
    assert analyser.average_submission_score() == pytest.approx(350 / 3)


def test_top_subreddits_by_submissions(analyser):
    df = analyser.top_subreddits_by_submissions(n=5)
    assert df.iloc[0]["subreddit"] == "python"
    assert df.iloc[0]["count"] == 2


# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------


def test_summary_keys(analyser):
    summary = analyser.summary()
    expected_keys = {
        "username",
        "link_karma",
        "comment_karma",
        "total_karma",
        "total_comments_scraped",
        "total_submissions_scraped",
        "average_comment_karma",
        "average_submission_score",
        "comments_per_month",
        "submissions_per_month",
        "top_subreddits_by_comments",
        "top_subreddits_by_submissions",
    }
    assert expected_keys == set(summary.keys())


def test_summary_totals(analyser):
    summary = analyser.summary()
    assert summary["total_comments_scraped"] == 5
    assert summary["total_submissions_scraped"] == 3


# ---------------------------------------------------------------------------
# Edge cases – empty data
# ---------------------------------------------------------------------------


def test_empty_comments_per_month(empty_analyser):
    df = empty_analyser.comments_per_month()
    assert df.empty


def test_empty_average_comment_karma(empty_analyser):
    assert empty_analyser.average_comment_karma() == 0.0


def test_empty_average_submission_score(empty_analyser):
    assert empty_analyser.average_submission_score() == 0.0


def test_empty_top_subreddits_by_comments(empty_analyser):
    df = empty_analyser.top_subreddits_by_comments()
    assert df.empty


def test_empty_summary(empty_analyser):
    summary = empty_analyser.summary()
    assert summary["total_comments_scraped"] == 0
    assert summary["total_karma"] == 0
