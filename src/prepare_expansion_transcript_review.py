"""Prepare a review CSV for the transcript expansion batch."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_expansion_transcript_review.csv"
)

OUTPUT_FILE = INPUT_FILE

REVIEW_BY_VIDEO_ID = {
    "Tb-zjsEqr1k": (
        "good",
        "yes",
        "Clear Turkish lyrics; suitable for analysis.",
    ),
    "GR6r-jIryH0": (
        "usable_with_noise",
        "yes",
        "Minor ASR errors; main lyrical meaning remains usable.",
    ),
    "_NoTqg152B0": (
        "good",
        "yes",
        "Clear Turkish lyrics; suitable for analysis.",
    ),
    "YqNqw4o-JBY": (
        "good",
        "yes",
        "Clear Turkish lyrics; suitable for analysis.",
    ),
    "icZ-OlVSvb4": (
        "good",
        "yes",
        "Clear Turkish lyrics; suitable for analysis.",
    ),
    "IQWkS1GyFRM": (
        "usable_with_noise",
        "yes",
        "Moderate ASR errors; main themes remain identifiable.",
    ),
    "9oZIOfx87Ww": (
        "unusable",
        "yes",
        "Severe ASR noise; excluded from lyric analysis.",
    ),
    "cQKR_bcE2ug": (
        "wrong_language",
        "no",
        "English transcript; not Turkish lyrics.",
    ),
}


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"File not found: {INPUT_FILE}")

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("CSV has no header.")

        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    new_fields = [
        "transcript_quality",
        "lyric_language_verified",
        "transcript_review_notes",
    ]

    for field in new_fields:
        if field not in fieldnames:
            fieldnames.append(field)

    for row in rows:
        video_id = (row.get("video_id") or "").strip()

        if video_id in REVIEW_BY_VIDEO_ID:
            quality, language_verified, notes = (
                REVIEW_BY_VIDEO_ID[video_id]
            )
        elif (row.get("transcript_available") or "").strip().lower() == "no":
            quality = "unavailable"
            language_verified = "unclear"
            notes = "Transcript unavailable."
        else:
            quality = ""
            language_verified = ""
            notes = ""

        row["transcript_quality"] = quality
        row["lyric_language_verified"] = language_verified
        row["transcript_review_notes"] = notes

    with OUTPUT_FILE.open(
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

    print(f"Rows updated: {len(rows)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()