import csv
import os
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


SEARCH_QUERIES = [
    "Turkish AI generated song",
    "Turkish Suno song",
    "Suno Türkçe şarkı",
    "yapay zeka Türkçe şarkı",
    "Turkish pop music",
    "Turkish folk song",
]

OUTPUT_PATH = Path("data/processed/turkish_youtube_auto_sample.csv")
RESULTS_PER_QUERY = 10


def search_video_ids(
    youtube: Any,
    query: str,
    max_results: int = RESULTS_PER_QUERY,
) -> list[str]:
    """Search YouTube and return matching video IDs."""
    response = (
        youtube.search()
        .list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results,
            relevanceLanguage="tr",
            regionCode="TR",
        )
        .execute()
    )

    return [
        item["id"]["videoId"]
        for item in response.get("items", [])
        if item.get("id", {}).get("videoId")
    ]


def fetch_video_details(youtube: Any, video_ids: list[str]) -> list[dict[str, Any]]:
    """Fetch metadata and engagement statistics for video IDs."""
    if not video_ids:
        return []

    response = (
        youtube.videos()
        .list(
            part="snippet,statistics",
            id=",".join(video_ids),
        )
        .execute()
    )

    rows: list[dict[str, Any]] = []

    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        statistics = item.get("statistics", {})
        video_id = item["id"]

        rows.append(
            {
                "video_id": video_id,
                "song_title": snippet.get("title", ""),
                "channel_title": snippet.get("channelTitle", ""),
                "published_at": snippet.get("publishedAt", ""),
                "description": snippet.get("description", ""),
                "youtube_url": f"https://www.youtube.com/watch?v={video_id}",
                "view_count": int(statistics.get("viewCount", 0)),
                "like_count": int(statistics.get("likeCount", 0)),
                "comment_count": int(statistics.get("commentCount", 0)),
            }
        )

    return rows


def save_rows(rows: list[dict[str, Any]], output_path: Path) -> None:
    """Save collected rows to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "video_id",
        "song_title",
        "channel_title",
        "published_at",
        "youtube_url",
        "view_count",
        "like_count",
        "comment_count",
        "description",
        "search_query",
    ]

    with output_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    load_dotenv()

    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "YOUTUBE_API_KEY is missing. Add it to your local .env file."
        )

    youtube = build("youtube", "v3", developerKey=api_key)

    collected_by_id: dict[str, dict[str, Any]] = {}

    try:
        for query in SEARCH_QUERIES:
            print(f"Searching: {query}")

            video_ids = search_video_ids(youtube, query)
            video_rows = fetch_video_details(youtube, video_ids)

            for row in video_rows:
                video_id = row["video_id"]

                if video_id not in collected_by_id:
                    row["search_query"] = query
                    collected_by_id[video_id] = row

        rows = list(collected_by_id.values())
        save_rows(rows, OUTPUT_PATH)

        print(f"Saved {len(rows)} unique videos to {OUTPUT_PATH}")

    except HttpError as error:
        raise RuntimeError(f"YouTube API request failed: {error}") from error


if __name__ == "__main__":
    main()