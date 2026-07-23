"""
Prepare an analysis-ready transcript dataset.

This script filters the manually reviewed transcript dataset and
keeps only songs that:

- have usable transcript quality
- have verified Turkish lyrics

The output is used as the input for lyric-level embedding.
"""
from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path


DEFAULT_INPUT = Path(
    "data/processed/turkish_transcript_review_21.csv"
)
DEFAULT_OUTPUT = Path(
    "data/processed/turkish_transcript_analysis_ready.csv"
)

USABLE_QUALITIES = {
    "good",
    "usable_with_noise",
}

REQUIRED_COLUMNS = {
    "video_id",
    "transcript_clean",
    "transcript_quality",
    "lyric_language_verified",
}


def normalize(value: str | None) -> str:
    """Normalize manually entered categorical values."""
    return (value or "").strip().lower()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError(f"Input CSV has no header: {path}")

        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    missing_columns = REQUIRED_COLUMNS.difference(fieldnames)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(
            f"Input CSV is missing required columns: {missing_text}"
        )

    return rows, fieldnames


def get_exclusion_reason(row: dict[str, str]) -> str | None:
    """
    Return None when a row is analysis-ready.
    Otherwise, return the primary reason it was excluded.
    """
    transcript_quality = normalize(row.get("transcript_quality"))
    language_verified = normalize(row.get("lyric_language_verified"))
    transcript_clean = (row.get("transcript_clean") or "").strip()

    if transcript_quality not in USABLE_QUALITIES:
        return f"transcript_quality={transcript_quality or 'blank'}"

    if language_verified != "yes":
        return (
            "lyric_language_verified="
            f"{language_verified or 'blank'}"
        )

    if not transcript_clean:
        return "empty_transcript_clean"

    return None


def filter_analysis_ready(
    rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], Counter[str]]:
    ready_rows: list[dict[str, str]] = []
    exclusion_counts: Counter[str] = Counter()

    for row in rows:
        exclusion_reason = get_exclusion_reason(row)

        if exclusion_reason is None:
            ready_rows.append(row)
        else:
            exclusion_counts[exclusion_reason] += 1

    return ready_rows, exclusion_counts


def write_csv(
    path: Path,
    rows: list[dict[str, str]],
    fieldnames: list[str],
    overwrite: bool,
) -> None:
    if path.exists() and not overwrite:
        raise FileExistsError(
            f"Output already exists: {path}\n"
            "Use --overwrite to replace it."
        )

    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames,
            extrasaction="ignore",
        )
        writer.writeheader()
        writer.writerows(rows)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Filter manually reviewed transcripts into an "
            "analysis-ready CSV."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=f"Reviewed transcript CSV. Default: {DEFAULT_INPUT}",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"Analysis-ready output CSV. Default: {DEFAULT_OUTPUT}",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace the output file if it already exists.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        rows, fieldnames = read_csv(args.input)
        ready_rows, exclusion_counts = filter_analysis_ready(rows)

        write_csv(
            path=args.output,
            rows=ready_rows,
            fieldnames=fieldnames,
            overwrite=args.overwrite,
        )

    except (FileNotFoundError, FileExistsError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print("Analysis-ready dataset created.")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}")
    print(f"Total reviewed rows: {len(rows)}")
    print(f"Analysis-ready rows: {len(ready_rows)}")
    print(f"Excluded rows: {len(rows) - len(ready_rows)}")

    if exclusion_counts:
        print("\nExclusion summary:")
        for reason, count in sorted(exclusion_counts.items()):
            print(f"- {reason}: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())