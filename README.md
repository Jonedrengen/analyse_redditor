# analyse_redditor

A simple command-line tool that scrapes Reddit user profiles via the official
Reddit API and performs basic analysis — comments per month, average karma,
top subreddits, and more.

## Features

- Scrape comment and submission history for one or more Reddit users
- Count comments and submissions grouped by month
- Calculate average comment karma and average submission score
- Identify the most active subreddits (by comments and by submissions)
- Output results as human-readable text or as JSON

## Prerequisites

- [Conda](https://docs.conda.io/en/latest/) (Miniconda or Anaconda)
- A Reddit application (free) to obtain API credentials:
  1. Go to <https://www.reddit.com/prefs/apps> and create a **script** app.
  2. Copy the **client ID** (shown under the app name) and the
     **client secret**.

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/Jonedrengen/analyse_redditor.git
cd analyse_redditor

# 2. Create and activate the conda environment
conda env create -f environment.yml
conda activate analyse_redditor

# 3. Configure credentials
cp .env.example .env
# Edit .env and fill in your REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
# and REDDIT_USER_AGENT values.
```

## Usage

```bash
# Analyse a single user
python main.py spez

# Analyse multiple users
python main.py spez kn0thing gallowboob

# Fetch up to 500 items per user (default is 100)
python main.py spez --limit 500

# Output as JSON
python main.py spez --json
```

### Example output

```
==================================================
  u/spez
==================================================
  Link karma     : 123,456
  Comment karma  : 78,910
  Total karma    : 202,366
  Avg comment karma : 12.34
  Avg submission score : 56.78

  Comments per month (most recent first):
    2024-03: 7
    2024-02: 12
    2024-01: 5

  Top subreddits by comments:
    r/announcements: 9
    r/help: 4
    r/bugs: 3

  Top subreddits by submissions:
    r/announcements: 5
    r/reddit.com: 2
```

## Project structure

```
analyse_redditor/
├── main.py            # CLI entry point
├── environment.yml    # Conda environment specification
├── .env.example       # Credentials template
├── src/
│   ├── scraper.py     # RedditorScraper — fetches data via PRAW
│   └── analyser.py    # RedditorAnalyser — computes statistics
└── tests/
    └── test_analyser.py
```

## Running the tests

```bash
conda activate analyse_redditor
pytest tests/ -v
```

## License

See [LICENSE](LICENSE).
