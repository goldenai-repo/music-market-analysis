import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"

DEFAULT_QUERY = "Taylor Swift Anti-Hero official music video"
DEFAULT_MAX_RESULTS = 5

OUTPUT_PATH = Path("data/processed/youtube_videos_sample.csv")


def get_api_key() -> str:
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise EnvironmentError("YOUTUBE_API_KEY must be set in your .env file.")
    return api_key


def search_videos(api_key: str, query: str = DEFAULT_QUERY, max_results: int = DEFAULT_MAX_RESULTS) -> list[str]:
    """Search YouTube videos and return a list of video IDs."""
    params = {
        "key": api_key,
        "q": query,
        "type": "video",
        "part": "id",
        "maxResults": max_results,
    }

    response = requests.get(YOUTUBE_SEARCH_URL, params=params, timeout=10)

    if response.status_code != 200:
        print("Status code:", response.status_code)
        print("Response text:", response.text)

    response.raise_for_status()

    items = response.json().get("items", [])
    return [item["id"]["videoId"] for item in items if "videoId" in item.get("id", {})]


def fetch_video_details(api_key: str, video_ids: list[str]) -> list[dict]:
    """Fetch snippet and statistics for the given video IDs."""
    params = {
        "key": api_key,
        "id": ",".join(video_ids),
        "part": "snippet,statistics",
    }

    response = requests.get(YOUTUBE_VIDEOS_URL, params=params, timeout=10)
    response.raise_for_status()

    return response.json().get("items", [])


def parse_results(items: list[dict]) -> pd.DataFrame:
    """Parse YouTube API video results into a dataframe."""
    rows = []

    for item in items:
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        video_id = item.get("id")

        def to_int(value):
            try:
                return int(value)
            except (TypeError, ValueError):
                return None

        rows.append(
            {
                "video_id": video_id,
                "title": snippet.get("title"),
                "channel_title": snippet.get("channelTitle"),
                "published_at": snippet.get("publishedAt"),
                "view_count": to_int(stats.get("viewCount")),
                "like_count": to_int(stats.get("likeCount")),
                "comment_count": to_int(stats.get("commentCount")),
                "youtube_url": f"https://www.youtube.com/watch?v={video_id}" if video_id else None,
            }
        )

    return pd.DataFrame(rows)


def save_results(df: pd.DataFrame, output_path: Path = OUTPUT_PATH) -> None:
    """Save dataframe to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def main(query: str = DEFAULT_QUERY, max_results: int = DEFAULT_MAX_RESULTS) -> None:
    print(f"Fetching YouTube videos for: '{query}'")

    try:
        api_key = get_api_key()
        video_ids = search_videos(api_key, query=query, max_results=max_results)
    except EnvironmentError as error:
        print(f"Credential error: {error}")
        return
    except requests.RequestException as error:
        print(f"YouTube API request error: {error}")
        return

    if not video_ids:
        print("No videos returned.")
        return

    try:
        items = fetch_video_details(api_key, video_ids)
    except requests.RequestException as error:
        print(f"YouTube API request error: {error}")
        return

    if not items:
        print("No video details returned.")
        return

    df = parse_results(items)
    save_results(df)

    print(f"Saved {len(df)} videos to {OUTPUT_PATH}")
    print(df[["title", "view_count", "like_count", "comment_count"]].head())


if __name__ == "__main__":
    main()
