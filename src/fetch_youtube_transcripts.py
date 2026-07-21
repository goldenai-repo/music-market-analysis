"""
Batch-fetch YouTube transcripts for manually validated Turkish music videos.

Run from the project root:

    python src/fetch_youtube_transcripts.py

Optional arguments:

    python src/fetch_youtube_transcripts.py --max-videos 5
    python src/fetch_youtube_transcripts.py --max-videos 20 --delay 3
    python src/fetch_youtube_transcripts.py --max-videos 0

Using --max-videos 0 processes all eligible rows.
"""

from __future__ import annotations

import argparse
import csv
import re
import time
from pathlib import Path
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi


DEFAULT_INPUT_PATH = Path(
    "data/processed/turkish_transcript_input.csv"
)

DEFAULT_OUTPUT_PATH = Path(
    "data/processed/turkish_transcripts_21.csv"
)

TRANSCRIPT_FIELDS = [
    "transcript_available",
    "transcript_language",
    "transcript_is_generated",
    "transcript_raw",
    "transcript_clean",
    "transcript_error",
]


def normalize_value(value: Any) -> str:
    """Normalize CSV values for reliable yes/no comparisons."""
    return str(value or "").strip().lower()


def is_eligible_song(row: dict[str, str]) -> bool:
    """Return True for rows already validated as Turkish music videos."""
    return (
        normalize_value(row.get("manual_valid")) == "yes"
        and normalize_value(row.get("language_verified")) == "yes"
        and normalize_value(row.get("is_music_video")) == "yes"
    )


def clean_transcript(text: str) -> str:
    """
    Apply conservative transcript cleaning.

    This removes common subtitle markers but preserves repeated lyrics,
    because repetitions may be meaningful in later lyric analysis.
    """
    cleaned = text

    noise_patterns = [
        r"\[\s*müzik\s*\]",
        r"\[\s*music\s*\]",
        r"\[\s*alkış\s*\]",
        r"\[\s*applause\s*\]",
        r"\[\s*instrumental\s*\]",
        r"\[\s*enstrümantal\s*\]",
    ]

    for pattern in noise_patterns:
        cleaned = re.sub(
            pattern,
            " ",
            cleaned,
            flags=re.IGNORECASE,
        )

    cleaned = cleaned.replace(">>", " ")
    cleaned = cleaned.replace("♪", " ")
    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def fetch_one_transcript(
    api: YouTubeTranscriptApi,
    video_id: str,
) -> dict[str, str]:
    """Fetch and clean one transcript without stopping the batch on failure."""
    try:
        transcript = api.fetch(
            video_id,
            languages=["tr", "en"],
        )

        transcript_rows = transcript.to_raw_data()

        raw_text = " ".join(
            str(item.get("text", "")).strip()
            for item in transcript_rows
            if str(item.get("text", "")).strip()
        )

        return {
            "transcript_available": "yes",
            "transcript_language": str(
                transcript.language_code or ""
            ),
            "transcript_is_generated": (
                "yes" if transcript.is_generated else "no"
            ),
            "transcript_raw": raw_text,
            "transcript_clean": clean_transcript(raw_text),
            "transcript_error": "",
        }

    except Exception as exc:
        return {
            "transcript_available": "no",
            "transcript_language": "",
            "transcript_is_generated": "",
            "transcript_raw": "",
            "transcript_clean": "",
            "transcript_error": (
                f"{type(exc).__name__}: {str(exc)}"
            ),
        }


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Read a UTF-8 CSV and return rows plus original field names."""
    if not path.exists():
        raise FileNotFoundError(
            f"Input CSV was not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(
                f"No header row was found in: {path}"
            )

        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    required_fields = {
        "video_id",
        "manual_valid",
        "language_verified",
        "is_music_video",
    }

    missing_fields = required_fields.difference(fieldnames)

    if missing_fields:
        missing_text = ", ".join(sorted(missing_fields))
        raise ValueError(
            f"Input CSV is missing required columns: {missing_text}"
        )

    return rows, fieldnames


def write_csv(
    path: Path,
    rows: list[dict[str, str]],
    original_fieldnames: list[str],
) -> None:
    """Write results without modifying the source CSV."""
    path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = list(original_fieldnames)

    for field in TRANSCRIPT_FIELDS:
        if field not in fieldnames:
            fieldnames.append(field)

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Fetch transcripts for validated Turkish music videos."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT_PATH,
        help="Path to the reviewed input CSV.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_PATH,
        help="Path for the transcript-enriched output CSV.",
    )

    parser.add_argument(
        "--max-videos",
        type=int,
        default=0,
        help=(
            "Maximum number of eligible videos to process. "
            "Use 0 to process all eligible videos."
        ),
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=2.0,
        help="Seconds to wait between transcript requests.",
    )

    return parser.parse_args()


def main() -> None:
    args = parse_arguments()

    if args.max_videos < 0:
        raise ValueError("--max-videos cannot be negative.")

    if args.delay < 0:
        raise ValueError("--delay cannot be negative.")

    rows, original_fieldnames = read_csv(args.input)

    eligible_rows = [
        row for row in rows if is_eligible_song(row)
    ]

    if args.max_videos > 0:
        eligible_rows = eligible_rows[: args.max_videos]

    if not eligible_rows:
        raise ValueError(
            "No eligible rows were found. Check whether the review "
            "columns contain the value 'yes'."
        )

    print(f"Input file: {args.input}")
    print(f"Eligible videos selected: {len(eligible_rows)}")
    print(f"Output file: {args.output}\n")

    api = YouTubeTranscriptApi()
    output_rows: list[dict[str, str]] = []

    successful = 0
    failed = 0

    for index, row in enumerate(eligible_rows, start=1):
        video_id = str(row.get("video_id", "")).strip()
        song_title = (str(row.get("seed_song_title", "")).strip()
    or str(row.get("candidate_title", "")).strip()
    or str(row.get("song_title", "")).strip()
)

        if not video_id:
            result = {
                "transcript_available": "no",
                "transcript_language": "",
                "transcript_is_generated": "",
                "transcript_raw": "",
                "transcript_clean": "",
                "transcript_error": "MissingVideoId",
            }
        else:
            print(
                f"[{index}/{len(eligible_rows)}] "
                f"{song_title or '(untitled)'} — {video_id}"
            )

            result = fetch_one_transcript(
                api=api,
                video_id=video_id,
            )

        enriched_row = dict(row)
        enriched_row.update(result)
        output_rows.append(enriched_row)

        if result["transcript_available"] == "yes":
            successful += 1
            clean_length = len(result["transcript_clean"])

            print(
                "  Success:",
                f"language={result['transcript_language']},",
                f"generated={result['transcript_is_generated']},",
                f"clean_characters={clean_length}",
            )
        else:
            failed += 1
            print(
                "  Failed:",
                result["transcript_error"].splitlines()[0],
            )

        # Save after every request so partial progress survives interruption.
        write_csv(
            path=args.output,
            rows=output_rows,
            original_fieldnames=original_fieldnames,
        )

        if index < len(eligible_rows):
            time.sleep(args.delay)

    print("\nFinished.")
    print(f"Successful transcripts: {successful}")
    print(f"Failed or unavailable: {failed}")
    print(f"Saved results to: {args.output}")


if __name__ == "__main__":
    main()