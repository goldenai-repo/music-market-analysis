import json
import os
import re
import time
from http.client import IncompleteRead
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE = "https://www.googleapis.com/youtube/v3"
OUTPUT_MD = Path("youtube_music_top100_likes.md")
RAW_CANDIDATES_JSON = Path("youtube_raw_candidates.json")
VIDEO_DETAILS_JSON = Path("youtube_video_details.json")

SEARCH_QUERIES = [
    "official music video",
    "official video music",
    "music video",
    "VEVO official music video",
    "pop official music video",
    "hip hop official music video",
    "rap official music video",
    "latin official music video",
    "kpop official music video",
    "rock official music video",
    "Taylor Swift official music video",
    "BTS official music video",
    "BLACKPINK official music video",
    "Justin Bieber official music video",
    "Ariana Grande official music video",
    "Billie Eilish official music video",
    "The Weeknd official music video",
    "Drake official music video",
    "Ed Sheeran official music video",
    "Eminem official music video",
    "Rihanna official music video",
    "Katy Perry official music video",
    "Shakira official music video",
    "Bruno Mars official music video",
    "Maroon 5 official music video",
    "Dua Lipa official music video",
    "Lady Gaga official music video",
    "Post Malone official music video",
    "Bad Bunny official music video",
    "J Balvin official music video",
    "Ozuna official music video",
    "Karol G official music video",
    "Adele official music video",
    "Selena Gomez official music video",
    "Miley Cyrus official music video",
    "Imagine Dragons official music video",
    "Coldplay official music video",
    "One Direction official music video",
    "Nicki Minaj official music video",
    "Beyonce official music video",
]


def youtube_get(path, params, api_key):
    query = dict(params)
    query["key"] = api_key
    url = f"{API_BASE}/{path}?{urlencode(query)}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "Connection": "close",
    }

    last_error = None
    for attempt in range(1, 4):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=60) as response:
                try:
                    raw_data = response.read()
                except IncompleteRead as exc:
                    raw_data = exc.partial
            return json.loads(raw_data.decode("utf-8"))
        except (HTTPError, URLError, IncompleteRead, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt == 3:
                break
            time.sleep(2 * attempt)

    raise last_error


def chunked(items, size):
    for index in range(0, len(items), size):
        yield items[index : index + size]


def parse_duration_seconds(duration):
    match = re.fullmatch(
        r"P(?:(?P<days>\d+)D)?T?"
        r"(?:(?P<hours>\d+)H)?"
        r"(?:(?P<minutes>\d+)M)?"
        r"(?:(?P<seconds>\d+)S)?",
        duration or "",
    )
    if not match:
        return 0

    parts = {key: int(value or 0) for key, value in match.groupdict().items()}
    return (
        parts["days"] * 86400
        + parts["hours"] * 3600
        + parts["minutes"] * 60
        + parts["seconds"]
    )


def clean_md(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()


def collect_candidates(api_key):
    candidates = {}

    for query in SEARCH_QUERIES:
        try:
            data = youtube_get(
                "search",
                {
                    "part": "snippet",
                    "type": "video",
                    "videoCategoryId": "10",
                    "order": "viewCount",
                    "maxResults": "50",
                    "q": query,
                    "safeSearch": "none",
                    "fields": "items(id/videoId,snippet(title,channelId,channelTitle,publishedAt,thumbnails/default/url))",
                },
                api_key,
            )
        except Exception as exc:
            print(f"Skipped query after retries: {query} ({exc})")
            continue

        for item in data.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            candidates.setdefault(
                video_id,
                {
                    "video_id": video_id,
                    "matched_queries": [],
                    "search_snippet": item.get("snippet", {}),
                },
            )
            candidates[video_id]["matched_queries"].append(query)

        time.sleep(0.1)

    return list(candidates.values())


def fetch_video_details(api_key, video_ids):
    videos = []

    for batch in chunked(video_ids, 25):
        data = youtube_get(
            "videos",
            {
                "part": "snippet,statistics,contentDetails",
                "id": ",".join(batch),
                "maxResults": "50",
                "fields": (
                    "items(id,"
                    "snippet(title,channelTitle,channelId,publishedAt,categoryId,"
                    "thumbnails/default/url,thumbnails/medium/url,thumbnails/high/url,thumbnails/standard/url,thumbnails/maxres/url),"
                    "statistics(viewCount,likeCount,commentCount),"
                    "contentDetails(duration))"
                ),
            },
            api_key,
        )
        videos.extend(data.get("items", []))
        time.sleep(0.1)

    return videos


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def normalize_video(item, collected_at):
    snippet = item.get("snippet", {})
    statistics = item.get("statistics", {})
    content_details = item.get("contentDetails", {})
    thumbnails = snippet.get("thumbnails", {})
    thumbnail = (
        thumbnails.get("maxres", {})
        or thumbnails.get("standard", {})
        or thumbnails.get("high", {})
        or thumbnails.get("medium", {})
        or thumbnails.get("default", {})
    )

    duration = content_details.get("duration", "")
    duration_seconds = parse_duration_seconds(duration)

    return {
        "video_id": item.get("id", ""),
        "title": snippet.get("title", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "channel_id": snippet.get("channelId", ""),
        "published_at": snippet.get("publishedAt", ""),
        "category_id": snippet.get("categoryId", ""),
        "description": snippet.get("description", ""),
        "tags": snippet.get("tags", []),
        "duration": duration,
        "duration_seconds": duration_seconds,
        "view_count": to_int(statistics.get("viewCount")),
        "like_count": to_int(statistics.get("likeCount")),
        "comment_count": to_int(statistics.get("commentCount")),
        "thumbnail_url": thumbnail.get("url", ""),
        "video_url": f"https://www.youtube.com/watch?v={item.get('id', '')}",
        "collected_at": collected_at,
    }


def looks_like_music_video(video):
    title = video["title"].lower()
    channel = video["channel_title"].lower()
    text = f"{title} {channel}"
    music_signals = [
        "official music video",
        "official video",
        "music video",
        "vevo",
        "mv",
    ]

    return any(signal in text for signal in music_signals)


def filter_videos(videos):
    filtered = []

    for video in videos:
        if video["category_id"] != "10":
            continue
        if video["like_count"] <= 0:
            continue
        if video["duration_seconds"] < 60:
            continue
        if not looks_like_music_video(video):
            continue
        filtered.append(video)

    return filtered


def export_markdown(videos):
    with OUTPUT_MD.open("w", encoding="utf-8") as f:
        f.write("# YouTube Music Videos Top 100 by Likes\n\n")
        f.write(
            "Scope: public YouTube music-video candidates, sorted by total public like count. "
            "This is not an official YouTube all-time chart.\n\n"
        )
        f.write("| Rank | Title | Channel | Published | Views | Likes | Comments | Duration | Thumbnail | YouTube Link |\n")
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |\n")

        for rank, video in enumerate(videos[:100], start=1):
            thumbnail = f"[Image]({video['thumbnail_url']})" if video["thumbnail_url"] else ""
            link = f"[Watch]({video['video_url']})"
            f.write(
                f"| {rank} "
                f"| {clean_md(video['title'])} "
                f"| {clean_md(video['channel_title'])} "
                f"| {clean_md(video['published_at'][:10])} "
                f"| {video['view_count']} "
                f"| {video['like_count']} "
                f"| {video['comment_count']} "
                f"| {clean_md(video['duration'])} "
                f"| {thumbnail} "
                f"| {link} |\n"
            )


def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        raise RuntimeError("Missing YOUTUBE_API_KEY environment variable.")

    collected_at = datetime.now(timezone.utc).isoformat()
    if RAW_CANDIDATES_JSON.exists():
        candidates = json.loads(RAW_CANDIDATES_JSON.read_text(encoding="utf-8"))
    else:
        candidates = collect_candidates(api_key)
        RAW_CANDIDATES_JSON.write_text(
            json.dumps(candidates, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    video_ids = [item["video_id"] for item in candidates]
    raw_details = fetch_video_details(api_key, video_ids)
    normalized = [normalize_video(item, collected_at) for item in raw_details]
    filtered = filter_videos(normalized)
    ranked = sorted(filtered, key=lambda item: item["like_count"], reverse=True)

    VIDEO_DETAILS_JSON.write_text(
        json.dumps(ranked, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    export_markdown(ranked)

    print(f"Candidates: {len(candidates)}")
    print(f"Filtered music videos: {len(ranked)}")
    print(f"Saved: {OUTPUT_MD}")


if __name__ == "__main__":
    main()
