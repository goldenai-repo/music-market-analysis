"""Merge reviewed expansion transcripts with the existing analysis-ready dataset."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

BASE_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_transcript_analysis_ready.csv"
)

EXPANSION_REVIEW_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_expansion_transcript_review.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_transcript_analysis_ready_expanded.csv"
)

USABLE_QUALITIES = {
    "good",
    "usable_with_noise",
}


def normalize(value: Any) -> str:
    """Convert a CSV value to normalized lowercase text."""
    return str(value or "").strip().lower()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    """Read a CSV file and return its rows and field names."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"CSV has no header: {path}")

        rows = list(reader)
        fieldnames = list(reader.fieldnames)

    return rows, fieldnames


def expansion_row_is_usable(row: dict[str, str]) -> bool:
    """Return True when an expansion transcript is ready for analysis."""
    return (
        normalize(row.get("transcript_available")) == "yes"
        and normalize(row.get("transcript_quality"))
        in USABLE_QUALITIES
        and normalize(row.get("lyric_language_verified")) == "yes"
        and normalize(row.get("transcript_language")) in {"tr", "tr-tr"}
        and bool(str(row.get("transcript_clean") or "").strip())
    )


def standardize_expansion_row(
    row: dict[str, str],
) -> dict[str, str]:
    """Map expansion fields onto the original analysis-ready schema."""
    standardized = dict(row)

    song_title = str(row.get("song_title") or "").strip()

    if not standardized.get("seed_song_title"):
        standardized["seed_song_title"] = song_title

    if not standardized.get("candidate_title"):
        standardized["candidate_title"] = song_title

    if not standardized.get("artist_name"):
        standardized["artist_name"] = ""

    standardized["pipeline_status"] = "analysis_ready_expansion"

    return standardized


def get_video_id(row: dict[str, str]) -> str:
    """Return a stripped YouTube video ID."""
    return str(row.get("video_id") or "").strip()


def main() -> None:
    base_rows, base_fields = read_csv(BASE_FILE)
    expansion_rows, expansion_fields = read_csv(
        EXPANSION_REVIEW_FILE
    )

    usable_expansion_rows = [
        standardize_expansion_row(row)
        for row in expansion_rows
        if expansion_row_is_usable(row)
    ]

    existing_video_ids = {
        get_video_id(row)
        for row in base_rows
        if get_video_id(row)
    }

    new_expansion_rows = [
        row
        for row in usable_expansion_rows
        if get_video_id(row) not in existing_video_ids
    ]

    combined_rows = base_rows + new_expansion_rows

    # Preserve all columns found in either input file.
    output_fields = list(
        dict.fromkeys(
            base_fields
            + expansion_fields
            + [
                "artist_name",
                "seed_song_title",
                "candidate_title",
                "pipeline_status",
            ]
        )
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=output_fields,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(combined_rows)

    print(f"Existing analysis-ready rows: {len(base_rows)}")
    print(f"Reviewed expansion rows: {len(expansion_rows)}")
    print(f"Usable expansion rows: {len(usable_expansion_rows)}")
    print(
        "New non-duplicate expansion rows:",
        len(new_expansion_rows),
    )
    print(f"Final combined rows: {len(combined_rows)}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()