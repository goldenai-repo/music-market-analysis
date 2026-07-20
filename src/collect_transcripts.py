from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from pathlib import Path
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi


DEFAULT_INPUT = Path("data/processed/turkish_youtube_review_sample.csv")
DEFAULT_OUTPUT = Path("data/processed/turkish_transcripts.csv")

REQUIRED_FILTER_COLUMNS = [
    "manual_valid",
    "language_verified",
    "is_music_video",
]

OUTPUT_COLUMNS = [
    "video_id",
    "song_title",
    "channel_title",
    "youtube_url",
    "ai_suno_related",
    "channel_type",
    "genre_style",
    "view_count",
    "like_count",
    "comment_count",
    "transcript_available",
    "transcript_language",
    "transcript_language_code",
    "transcript_is_generated",
    "transcript_raw",
    "transcript_clean",
    "transcript_snippet_count",
    "transcript_error_type",
    "transcript_error_message",
]


def normalize_yes_no(value: Any) -> str:
    """Normalize common yes/no values for filtering."""
    return str(value or "").strip().lower()


def is_selected_song(row: dict[str, str], ai_only: bool = False) -> bool:
    """Return True when a row should be included in transcript collection."""
    required_yes = all(
        normalize_yes_no(row.get(column)) == "yes"
        for column in REQUIRED_FILTER_COLUMNS
    )

    if not required_yes:
        return False

    if ai_only:
        return normalize_yes_no(row.get("ai_suno_related")) == "yes"

    return True


def clean_transcript_text(text: str) -> str:
    """Remove line breaks, repeated spaces, and common caption artifacts."""
    text = text.replace("\n", " ")
    text = re.sub(r"\[[^\]]+\]", " ", text)
    text = re.sub(r"\([^)]*music[^)]*\)", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a UTF-8 CSV file."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)

    if not rows:
        raise ValueError(f"Input file is empty: {path}")

    missing_columns = [
        column
        for column in REQUIRED_FILTER_COLUMNS + ["video_id"]
        if column not in rows[0]
    ]

    if missing_columns:
        raise ValueError(
            "Input CSV is missing required columns: "
            + ", ".join(missing_columns)
        )

    return rows


def read_existing_video_ids(path: Path) -> set[str]:
    """Read video IDs already written to the output CSV."""
    if not path.exists():
        return set()

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        return {
            str(row.get("video_id", "")).strip()
            for row in reader
            if str(row.get("video_id", "")).strip()
        }


def choose_transcript(api: YouTubeTranscriptApi, video_id: str):
    """
    Select the best available transcript.

    Priority:
    1. Turkish manually created
    2. Turkish automatically generated
    3. Any Turkish transcript
    4. First available transcript
    """
    transcript_list = api.list(video_id)

    preferred_languages = ["tr", "tr-TR"]

    try:
        return transcript_list.find_manually_created_transcript(
            preferred_languages
        )
    except Exception:
        pass

    try:
        return transcript_list.find_generated_transcript(
            preferred_languages
        )
    except Exception:
        pass

    try:
        return transcript_list.find_transcript(preferred_languages)
    except Exception:
        pass

    available_transcripts = list(transcript_list)

    if not available_transcripts:
        raise RuntimeError("No transcript tracks were found.")

    return available_transcripts[0]


def fetch_transcript(
    api: YouTubeTranscriptApi,
    row: dict[str, str],
) -> dict[str, str]:
    """Fetch one transcript and return an output row."""
    video_id = str(row.get("video_id", "")).strip()

    base_result = {
        "video_id": video_id,
        "song_title": row.get("song_title", ""),
        "channel_title": row.get("channel_title", ""),
        "youtube_url": row.get("youtube_url", ""),
        "ai_suno_related": row.get("ai_suno_related", ""),
        "channel_type": row.get("channel_type", ""),
        "genre_style": row.get("genre_style", ""),
        "view_count": row.get("view_count", ""),
        "like_count": row.get("like_count", ""),
        "comment_count": row.get("comment_count", ""),
        "transcript_available": "no",
        "transcript_language": "",
        "transcript_language_code": "",
        "transcript_is_generated": "",
        "transcript_raw": "",
        "transcript_clean": "",
        "transcript_snippet_count": "0",
        "transcript_error_type": "",
        "transcript_error_message": "",
    }

    try:
        transcript = choose_transcript(api, video_id)
        fetched = transcript.fetch()

        snippets = [snippet.text.strip() for snippet in fetched if snippet.text]
        raw_text = "\n".join(snippets)
        clean_text = clean_transcript_text(" ".join(snippets))

        base_result.update(
            {
                "transcript_available": "yes",
                "transcript_language": transcript.language,
                "transcript_language_code": transcript.language_code,
                "transcript_is_generated": (
                    "yes" if transcript.is_generated else "no"
                ),
                "transcript_raw": raw_text,
                "transcript_clean": clean_text,
                "transcript_snippet_count": str(len(snippets)),
            }
        )

    except Exception as error:
        base_result.update(
            {
                "transcript_error_type": type(error).__name__,
                "transcript_error_message": clean_transcript_text(str(error)),
            }
        )

    return base_result


def append_result(path: Path, result: dict[str, str]) -> None:
    """Append one result immediately so progress is not lost."""
    path.parent.mkdir(parents=True, exist_ok=True)
    file_exists = path.exists() and path.stat().st_size > 0

    with path.open("a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_COLUMNS)

        if not file_exists:
            writer.writeheader()

        writer.writerow(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect YouTube transcripts for reviewed Turkish songs."
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Input review CSV. Default: {DEFAULT_INPUT}",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Output transcript CSV. Default: {DEFAULT_OUTPUT}",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Maximum number of new videos to process. Default: 10",
    )

    parser.add_argument(
        "--sleep",
        type=float,
        default=2.0,
        help="Seconds to wait between requests. Default: 2",
    )

    parser.add_argument(
        "--ai-only",
        action="store_true",
        help="Only process rows where ai_suno_related=yes.",
    )

    parser.add_argument(
        "--retry-existing",
        action="store_true",
        help="Process videos already present in the output CSV.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        rows = read_csv(args.input)
    except (FileNotFoundError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    selected_rows = [
        row for row in rows if is_selected_song(row, ai_only=args.ai_only)
    ]

    existing_video_ids = (
        set()
        if args.retry_existing
        else read_existing_video_ids(args.output)
    )

    pending_rows = [
        row
        for row in selected_rows
        if str(row.get("video_id", "")).strip() not in existing_video_ids
    ]

    if args.limit > 0:
        pending_rows = pending_rows[: args.limit]

    print(f"Total input rows: {len(rows)}")
    print(f"Eligible reviewed songs: {len(selected_rows)}")
    print(f"Already processed: {len(existing_video_ids)}")
    print(f"Videos to process now: {len(pending_rows)}")
    print()

    if not pending_rows:
        print("No new videos to process.")
        return 0

    api = YouTubeTranscriptApi()

    success_count = 0
    failure_count = 0

    for index, row in enumerate(pending_rows, start=1):
        video_id = str(row.get("video_id", "")).strip()
        song_title = row.get("song_title", "")

        print(
            f"[{index}/{len(pending_rows)}] "
            f"Fetching: {song_title} ({video_id})"
        )

        result = fetch_transcript(api, row)
        append_result(args.output, result)

        if result["transcript_available"] == "yes":
            success_count += 1
            print(
                "  Success:"
                f" language={result['transcript_language_code']},"
                f" generated={result['transcript_is_generated']},"
                f" snippets={result['transcript_snippet_count']}"
            )
        else:
            failure_count += 1
            print(
                "  Failed:"
                f" {result['transcript_error_type']} - "
                f"{result['transcript_error_message'][:150]}"
            )

        if index < len(pending_rows):
            time.sleep(args.sleep)

    print()
    print("Transcript collection complete.")
    print(f"Successful: {success_count}")
    print(f"Failed: {failure_count}")
    print(f"Output: {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())