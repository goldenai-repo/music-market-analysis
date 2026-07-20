from __future__ import annotations

import csv
from pathlib import Path


INPUT_PATH = Path("data/processed/turkish_transcripts.csv")
OUTPUT_PATH = Path("data/processed/turkish_transcript_review_sample.csv")

NEW_COLUMNS = [
    "transcript_quality",
    "lyric_language_verified",
    "transcript_review_notes",
]


def suggest_review_values(row: dict[str, str]) -> tuple[str, str, str]:
    """
    Generate conservative initial suggestions.

    These values are only starting points and should still be manually checked.
    """
    available = row.get("transcript_available", "").strip().lower()
    language_code = row.get("transcript_language_code", "").strip().lower()
    title = row.get("song_title", "").strip().lower()

    try:
        snippet_count = int(row.get("transcript_snippet_count", "0") or 0)
    except ValueError:
        snippet_count = 0

    if available != "yes":
        return (
            "unavailable",
            "unclear",
            row.get("transcript_error_type", "") or "Transcript unavailable",
        )

    if language_code and not language_code.startswith("tr"):
        return (
            "wrong_language",
            "no",
            f"Transcript language is {language_code or 'unknown'}, not Turkish.",
        )

    if "full album" in title or "compilation" in title or "playlist" in title:
        return (
            "not_song_level",
            "unclear",
            "Video may contain multiple songs; exclude from song-level analysis.",
        )

    if snippet_count < 10:
        return (
            "too_short",
            "unclear",
            f"Transcript contains only {snippet_count} snippets; inspect manually.",
        )

    return (
        "needs_manual_review",
        "unclear",
        "",
    )


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        original_columns = reader.fieldnames or []

    output_columns = original_columns.copy()

    for column in NEW_COLUMNS:
        if column not in output_columns:
            output_columns.append(column)

    for row in rows:
        quality, language_verified, notes = suggest_review_values(row)

        row["transcript_quality"] = (
            row.get("transcript_quality", "").strip() or quality
        )
        row["lyric_language_verified"] = (
            row.get("lyric_language_verified", "").strip()
            or language_verified
        )
        row["transcript_review_notes"] = (
            row.get("transcript_review_notes", "").strip() or notes
        )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=output_columns)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Input rows: {len(rows)}")
    print(f"Review file created: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()