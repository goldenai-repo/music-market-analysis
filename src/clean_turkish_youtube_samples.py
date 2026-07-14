import csv
from pathlib import Path

INPUT_PATH = Path("data/processed/turkish_youtube_auto_sample.csv")
OUTPUT_PATH = Path("data/processed/turkish_youtube_review_flagged_sample.csv")

REVIEW_COLUMNS = [
    "video_id",
    "song_title",
    "channel_title",
    "published_at",
    "youtube_url",
    "view_count",
    "like_count",
    "comment_count",
    "search_query",
    "description_preview",
    "auto_review_flag",
    "manual_valid",
    "language_verified",
    "is_music_video",
    "ai_suno_related",
    "channel_type",
    "genre_style",
    "manual_theme",
    "review_notes",
]


def clean_text(value: str) -> str:
    """Remove repeated whitespace and line breaks."""
    return " ".join((value or "").split())


def parse_count(value: str) -> str:
    """Keep numeric counts clean while preserving missing values."""
    value = (value or "").strip()

    if value == "":
        return ""

    try:
        return str(int(float(value)))
    except ValueError:
        return ""


def get_auto_review_flag(title: str, description: str) -> str:
    """Assign a lightweight rule-based flag for manual review."""
    text = f"{title} {description}".lower()

    tutorial_keywords = [
        "nasıl kullanılır",
        "rehber",
        "tutorial",
        "prompt",
        "kullanım şartları",
        "studio",
        "inceleme",
        "adım adım",
        "nasıl yapılır",
    ]

    mix_keywords = [
        "mix",
        "set",
        "full album",
        "best of",
        "en çok dinlenen",
        "playlist",
        "compilation",
    ]

    if any(keyword in text for keyword in tutorial_keywords):
        return "likely_tutorial"

    if any(keyword in text for keyword in mix_keywords):
        return "likely_mix_or_compilation"

    return "likely_song"


def main() -> None:
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_PATH}")

    cleaned_rows: list[dict[str, str]] = []
    seen_video_ids: set[str] = set()

    with INPUT_PATH.open("r", encoding="utf-8-sig", newline="") as input_file:
        reader = csv.DictReader(input_file)

        for row in reader:
            video_id = (row.get("video_id") or "").strip()

            if not video_id or video_id in seen_video_ids:
                continue

            seen_video_ids.add(video_id)

            title = clean_text(row.get("song_title", ""))
            description = clean_text(row.get("description", ""))

            cleaned_rows.append(
                {
                    "video_id": video_id,
                    "song_title": title,
                    "channel_title": clean_text(row.get("channel_title", "")),
                    "published_at": clean_text(row.get("published_at", "")),
                    "youtube_url": clean_text(row.get("youtube_url", "")),
                    "view_count": parse_count(row.get("view_count", "")),
                    "like_count": parse_count(row.get("like_count", "")),
                    "comment_count": parse_count(row.get("comment_count", "")),
                    "search_query": clean_text(row.get("search_query", "")),
                    "description_preview": description[:120],
                    "auto_review_flag": get_auto_review_flag(title, description),
                    "manual_valid": "",
                    "language_verified": "",
                    "is_music_video": "",
                    "ai_suno_related": "",
                    "channel_type": "",
                    "genre_style": "",
                    "manual_theme": "",
                    "review_notes": "",
                }
            )

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8-sig", newline="") as output_file:
        writer = csv.DictWriter(output_file, fieldnames=REVIEW_COLUMNS)
        writer.writeheader()
        writer.writerows(cleaned_rows)

    print(f"Saved {len(cleaned_rows)} cleaned rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()