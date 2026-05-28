# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a research and data analysis project exploring AI music generation (Suno) and streaming platform data. The codebase is primarily Python for data fetching and analysis.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run a specific fetcher script
python src/fetch_itunes.py
python src/fetch_youtube.py

# Run all fetchers
python src/fetch_all.py

# Run analysis
python src/analyze.py

# Run tests
pytest

# Run a single test
pytest tests/test_fetch.py::test_function_name
```

## Architecture

The project is divided into four phases, each with its own directory:

- **`research/`** — Markdown reports. `api_availability.md` documents what data can/cannot be fetched per platform. Add platform-specific notes here.
- **`src/`** — Python scripts. Each streaming platform gets its own fetcher module (e.g. `fetch_itunes.py`). `fetch_all.py` orchestrates them. `analyze.py` runs analysis on data in `data/processed/`.
- **`data/raw/`** — Unmodified API responses (JSON). Never commit API keys or tokens.
- **`data/processed/`** — Cleaned/transformed data ready for analysis.
- **`slides/`** — Final presentation materials.

## Platform API Notes

- **iTunes Search API** — Public, no auth required. Base URL: `https://itunes.apple.com/search`
- **YouTube Data API v3** — Requires API key. Set as `YOUTUBE_API_KEY` env var.
- Other platforms (Spotify, etc.) — document auth requirements in `research/api_availability.md` as discovered.

Store API keys in a `.env` file (never commit it). Load with `python-dotenv`.
