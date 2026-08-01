"""Prepare a small expansion batch for transcript collection."""

from __future__ import annotations

import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_youtube_review_sample_backup.csv"
)

OUTPUT_FILE = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "turkish_expansion_transcript_input.csv"
)


SELECTED_VIDEO_IDS = [
    "Tb-zjsEqr1k",   # İnceden İnceden
    "GR6r-jIryH0",   # Heyecan
    "_NoTqg152B0",   # Yerinde Dur
    "rYJjgfCfBOU",   # Ey Aşk
    "YqNqw4o-JBY",   # Kırk Yılda Bir Gibisin
    "icZ-OlVSvb4",   # Bangır Bangır
    "IQWkS1GyFRM",   # Bir Ay Doğar
    "9oZIOfx87Ww",   # Bulut Gelir
    "mbY17Lr_wu4",   # Üsküdara
    "ih9nX3KZVfU",   # Ceddin Deden
    "Z4fKe_EGw7k",   # ER TURAN
    "cQKR_bcE2ug",   # Hey Gidi Dünya Hey
]


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_FILE}")

    selected_ids = set(SELECTED_VIDEO_IDS)
    selected_rows: list[dict[str, str]] = []

    with INPUT_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        if reader.fieldnames is None:
            raise ValueError("Input CSV has no header.")

        input_fields = list(reader.fieldnames)

        for row in reader:
            video_id = (row.get("video_id") or "").strip()

            if video_id not in selected_ids:
                continue

            row["manual_valid"] = "yes"
            row["language_verified"] = "yes"
            row["is_music_video"] = "yes"
            row["ai_suno_related"] = "no"
            row["pipeline_status"] = "selected_for_transcript_expansion"

            selected_rows.append(row)

    found_ids = {
        (row.get("video_id") or "").strip()
        for row in selected_rows
    }

    missing_ids = [
        video_id
        for video_id in SELECTED_VIDEO_IDS
        if video_id not in found_ids
    ]

    selected_rows.sort(
        key=lambda row: SELECTED_VIDEO_IDS.index(
            (row.get("video_id") or "").strip()
        )
    )

    output_fields = input_fields + ["pipeline_status"]
    output_fields = list(dict.fromkeys(output_fields))

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

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
        writer.writerows(selected_rows)

    print(f"Input file: {INPUT_FILE}")
    print(f"Output file: {OUTPUT_FILE}")
    print(f"Selected rows: {len(selected_rows)}")

    if missing_ids:
        print("Missing video IDs:")
        for video_id in missing_ids:
            print(f"  {video_id}")
    else:
        print("All requested video IDs were found.")


if __name__ == "__main__":
    main()