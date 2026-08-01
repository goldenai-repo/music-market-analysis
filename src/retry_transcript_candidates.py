"""Retry alternative YouTube candidates for songs with failed transcripts.

Inputs:
    data/processed/turkish_artist_song_candidates_reviewed.csv
    data/processed/turkish_transcript_review_21.csv

Outputs:
    data/processed/turkish_transcript_rescue_results.csv
    data/processed/turkish_transcript_rescue_success.csv

The script identifies songs whose primary YouTube video produced an unavailable
or wrong-language transcript, then tries reviewed alternative candidates in
candidate-rank order.

Only one successful alternative is retained per song.
"""

from __future__ import annotations

import csv
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from youtube_transcript_api import YouTubeTranscriptApi


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATES_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_artist_song_candidates_reviewed.csv"
)

TRANSCRIPT_REVIEW_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_transcript_review_21.csv"
)

RESULTS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_transcript_rescue_results.csv"
)

SUCCESS_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_transcript_rescue_success.csv"
)


FAILED_QUALITIES = {
    "unavailable",
    "wrong_language",
}

PREFERRED_LANGUAGE_CODES = [
    "tr",
    "tr-TR",
]

REQUEST_DELAY_SECONDS = 1.0


def normalize_value(value: Any) -> str:
    """Convert a CSV value to a normalized lowercase string."""
    return str(value or "").strip().lower()


def parse_rank(value: Any) -> int:
    """Parse candidate rank safely."""
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return 999


def clean_transcript_text(text: str) -> str:
    """Remove common non-lyrical transcript markers and normalize spacing."""
    if not text:
        return ""

    marker_patterns = [
        r"\[müzik\]",
        r"\[music\]",
        r"\[alkış\]",
        r"\[applause\]",
        r"\[gülüşmeler\]",
        r"\[laughter\]",
    ]

    cleaned = text

    for pattern in marker_patterns:
        cleaned = re.sub(
            pattern,
            " ",
            cleaned,
            flags=re.IGNORECASE,
        )

    cleaned = re.sub(r"\s+", " ", cleaned)

    return cleaned.strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    """Read a CSV file using UTF-8 with optional BOM support."""
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")

        return list(reader)


def write_csv(
    path: Path,
    rows: list[dict[str, Any]],
    fieldnames: list[str],
) -> None:
    """Write rows to a CSV file."""
    path.parent.mkdir(parents=True, exist_ok=True)

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


def song_key(
    artist_name: str,
    song_title: str,
) -> tuple[str, str]:
    """Create a matching key for artist and song title."""
    return (
        normalize_value(artist_name),
        normalize_value(song_title),
    )


def identify_failed_songs(
    review_rows: list[dict[str, str]],
) -> dict[tuple[str, str], dict[str, str]]:
    """Return songs requiring an alternative transcript attempt."""
    failed: dict[tuple[str, str], dict[str, str]] = {}

    for row in review_rows:
        quality = normalize_value(row.get("transcript_quality"))

        if quality not in FAILED_QUALITIES:
            continue

        artist = row.get("artist_name", "")
        title = (
            row.get("seed_song_title")
            or row.get("song_title")
            or ""
        )

        if not artist or not title:
            print(
                "Warning: failed row is missing artist or song title:",
                row.get("video_id", ""),
            )
            continue

        failed[song_key(artist, title)] = row

    return failed


def candidate_is_eligible(row: dict[str, str]) -> bool:
    """Check whether an alternative candidate passed manual review."""
    manual_valid = normalize_value(row.get("manual_valid"))
    language_verified = normalize_value(row.get("language_verified"))
    is_music_video = normalize_value(row.get("is_music_video"))
    selected_for_analysis = normalize_value(
        row.get("selected_for_analysis")
    )

    if manual_valid != "yes":
        return False

    if language_verified != "yes":
        return False

    if is_music_video != "yes":
        return False

    # Exclude the primary video already used in the baseline.
    if selected_for_analysis == "yes":
        return False

    return True


def group_alternative_candidates(
    candidate_rows: list[dict[str, str]],
    failed_songs: dict[tuple[str, str], dict[str, str]],
) -> dict[tuple[str, str], list[dict[str, str]]]:
    """Group eligible alternatives for failed songs."""
    grouped: dict[
        tuple[str, str],
        list[dict[str, str]],
    ] = defaultdict(list)

    for row in candidate_rows:
        artist = row.get("artist_name", "")
        title = row.get("seed_song_title", "")
        key = song_key(artist, title)

        if key not in failed_songs:
            continue

        if not candidate_is_eligible(row):
            continue

        video_id = str(row.get("video_id") or "").strip()

        if not video_id:
            continue

        grouped[key].append(row)

    for key in grouped:
        grouped[key].sort(
            key=lambda row: parse_rank(row.get("candidate_rank"))
        )

    return grouped


def get_transcript_language_code(
    transcript: Any,
) -> str:
    """Return a transcript object's language code safely."""
    return str(
        getattr(transcript, "language_code", "") or ""
    ).strip()


def get_is_generated(
    transcript: Any,
) -> bool:
    """Return whether a transcript is auto-generated."""
    return bool(getattr(transcript, "is_generated", False))


def flatten_fetched_transcript(
    fetched: Any,
) -> str:
    """Convert fetched transcript data into one text string."""
    pieces: list[str] = []

    for item in fetched:
        if hasattr(item, "text"):
            text = item.text
        elif isinstance(item, dict):
            text = item.get("text", "")
        else:
            text = ""

        text = str(text or "").strip()

        if text:
            pieces.append(text)

    return " ".join(pieces).strip()


def fetch_turkish_transcript(
    video_id: str,
) -> dict[str, Any]:
    """Fetch a Turkish transcript for one YouTube video."""
    api = YouTubeTranscriptApi()

    try:
        transcript_list = api.list(video_id)
    except AttributeError:
        # Compatibility with older youtube-transcript-api versions.
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    available_languages = [
        get_transcript_language_code(transcript)
        for transcript in transcript_list
    ]

    selected_transcript = None

    # Prefer a manually created Turkish transcript.
    for transcript in transcript_list:
        language_code = get_transcript_language_code(transcript)

        if (
            language_code in PREFERRED_LANGUAGE_CODES
            and not get_is_generated(transcript)
        ):
            selected_transcript = transcript
            break

    # Otherwise accept an auto-generated Turkish transcript.
    if selected_transcript is None:
        for transcript in transcript_list:
            language_code = get_transcript_language_code(transcript)

            if language_code in PREFERRED_LANGUAGE_CODES:
                selected_transcript = transcript
                break

    if selected_transcript is None:
        return {
            "success": False,
            "transcript_available": "no",
            "transcript_language": "",
            "transcript_is_generated": "",
            "transcript_raw": "",
            "transcript_clean": "",
            "transcript_error": (
                "No Turkish transcript found. "
                f"Available languages: {available_languages}"
            ),
        }

    fetched = selected_transcript.fetch()
    raw_text = flatten_fetched_transcript(fetched)
    clean_text = clean_transcript_text(raw_text)

    if not clean_text:
        return {
            "success": False,
            "transcript_available": "no",
            "transcript_language": get_transcript_language_code(
                selected_transcript
            ),
            "transcript_is_generated": (
                "yes"
                if get_is_generated(selected_transcript)
                else "no"
            ),
            "transcript_raw": raw_text,
            "transcript_clean": clean_text,
            "transcript_error": "Transcript was empty after cleaning.",
        }

    return {
        "success": True,
        "transcript_available": "yes",
        "transcript_language": get_transcript_language_code(
            selected_transcript
        ),
        "transcript_is_generated": (
            "yes"
            if get_is_generated(selected_transcript)
            else "no"
        ),
        "transcript_raw": raw_text,
        "transcript_clean": clean_text,
        "transcript_error": "",
    }


def build_result_row(
    candidate: dict[str, str],
    fetch_result: dict[str, Any],
    attempt_number: int,
    rescue_status: str,
) -> dict[str, Any]:
    """Combine candidate metadata and transcript fetch results."""
    return {
        "artist_name": candidate.get("artist_name", ""),
        "seed_song_title": candidate.get(
            "seed_song_title",
            "",
        ),
        "candidate_rank": candidate.get(
            "candidate_rank",
            "",
        ),
        "attempt_number": attempt_number,
        "video_id": candidate.get("video_id", ""),
        "candidate_title": candidate.get(
            "candidate_title",
            "",
        ),
        "channel_title": candidate.get(
            "channel_title",
            "",
        ),
        "published_at": candidate.get(
            "published_at",
            "",
        ),
        "youtube_url": candidate.get(
            "youtube_url",
            "",
        ),
        "view_count": candidate.get(
            "view_count",
            "",
        ),
        "like_count": candidate.get(
            "like_count",
            "",
        ),
        "comment_count": candidate.get(
            "comment_count",
            "",
        ),
        "duration": candidate.get(
            "duration",
            "",
        ),
        "channel_type": candidate.get(
            "channel_type",
            "",
        ),
        "review_notes": candidate.get(
            "review_notes",
            "",
        ),
        "rescue_status": rescue_status,
        "transcript_available": fetch_result.get(
            "transcript_available",
            "no",
        ),
        "transcript_language": fetch_result.get(
            "transcript_language",
            "",
        ),
        "transcript_is_generated": fetch_result.get(
            "transcript_is_generated",
            "",
        ),
        "transcript_raw": fetch_result.get(
            "transcript_raw",
            "",
        ),
        "transcript_clean": fetch_result.get(
            "transcript_clean",
            "",
        ),
        "transcript_error": fetch_result.get(
            "transcript_error",
            "",
        ),
        "transcript_quality": "",
        "lyric_language_verified": "",
        "transcript_review_notes": "",
    }


def main() -> None:
    candidate_rows = read_csv(CANDIDATES_FILE)
    review_rows = read_csv(TRANSCRIPT_REVIEW_FILE)

    failed_songs = identify_failed_songs(review_rows)

    alternatives = group_alternative_candidates(
        candidate_rows,
        failed_songs,
    )

    results: list[dict[str, Any]] = []
    successes: list[dict[str, Any]] = []

    print(f"Failed songs identified: {len(failed_songs)}")
    print(
        "Failed songs with eligible alternatives:",
        len(alternatives),
    )

    for index, (key, failed_row) in enumerate(
        failed_songs.items(),
        start=1,
    ):
        artist_name, song_title = key
        song_candidates = alternatives.get(key, [])

        print()
        print(
            f"[{index}/{len(failed_songs)}] "
            f"{failed_row.get('artist_name', artist_name)}"
            f" — "
            f"{failed_row.get('seed_song_title', song_title)}"
        )

        if not song_candidates:
            print("  No eligible alternative candidates.")

            results.append(
                {
                    "artist_name": failed_row.get(
                        "artist_name",
                        "",
                    ),
                    "seed_song_title": (
                        failed_row.get("seed_song_title")
                        or failed_row.get("song_title")
                        or ""
                    ),
                    "candidate_rank": "",
                    "attempt_number": "",
                    "video_id": "",
                    "candidate_title": "",
                    "channel_title": "",
                    "published_at": "",
                    "youtube_url": "",
                    "view_count": "",
                    "like_count": "",
                    "comment_count": "",
                    "duration": "",
                    "channel_type": "",
                    "review_notes": "",
                    "rescue_status": "no_eligible_alternative",
                    "transcript_available": "no",
                    "transcript_language": "",
                    "transcript_is_generated": "",
                    "transcript_raw": "",
                    "transcript_clean": "",
                    "transcript_error": (
                        "No manually validated alternative candidate."
                    ),
                    "transcript_quality": "",
                    "lyric_language_verified": "",
                    "transcript_review_notes": "",
                }
            )
            continue

        rescued = False

        for attempt_number, candidate in enumerate(
            song_candidates,
            start=1,
        ):
            video_id = str(
                candidate.get("video_id") or ""
            ).strip()

            rank = candidate.get("candidate_rank", "")
            title = candidate.get("candidate_title", "")

            print(
                f"  Trying rank {rank}: "
                f"{video_id} — {title}"
            )

            try:
                fetch_result = fetch_turkish_transcript(
                    video_id
                )

                if fetch_result["success"]:
                    rescue_status = "rescued"
                else:
                    rescue_status = "failed"

            except Exception as error:
                fetch_result = {
                    "success": False,
                    "transcript_available": "no",
                    "transcript_language": "",
                    "transcript_is_generated": "",
                    "transcript_raw": "",
                    "transcript_clean": "",
                    "transcript_error": (
                        f"{type(error).__name__}: {error}"
                    ),
                }
                rescue_status = "failed"

            result_row = build_result_row(
                candidate,
                fetch_result,
                attempt_number,
                rescue_status,
            )

            results.append(result_row)

            if fetch_result["success"]:
                successes.append(result_row)
                rescued = True
                print(
                    "  Success:",
                    fetch_result["transcript_language"],
                    "generated="
                    f"{fetch_result['transcript_is_generated']}",
                )
                break

            print(
                "  Failed:",
                fetch_result["transcript_error"],
            )

            time.sleep(REQUEST_DELAY_SECONDS)

        if not rescued:
            print("  No Turkish transcript rescued.")

    fieldnames = [
        "artist_name",
        "seed_song_title",
        "candidate_rank",
        "attempt_number",
        "video_id",
        "candidate_title",
        "channel_title",
        "published_at",
        "youtube_url",
        "view_count",
        "like_count",
        "comment_count",
        "duration",
        "channel_type",
        "review_notes",
        "rescue_status",
        "transcript_available",
        "transcript_language",
        "transcript_is_generated",
        "transcript_raw",
        "transcript_clean",
        "transcript_error",
        "transcript_quality",
        "lyric_language_verified",
        "transcript_review_notes",
    ]

    write_csv(
        RESULTS_FILE,
        results,
        fieldnames,
    )

    write_csv(
        SUCCESS_FILE,
        successes,
        fieldnames,
    )

    print()
    print("Rescue complete.")
    print(f"Failed baseline songs: {len(failed_songs)}")
    print(
        "Songs with alternatives:",
        len(alternatives),
    )
    print(f"Songs rescued: {len(successes)}")
    print(f"All attempts: {RESULTS_FILE}")
    print(f"Successful rescues: {SUCCESS_FILE}")


if __name__ == "__main__":
    main()