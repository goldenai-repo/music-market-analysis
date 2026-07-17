"""
Search YouTube for candidate videos using the artist-song pipeline CSV.

Input:
    data/processed/turkish_artist_song_pipeline.csv

Output:
    data/processed/turkish_artist_song_candidates.csv

Run from the project root:
    python src/search_turkish_artist_songs.py

Examples:
    python src/search_turkish_artist_songs.py --results-per-song 3
    python src/search_turkish_artist_songs.py --max-songs 5
    python src/search_turkish_artist_songs.py --query-variant ai
    python src/search_turkish_artist_songs.py --query-variant all

Environment:
    Add YOUTUBE_API_KEY=... to your .env file.

Notes:
- The output is long-form: one artist-song seed can produce several candidate videos.
- This script does not decide whether a result is valid. Manual review comes next.
- search.list is quota-expensive, so start with a small --max-songs test.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None


DEFAULT_INPUT = Path("data/processed/turkish_artist_song_pipeline.csv")
DEFAULT_OUTPUT = Path("data/processed/turkish_artist_song_candidates.csv")

OUTPUT_FIELDS = [
    "artist_name",
    "seed_song_title",
    "search_query",
    "query_variant",
    "candidate_rank",
    "video_id",
    "candidate_title",
    "channel_title",
    "published_at",
    "youtube_url",
    "description_preview",
    "view_count",
    "like_count",
    "comment_count",
    "duration",
    "category_id",
    "default_language",
    "default_audio_language",
    "manual_valid",
    "language_verified",
    "is_music_video",
    "ai_suno_related",
    "channel_type",
    "genre_style",
    "manual_theme",
    "review_notes",
    "pipeline_status",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Search YouTube for candidate videos from artist-song seeds."
    )
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--results-per-song",
        type=int,
        default=3,
        help="Number of candidate videos to keep for each query (1-10).",
    )
    parser.add_argument(
        "--max-songs",
        type=int,
        default=5,
        help="Maximum number of seed songs to process. Use 0 for all.",
    )
    parser.add_argument(
        "--query-variant",
        choices=["base", "ai", "suno", "cover", "all"],
        default="base",
        help=(
            "Search the exact artist/song only, add one qualifier, "
            "or run all four variants."
        ),
    )
    parser.add_argument(
        "--region-code",
        default="TR",
        help="Two-letter region code used to improve result relevance.",
    )
    parser.add_argument(
        "--relevance-language",
        default="tr",
        help="Language code used to improve result relevance.",
    )
    parser.add_argument(
        "--order",
        choices=["relevance", "date", "rating", "title", "viewCount"],
        default="relevance",
    )
    return parser.parse_args()


def clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_count(value: Any) -> str:
    text = clean_text(value)
    return text if text.isdigit() else ""


def load_api_key() -> str:
    if load_dotenv is not None:
        load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY was not found. Add it to .env or export it "
            "in the current terminal."
        )
    return api_key


def read_seed_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError(f"No CSV header found in: {path}")

        required = {"artist_name", "song_title", "search_query"}
        missing = required.difference(reader.fieldnames)
        if missing:
            raise ValueError(
                "Input CSV is missing required columns: "
                + ", ".join(sorted(missing))
            )

        rows = []
        for row in reader:
            artist = clean_text(row.get("artist_name"))
            song = clean_text(row.get("song_title"))
            base_query = clean_text(row.get("search_query"))

            if not artist or not song:
                continue

            if not base_query:
                base_query = f"{artist} {song}"

            rows.append(
                {
                    "artist_name": artist,
                    "song_title": song,
                    "search_query": base_query,
                }
            )

    return rows


def build_queries(base_query: str, variant: str) -> list[tuple[str, str]]:
    variants = {
        "base": [("base", base_query)],
        "ai": [("ai", f"{base_query} AI")],
        "suno": [("suno", f"{base_query} Suno")],
        "cover": [("cover", f"{base_query} cover")],
        "all": [
            ("base", base_query),
            ("ai", f"{base_query} AI"),
            ("suno", f"{base_query} Suno"),
            ("cover", f"{base_query} cover"),
        ],
    }
    return variants[variant]


def chunks(items: list[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield items[index : index + size]


def search_candidates(
    youtube: Any,
    query: str,
    max_results: int,
    region_code: str,
    relevance_language: str,
    order: str,
) -> list[dict[str, Any]]:
    response = (
        youtube.search()
        .list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            regionCode=region_code,
            relevanceLanguage=relevance_language,
            order=order,
            safeSearch="none",
        )
        .execute()
    )

    candidates: list[dict[str, Any]] = []

    for rank, item in enumerate(response.get("items", []), start=1):
        video_id = clean_text(item.get("id", {}).get("videoId"))
        snippet = item.get("snippet", {})

        if not video_id:
            continue

        candidates.append(
            {
                "candidate_rank": rank,
                "video_id": video_id,
                "candidate_title": clean_text(snippet.get("title")),
                "channel_title": clean_text(snippet.get("channelTitle")),
                "published_at": clean_text(snippet.get("publishedAt")),
                "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                "description_preview": clean_text(snippet.get("description"))[:500],
            }
        )

    return candidates


def fetch_video_metadata(
    youtube: Any,
    video_ids: list[str],
) -> dict[str, dict[str, str]]:
    metadata: dict[str, dict[str, str]] = {}

    unique_ids = list(dict.fromkeys(video_ids))

    for batch in chunks(unique_ids, 50):
        response = (
            youtube.videos()
            .list(
                part="snippet,statistics,contentDetails",
                id=",".join(batch),
            )
            .execute()
        )

        for item in response.get("items", []):
            video_id = clean_text(item.get("id"))
            snippet = item.get("snippet", {})
            stats = item.get("statistics", {})
            content = item.get("contentDetails", {})

            metadata[video_id] = {
                "view_count": parse_count(stats.get("viewCount")),
                "like_count": parse_count(stats.get("likeCount")),
                "comment_count": parse_count(stats.get("commentCount")),
                "duration": clean_text(content.get("duration")),
                "category_id": clean_text(snippet.get("categoryId")),
                "default_language": clean_text(snippet.get("defaultLanguage")),
                "default_audio_language": clean_text(
                    snippet.get("defaultAudioLanguage")
                ),
            }

    return metadata


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_FIELDS,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()

    if not 1 <= args.results_per_song <= 10:
        raise ValueError("--results-per-song must be between 1 and 10.")
    if args.max_songs < 0:
        raise ValueError("--max-songs cannot be negative.")

    seeds = read_seed_rows(args.input)
    if args.max_songs > 0:
        seeds = seeds[: args.max_songs]

    if not seeds:
        raise ValueError("No valid artist-song seed rows were found.")

    youtube = build(
        "youtube",
        "v3",
        developerKey=load_api_key(),
        cache_discovery=False,
    )

    output_rows: list[dict[str, Any]] = []

    print(f"Input: {args.input}")
    print(f"Seed songs selected: {len(seeds)}")
    print(f"Query variant: {args.query_variant}")
    print(f"Candidates per query: {args.results_per_song}\n")

    try:
        for seed_index, seed in enumerate(seeds, start=1):
            query_pairs = build_queries(
                seed["search_query"],
                args.query_variant,
            )

            for query_variant, query in query_pairs:
                print(
                    f"[{seed_index}/{len(seeds)}] "
                    f"{seed['artist_name']} — {seed['song_title']} "
                    f"({query_variant}: {query})"
                )

                candidates = search_candidates(
                    youtube=youtube,
                    query=query,
                    max_results=args.results_per_song,
                    region_code=args.region_code,
                    relevance_language=args.relevance_language,
                    order=args.order,
                )

                metadata = fetch_video_metadata(
                    youtube,
                    [candidate["video_id"] for candidate in candidates],
                )

                for candidate in candidates:
                    row = {
                        field: "" for field in OUTPUT_FIELDS
                    }
                    row.update(
                        {
                            "artist_name": seed["artist_name"],
                            "seed_song_title": seed["song_title"],
                            "search_query": query,
                            "query_variant": query_variant,
                            "pipeline_status": "needs_manual_review",
                        }
                    )
                    row.update(candidate)
                    row.update(metadata.get(candidate["video_id"], {}))
                    output_rows.append(row)

                # Save after every query so partial work is not lost.
                write_csv(args.output, output_rows)
                print(f"  Found {len(candidates)} candidates.")

    except HttpError as exc:
        write_csv(args.output, output_rows)
        print("\nYouTube API request failed.", file=sys.stderr)
        print(exc, file=sys.stderr)
        print(f"Partial results saved to: {args.output}", file=sys.stderr)
        raise

    # Remove exact duplicate rows caused by repeated search variants.
    deduplicated: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()

    for row in output_rows:
        key = (
            clean_text(row.get("artist_name")),
            clean_text(row.get("seed_song_title")),
            clean_text(row.get("video_id")),
        )
        if key in seen:
            continue
        seen.add(key)
        deduplicated.append(row)

    write_csv(args.output, deduplicated)

    print("\nFinished.")
    print(f"Raw candidate rows: {len(output_rows)}")
    print(f"Deduplicated candidate rows: {len(deduplicated)}")
    print(f"Saved to: {args.output}")
    print("\nNext step: import the output CSV into Google Sheets and review")
    print("manual_valid, language_verified, is_music_video, and AI/Suno status.")


if __name__ == "__main__":
    main()
