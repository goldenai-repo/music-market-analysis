import json
import os
import re
import statistics
import sys
import time
from datetime import datetime, timezone
from http.client import IncompleteRead
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API_BASE = "https://www.googleapis.com/youtube/v3"
OUTPUT_MD = Path(__file__).with_name("youtube_five_country_2025_data.md")
RAW_JSON = Path(__file__).with_name("youtube_five_country_2025_raw.json")
CANDIDATES_JSON = Path(__file__).with_name("youtube_five_country_2025_candidates.json")
DETAILS_JSON = Path(__file__).with_name("youtube_five_country_2025_details.json")

YEAR_START = "2025-01-01T00:00:00Z"
YEAR_END = "2026-01-01T00:00:00Z"
REQUEST_TIMEOUT_SECONDS = 15
SEARCH_DELAY_SECONDS = 0.8
DETAILS_DELAY_SECONDS = 0.4
TARGET_PER_COUNTRY = 40

EXCLUDED_TITLE_PATTERNS = [
    "shorts",
    "#shorts",
    "karaoke",
    "cover",
    "reaction",
    "review",
    "playlist",
    "full album",
    "album completo",
    "mix",
    "live",
    "concert",
    "performance",
    "tutorial",
    "instrumental",
]

COUNTRIES = {
    "Finland": {
        "region_code": "FI",
        "language_code": "fi",
        "queries": [
            "suomalainen musiikki official music video 2025",
            "suomalainen musiikki official audio 2025",
            "suomalainen musiikki lyric video 2025",
            "uusi suomalainen kappale 2025",
            "uusi suomalainen musiikki 2025",
        ],
    },
    "Norway": {
        "region_code": "NO",
        "language_code": "no",
        "queries": [
            "norsk musikk official music video 2025",
            "norsk musikk official audio 2025",
            "norsk musikk lyric video 2025",
            "ny norsk sang 2025",
            "ny norsk musikk 2025",
        ],
    },
    "Czechia": {
        "region_code": "CZ",
        "language_code": "cs",
        "queries": [
            "ceska hudba official music video 2025",
            "ceska hudba official audio 2025",
            "ceska hudba lyric video 2025",
            "nova ceska pisnicka 2025",
            "nova ceska hudba 2025",
        ],
    },
    "Hungary": {
        "region_code": "HU",
        "language_code": "hu",
        "queries": [
            "magyar zene official music video 2025",
            "magyar zene official audio 2025",
            "magyar zene lyric video 2025",
            "uj magyar dal 2025",
            "uj magyar zene 2025",
        ],
    },
    "Greece": {
        "region_code": "GR",
        "language_code": "el",
        "queries": [
            "elliniki mousiki official music video 2025",
            "elliniki mousiki official audio 2025",
            "elliniki mousiki lyric video 2025",
            "neo elliniko tragoudi 2025",
            "nea elliniki mousiki 2025",
        ],
    },
}


def youtube_get(path, params, api_key):
    query = dict(params)
    query["key"] = api_key
    url = f"{API_BASE}/{path}?{urlencode(query)}"
    headers = {
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "Connection": "close",
        "User-Agent": "Mozilla/5.0",
    }

    last_error = None
    for attempt in range(1, 3):
        request = Request(url, headers=headers)
        try:
            with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
                try:
                    raw_data = response.read()
                except IncompleteRead as exc:
                    raw_data = exc.partial
            return json.loads(raw_data.decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, IncompleteRead, json.JSONDecodeError) as exc:
            last_error = exc
            if isinstance(exc, HTTPError) and exc.code == 429:
                break
            if attempt < 2:
                time.sleep(attempt * 2)

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


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def clean_md(value):
    return str(value or "").replace("|", "\\|").replace("\n", " ").strip()


def fmt_int(value):
    return f"{int(value):,}"


def fmt_rate(value):
    return f"{value:.3%}"


def write_candidate_cache(candidates, failed_queries):
    CANDIDATES_JSON.write_text(
        json.dumps(
            {
                "framework": "unrestricted_genre",
                "candidates": list(candidates.values()),
                "failed_queries": failed_queries,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )


def collect_search_candidates(api_key):
    candidates = {}
    failed_queries = []

    for country, country_config in COUNTRIES.items():
        for query in country_config["queries"]:
            print(f"Searching: {country} / {query}", flush=True)
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
                        "regionCode": country_config["region_code"],
                        "relevanceLanguage": country_config["language_code"],
                        "publishedAfter": YEAR_START,
                        "publishedBefore": YEAR_END,
                        "safeSearch": "none",
                        "fields": (
                            "items(id/videoId,"
                            "snippet(title,channelId,channelTitle,publishedAt))"
                        ),
                    },
                    api_key,
                )
            except Exception as exc:
                print(f"Skipped query after retries: {query} ({exc})", flush=True)
                failed_queries.append(
                    {
                        "country": country,
                        "query": query,
                        "error": repr(exc),
                    }
                )
                write_candidate_cache(candidates, failed_queries)
                continue

            for item in data.get("items", []):
                video_id = item.get("id", {}).get("videoId")
                if not video_id:
                    continue
                key = (country, video_id)
                candidates.setdefault(
                    key,
                    {
                        "video_id": video_id,
                        "country": country,
                        "query": query,
                        "matched_queries": [],
                        "search_snippet": item.get("snippet", {}),
                    },
                )
                candidates[key]["matched_queries"].append(query)
            write_candidate_cache(candidates, failed_queries)
            time.sleep(SEARCH_DELAY_SECONDS)

        print(
            f"Finished search for {country}: "
            f"{len([key for key in candidates if key[0] == country])} unique candidates",
            flush=True,
        )

    return list(candidates.values()), failed_queries


def fetch_video_details(api_key, video_ids):
    videos_by_id = {}
    failed_detail_batches = []
    batches = list(chunked(video_ids, 50))

    for batch_index, batch in enumerate(batches, start=1):
        print(f"Fetching video details batch {batch_index}/{len(batches)}", flush=True)
        try:
            data = youtube_get(
                "videos",
                {
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(batch),
                    "maxResults": "50",
                    "fields": (
                        "items(id,"
                        "snippet(title,channelTitle,publishedAt,categoryId),"
                        "statistics(viewCount,likeCount,commentCount),"
                        "contentDetails(duration))"
                    ),
                },
                api_key,
            )
        except Exception as exc:
            print(
                f"Skipped details batch {batch_index}/{len(batches)} after retries: {exc}",
                flush=True,
            )
            failed_detail_batches.append(
                {
                    "batch_index": batch_index,
                    "video_ids": batch,
                    "error": repr(exc),
                }
            )
            continue

        for item in data.get("items", []):
            videos_by_id[item.get("id")] = item
        DETAILS_JSON.write_text(
            json.dumps(
                {
                    "framework": "unrestricted_genre",
                    "videos_by_id": videos_by_id,
                    "failed_detail_batches": failed_detail_batches,
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        time.sleep(DETAILS_DELAY_SECONDS)

    return videos_by_id, failed_detail_batches


def normalize_video(candidate, detail, collected_at):
    snippet = detail.get("snippet", {})
    statistics = detail.get("statistics", {})
    content_details = detail.get("contentDetails", {})
    duration = content_details.get("duration", "")
    duration_seconds = parse_duration_seconds(duration)
    video_id = detail.get("id", candidate["video_id"])

    return {
        "video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": snippet.get("title", ""),
        "channel_title": snippet.get("channelTitle", ""),
        "published_at": snippet.get("publishedAt", ""),
        "duration": duration,
        "duration_seconds": duration_seconds,
        "view_count": to_int(statistics.get("viewCount")),
        "like_count": to_int(statistics.get("likeCount")),
        "comment_count": to_int(statistics.get("commentCount")),
        "query": candidate["query"],
        "country": candidate["country"],
        "category_id": snippet.get("categoryId", ""),
        "matched_queries": candidate["matched_queries"],
        "collected_at": collected_at,
    }


def is_2025_video(video):
    return "2025-01-01" <= video["published_at"][:10] < "2026-01-01"


def is_target_duration(video):
    return 90 <= video["duration_seconds"] <= 480


def has_excluded_title(video):
    text = f"{video['title']} {video['channel_title']}".lower()
    return any(pattern in text for pattern in EXCLUDED_TITLE_PATTERNS)


def is_usable_video(video):
    if video["category_id"] != "10":
        return False
    if not is_2025_video(video):
        return False
    if not is_target_duration(video):
        return False
    if has_excluded_title(video):
        return False
    if video["view_count"] <= 0:
        return False
    return True


def rank_videos(videos):
    return sorted(
        videos,
        key=lambda item: (
            item["view_count"],
            item["like_count"],
            item["comment_count"],
        ),
        reverse=True,
    )


def select_country_samples(videos):
    selected = []
    selected_ids = set()

    for country in COUNTRIES:
        for video in rank_videos([item for item in videos if item["country"] == country]):
            if video["video_id"] in selected_ids:
                continue
            selected.append(video)
            selected_ids.add(video["video_id"])
            if len([item for item in selected if item["country"] == country]) >= TARGET_PER_COUNTRY:
                break

    return selected


def summarize_group(videos):
    views = [item["view_count"] for item in videos]
    likes = [item["like_count"] for item in videos]
    comments = [item["comment_count"] for item in videos]
    total_views = sum(views)
    total_likes = sum(likes)
    total_comments = sum(comments)
    return {
        "video_count": len(videos),
        "total_views": total_views,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "average_views": int(total_views / len(videos)) if videos else 0,
        "median_views": int(statistics.median(views)) if videos else 0,
        "average_likes": int(sum(likes) / len(videos)) if videos else 0,
        "like_rate": (total_likes / total_views) if total_views else 0,
        "comment_rate": (total_comments / total_views) if total_views else 0,
    }


def write_summary_table(handle, rows):
    handle.write("## Country Summary\n\n")
    handle.write(
        "| Country | Videos | Total Views | Total Likes | Total Comments | "
        "Average Views | Median Views | Like Rate | Comment Rate |\n"
    )
    handle.write("| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
    for country, summary in rows:
        handle.write(
            f"| {country} | {summary['video_count']} "
            f"| {fmt_int(summary['total_views'])} "
            f"| {fmt_int(summary['total_likes'])} "
            f"| {fmt_int(summary['total_comments'])} "
            f"| {fmt_int(summary['average_views'])} "
            f"| {fmt_int(summary['median_views'])} "
            f"| {fmt_rate(summary['like_rate'])} "
            f"| {fmt_rate(summary['comment_rate'])} |\n"
        )
    handle.write("\n")


def write_markdown(videos, all_candidates, failed_queries, failed_detail_batches, output_path):
    collected_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    with output_path.open("w", encoding="utf-8") as handle:
        handle.write("# Five-Country YouTube 2025 Music Data\n\n")
        handle.write(f"Collected at: {collected_at}\n\n")
        handle.write("## Methodology\n\n")
        handle.write("- Countries: Finland, Norway, Czechia, Hungary, Greece.\n")
        handle.write("- Year filter: videos published from 2025-01-01 to 2025-12-31.\n")
        handle.write("- Genre rule: unrestricted; no pop/ballad/rap filtering or quota split.\n")
        handle.write(
            f"- Target sample: {TARGET_PER_COUNTRY} videos per country, "
            f"{TARGET_PER_COUNTRY * len(COUNTRIES)} videos total.\n"
        )
        handle.write("- Query structure: local-language music/new-song terms plus official music video, official audio, and lyric video variants.\n")
        handle.write("- Target video types: official music video, official audio, lyric video, and recent local-language song uploads.\n")
        handle.write("- Filters: YouTube music category, 90-480 second duration, positive views, and title/channel exclusions for shorts, karaoke, covers, reactions, playlists, mixes, full albums, live/concert/performance videos, tutorials, and instrumentals.\n\n")

        country_rows = []
        for country in COUNTRIES:
            country_videos = [item for item in videos if item["country"] == country]
            country_rows.append((country, summarize_group(country_videos)))
        write_summary_table(handle, country_rows)

        handle.write("## Raw Video Data\n\n")
        handle.write(
            "| Country | Title | Channel | Published | Duration | Views | Likes | Comments | Query | URL |\n"
        )
        handle.write("| --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |\n")
        for video in sorted(videos, key=lambda item: (item["country"], -item["view_count"])):
            handle.write(
                f"| {video['country']} "
                f"| {clean_md(video['title'])} "
                f"| {clean_md(video['channel_title'])} "
                f"| {video['published_at'][:10]} "
                f"| {video['duration']} "
                f"| {video['view_count']} "
                f"| {video['like_count']} "
                f"| {video['comment_count']} "
                f"| {clean_md(video['query'])} "
                f"| [Watch]({video['url']}) |\n"
            )

        handle.write("\n## Collection Diagnostics\n\n")
        handle.write(f"- Raw unique country-video candidates before filters: {len(all_candidates)}.\n")
        handle.write(f"- Final selected videos: {len(videos)}.\n")
        handle.write(f"- Failed search queries: {len(failed_queries)}.\n")
        handle.write(f"- Failed video-detail batches: {len(failed_detail_batches)}.\n")
        for country in COUNTRIES:
            count = len([item for item in videos if item["country"] == country])
            handle.write(f"- {country}: {count} selected videos.\n")

        if failed_queries:
            handle.write("\n### Failed Queries\n\n")
            handle.write("| Country | Query | Error |\n")
            handle.write("| --- | --- | --- |\n")
            for item in failed_queries:
                handle.write(
                    f"| {item['country']} | {clean_md(item['query'])} "
                    f"| {clean_md(item['error'])} |\n"
                )

        if failed_detail_batches:
            handle.write("\n### Failed Video Detail Batches\n\n")
            handle.write("| Batch | Video Count | Error |\n")
            handle.write("| ---: | ---: | --- |\n")
            for item in failed_detail_batches:
                handle.write(
                    f"| {item['batch_index']} | {len(item['video_ids'])} "
                    f"| {clean_md(item['error'])} |\n"
                )


def load_candidate_cache():
    candidate_cache = json.loads(CANDIDATES_JSON.read_text(encoding="utf-8"))
    if candidate_cache.get("framework") != "unrestricted_genre":
        return None
    return candidate_cache


def load_details_cache():
    details_cache = json.loads(DETAILS_JSON.read_text(encoding="utf-8"))
    if details_cache.get("framework") != "unrestricted_genre":
        return None
    return details_cache


def main():
    api_key = os.getenv("YOUTUBE_API_KEY")
    candidate_cache = load_candidate_cache() if CANDIDATES_JSON.exists() else None
    details_cache = load_details_cache() if DETAILS_JSON.exists() else None

    if not api_key and (candidate_cache is None or details_cache is None):
        raise RuntimeError("Missing YOUTUBE_API_KEY environment variable.")

    collected_at = datetime.now(timezone.utc).isoformat()
    if candidate_cache is not None:
        print(f"Loading cached candidates: {CANDIDATES_JSON}", flush=True)
        candidates = candidate_cache["candidates"]
        failed_queries = candidate_cache.get("failed_queries", [])
    else:
        candidates, failed_queries = collect_search_candidates(api_key)

    unique_video_ids = sorted({item["video_id"] for item in candidates})
    if details_cache is not None:
        print(f"Loading cached video details: {DETAILS_JSON}", flush=True)
        details_by_id = details_cache["videos_by_id"]
        failed_detail_batches = details_cache.get("failed_detail_batches", [])
    else:
        details_by_id, failed_detail_batches = fetch_video_details(api_key, unique_video_ids)

    normalized = []
    for candidate in candidates:
        detail = details_by_id.get(candidate["video_id"])
        if not detail:
            continue
        normalized.append(normalize_video(candidate, detail, collected_at))

    filtered = [item for item in normalized if is_usable_video(item)]
    selected = select_country_samples(filtered)

    RAW_JSON.write_text(
        json.dumps(
            {
                "framework": "unrestricted_genre",
                "collected_at": collected_at,
                "candidates": candidates,
                "failed_queries": failed_queries,
                "failed_detail_batches": failed_detail_batches,
                "filtered_count": len(filtered),
                "selected": selected,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    write_markdown(selected, candidates, failed_queries, failed_detail_batches, OUTPUT_MD)

    print(f"Raw candidates: {len(candidates)}")
    print(f"Filtered usable videos: {len(filtered)}")
    print(f"Selected videos: {len(selected)}")
    print(f"Saved Markdown: {OUTPUT_MD}")
    print(f"Saved raw JSON: {RAW_JSON}")


if __name__ == "__main__":
    main()
