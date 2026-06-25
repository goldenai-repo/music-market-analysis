#!/usr/bin/env python3
"""
Generate the Finland Finnish-language AI music market report.

The script is intentionally snapshot-first: it stores the desk-research values
used in the report, then calculates all derived metrics from those values. A
few optional API helpers are included for future refreshes.
"""

from __future__ import annotations

import argparse
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Iterable


REPORT_DATE = "2026-06-22"
OUTPUT_FILE = "Finland_AI_Music_Market_Report.md"


POPULATION = 5_652_881
INTERNET_USERS = 5_520_000
YOUTUBE_REACH = 4_100_000
YOUTUBE_REACH_PENETRATION = 72.9
TRAFICOM_YOUTUBE_FREE_STREAMING_3M = 48.0
IFPI_TOTAL_SALES_EUR = 65_477_516
IFPI_STREAMING_EUR = 61_108_999
IFPI_DOWNLOADS_EUR = 362_001
IFPI_PHYSICAL_EUR = 3_986_940
IFPI_FINLAND_TOTAL_MARKET_ESTIMATE_EUR = 86_100_000
IFPI_DOMESTIC_DIGITAL_SHARE = 38.4

APP_STORE_RATING_PROXY = [
    ("Spotify", "Spotify: Music and Podcasts", 363_017),
    ("SoundCloud", "SoundCloud: The Music You Love", 8_015),
    ("YouTube Music", "YouTube Music", 5_210),
    ("Apple Music", "Apple Music", 4_728),
    ("TIDAL", "TIDAL Music: HiFi Sound", 2_752),
    ("Deezer", "Deezer: Music & Podcast Player", 1_174),
    ("Amazon Music", "Amazon Music: Songs & Podcasts", 315),
    ("Qobuz", "Qobuz: Music & Editorial", 285),
]

FORMAT_REVENUE = [
    ("Streaming", IFPI_STREAMING_EUR),
    ("Downloads", IFPI_DOWNLOADS_EUR),
    ("Physical", IFPI_PHYSICAL_EUR),
]

YOUTUBE_MUSIC_PLAY_BENCHMARKS = [
    ("Low $0.5 RPM", 0.50),
    ("Base $1 RPM", 1.00),
    ("High $2 RPM", 2.00),
]
YOUTUBE_VIDEO_BENCHMARKS = [
    ("Low $1 RPM", 1.00),
    ("Base $2 RPM", 2.00),
    ("High $3 RPM", 3.00),
]
CONTENT_ID_BENCHMARKS = [
    ("Low $0.25 RPM", 0.25),
    ("Base $0.75 RPM", 0.75),
    ("High $1.5 RPM", 1.50),
]
SPOTIFY_CREATOR_REPORTED_BENCHMARKS = [
    ("Low $0.0035", 0.0035),
    ("Base $0.0045", 0.0045),
    ("High $0.0052", 0.0052),
]
APPLE_MUSIC_BENCHMARKS = [
    ("Low $0.007", 0.007),
    ("Base $0.010", 0.010),
    ("High $0.012", 0.012),
]
ITUNES_SINGLE_EUR = 1.29
ITUNES_ALBUM_EUR = 11.99

# Strict MusicBrainz proxy: lang:fin AND country:FI, queried on 2026-06-20.
# Past-12-month period is Jul 2025 through Jun 20, 2026.
MONTHLY_RELEASES = {
    "2026-01": 11,
    "2026-02": 14,
    "2026-03": 9,
    "2026-04": 8,
    "2026-05": 6,
    "2026-06": 5,
    "2025-07": 15,
    "2025-08": 20,
    "2025-09": 29,
    "2025-10": 22,
    "2025-11": 20,
    "2025-12": 21,
}

MUSICBRAINZ_WIDE_TOTAL_RELEASES = 530
MUSICBRAINZ_UNIQUE_ARTISTS = 344

AI_TRENDS = {
    "Suno": 60.5,
    "Udio": 13.1,
    "AI Music": 55.4,
}

def pct(value: float) -> str:
    return f"{value:.1f}%"


def money_usd(value: float) -> str:
    return f"${value:,.2f}"


def money_eur(value: float) -> str:
    return f"€{value:,.2f}"


def rows(headers: Iterable[str], body: Iterable[Iterable[object]]) -> str:
    header = "| " + " | ".join(headers) + " |"
    sep = "| " + " | ".join(["---"] * len(list(headers))) + " |"
    lines = [header, sep]
    for row in body:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def scenario_table(
    label: str,
    unit: str,
    benchmarks: list[tuple[str, float]],
) -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    return rows(
        [label, *(name for name, _ in benchmarks)],
        (
            (
                f"{volume:,} {unit}",
                *(money_usd(volume / 1000 * rpm) for _, rpm in benchmarks),
            )
            for volume in volumes
        ),
    )


def spotify_creator_reported_table() -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    return rows(
        ["Spotify Streams", *(name for name, _ in SPOTIFY_CREATOR_REPORTED_BENCHMARKS)],
        (
            (
                f"{volume:,} Streams",
                *(money_usd(volume * rate) for _, rate in SPOTIFY_CREATOR_REPORTED_BENCHMARKS),
            )
            for volume in volumes
        ),
    )


def apple_music_benchmark_table() -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    return rows(
        ["Apple Music Streams", *(name for name, _ in APPLE_MUSIC_BENCHMARKS)],
        (
            (
                f"{volume:,} Streams",
                *(money_usd(volume * rate) for _, rate in APPLE_MUSIC_BENCHMARKS),
            )
            for volume in volumes
        ),
    )


def refresh_itunes(term: str = "kuumaa") -> dict:
    params = {
        "term": term,
        "country": "fi",
        "media": "music",
        "limit": "10",
    }
    url = "https://itunes.apple.com/search?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def refresh_musicbrainz_monthly() -> dict[str, int]:
    headers = {"User-Agent": "GoldenAIResearch/1.0 (market-research)"}
    months = [
        ("2025-07", "2025-07-01", "2025-07-31"),
        ("2025-08", "2025-08-01", "2025-08-31"),
        ("2025-09", "2025-09-01", "2025-09-30"),
        ("2025-10", "2025-10-01", "2025-10-31"),
        ("2025-11", "2025-11-01", "2025-11-30"),
        ("2025-12", "2025-12-01", "2025-12-31"),
        ("2026-01", "2026-01-01", "2026-01-31"),
        ("2026-02", "2026-02-01", "2026-02-28"),
        ("2026-03", "2026-03-01", "2026-03-31"),
        ("2026-04", "2026-04-01", "2026-04-30"),
        ("2026-05", "2026-05-01", "2026-05-31"),
        ("2026-06", "2026-06-01", "2026-06-20"),
    ]
    output: dict[str, int] = {}
    for month, start, end in months:
        query = urllib.parse.quote(f"lang:fin AND country:FI AND date:[{start} TO {end}]")
        url = f"https://musicbrainz.org/ws/2/release/?query={query}&fmt=json&limit=1"
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request, timeout=30) as response:
            output[month] = json.loads(response.read().decode("utf-8"))["count"]
        time.sleep(1.1)
    return output


def generate_report() -> str:
    format_revenue_rows = [
        (
            name,
            money_eur(value),
            pct(value / IFPI_TOTAL_SALES_EUR * 100),
        )
        for name, value in FORMAT_REVENUE
    ]
    app_store_rating_total = sum(count for _, _, count in APP_STORE_RATING_PROXY)
    app_store_rating_rows = [
        (
            rank,
            platform,
            app_name,
            f"{rating_count:,}",
            pct(rating_count / app_store_rating_total * 100),
        )
        for rank, (platform, app_name, rating_count) in enumerate(
            APP_STORE_RATING_PROXY, start=1
        )
    ]
    population_demand_rows = [
        ("Finland population", f"{POPULATION:,}", "Statistics Finland / DataReportal"),
        ("Internet users", f"{INTERNET_USERS:,}", "DataReportal / Kepios"),
        (
            "Internet penetration",
            pct(INTERNET_USERS / POPULATION * 100),
            "Calculated",
        ),
    ]
    platform_reach_rows = [
        (
            "YouTube free streaming",
            f"{TRAFICOM_YOUTUBE_FREE_STREAMING_3M:.0f}%",
            "Watched in last 3 months; free streaming service, not YouTube Music MAU",
        ),
        (
            "YouTube overall ad reach",
            f"{YOUTUBE_REACH:,}",
            "Overall ad reach; ad-planning reach, not YouTube Music users",
        ),
    ]

    ordered_release_rows = [
        ("Jan 2026", MONTHLY_RELEASES["2026-01"]),
        ("Feb 2026", MONTHLY_RELEASES["2026-02"]),
        ("Mar 2026", MONTHLY_RELEASES["2026-03"]),
        ("Apr 2026", MONTHLY_RELEASES["2026-04"]),
        ("May 2026", MONTHLY_RELEASES["2026-05"]),
        ("Jun 2026*", MONTHLY_RELEASES["2026-06"]),
        ("Jul 2025", MONTHLY_RELEASES["2025-07"]),
        ("Aug 2025", MONTHLY_RELEASES["2025-08"]),
        ("Sep 2025", MONTHLY_RELEASES["2025-09"]),
        ("Oct 2025", MONTHLY_RELEASES["2025-10"]),
        ("Nov 2025", MONTHLY_RELEASES["2025-11"]),
        ("Dec 2025", MONTHLY_RELEASES["2025-12"]),
    ]
    annual_releases = sum(MONTHLY_RELEASES.values())
    avg_releases = annual_releases / len(MONTHLY_RELEASES)
    highest_month = max(MONTHLY_RELEASES.items(), key=lambda item: item[1])
    lowest_month = min(MONTHLY_RELEASES.items(), key=lambda item: item[1])
    known_trend_values = [value for value in AI_TRENDS.values() if value is not None]
    ai_interest = (
        sum(known_trend_values) / len(known_trend_values)
        if known_trend_values
        else None
    )

    report = f"""# Finland Finnish-Language AI Music Market Research

Report date: {REPORT_DATE}

## Executive Summary

The Finnish-language AI music market offers a medium-low to medium opportunity. The market is digitally mature and suitable for small-scale testing, but its audience size is limited and does not justify heavy investment yet.

Final judgment: **Market Opportunity = Medium-Low to Medium**  
Recommendation: **Monitor / Small-Scale Test**

## 1. Platform Availability & Verified Market Structure

### 1.1 Main Platform User-Scale Proxy Ranking

{rows(["Rank", "Platform", "Finland App Store App", "Rating Count", "Approx. Proxy Share"], app_store_rating_rows)}

Note: Approx. Proxy Share = Finland App Store rating count for the app / total rating count across the checked music apps. It is not actual market share, downloads, or monthly active users, but it can be used as an iOS-side user-scale and activity proxy. Apple Music may be undercounted because it is deeply integrated into iOS.

### 1.2 Verified Market Structure

{rows(["Format", "Revenue", "Share"], format_revenue_rows)}

IFPI Finland data shows that the recorded music market is highly streaming-driven, so Finnish-language AI music should prioritize streaming platforms rather than treating iTunes downloads as the main growth channel.

## 2. Demand

### 2.1 Population & Internet Base

{rows(["Indicator", "Data", "Source"], population_demand_rows)}

### 2.2 Verified YouTube Reach

{rows(["Platform / Service", "Verified Reach", "Note"], platform_reach_rows)}

### 2.3 Demand Conclusion

Demand rating: **Medium**. Finland has a population of **{POPULATION:,}**, around **{INTERNET_USERS:,}** internet users, and **{pct(INTERNET_USERS / POPULATION * 100)}** internet penetration. YouTube free streaming usage is **{TRAFICOM_YOUTUBE_FREE_STREAMING_3M:.0f}%**, and YouTube overall ad reach is **{YOUTUBE_REACH:,}**, indicating a strong online content reach base.

## 3. Monetization

### 3.1 YouTube

Note: YouTube does not publish fixed Finland/music payout rates. The tables below are planning estimates, not guaranteed revenue.

#### YouTube Music / Art Track Plays

{scenario_table("YouTube Music / Art Track", "Plays", YOUTUBE_MUSIC_PLAY_BENCHMARKS)}

#### Own YouTube Channel Videos

{scenario_table("Own YouTube Channel Video", "Views", YOUTUBE_VIDEO_BENCHMARKS)}

#### Content ID / UGC Claimed Views

{scenario_table("Content ID / UGC Claimed", "Claimed Views", CONTENT_ID_BENCHMARKS)}

### 3.2 iTunes

{rows(["iTunes Finland", "Verified Price"], [
    ("Single Sale", money_eur(ITUNES_SINGLE_EUR)),
    ("Album Sale", money_eur(ITUNES_ALBUM_EUR)),
])}

### 3.3 Spotify

Note: Spotify does not publish a fixed payout rate. This estimate is summarized from creator-reported cases and industry reporting, not official Finland data.

{spotify_creator_reported_table()}

### 3.4 Apple Music

Note: Apple Music has public reporting around a $0.01/stream average, but this is not Finland-specific or guaranteed.

{apple_music_benchmark_table()}

### 3.5 Monetization Conclusion

Apple Music has the highest per-stream estimate in this section. Spotify has a lower creator-reported estimate range but stronger platform scale proxy. YouTube should be treated as a multi-path revenue channel, while iTunes has verified prices but low download-market priority.

## 4. Competition

{rows(["Indicator", "Data"], [
    ("Finnish-language Artists", f"{MUSICBRAINZ_UNIQUE_ARTISTS:,} active artist-credit proxy"),
])}

Scope: MusicBrainz `lang:fin` release data, Jul 2025-Jun 2026, deduplicated by artist-credit. The true total number of Finnish-language creators is likely higher than this proxy, but active publisher count is still far below large-language markets such as English, Spanish, or German.

Competition conclusion: **Medium**. This is not an empty market, but competition is far lower than in English-language music.

## 5. Supply

Scope: MusicBrainz strict proxy = `lang:fin AND country:FI`, covering **Jul 2025-Jun 20 2026**. Jun 2026 is a partial month.

{rows(["Month", "New Releases"], ordered_release_rows)}

{rows(["Metric", "Data"], [
    ("Annual Releases, strict proxy", f"{annual_releases:,}"),
    ("Annual Releases, wide lang:fin proxy", f"{MUSICBRAINZ_WIDE_TOTAL_RELEASES:,}"),
    ("Monthly Average, strict proxy", f"{avg_releases:.1f}"),
    ("Highest Month", f"{highest_month[0]} ({highest_month[1]})"),
    ("Lowest Month", f"{lowest_month[0]} ({lowest_month[1]}; partial month)"),
])}

Supply conclusion: **Low to Medium saturation**. The strict proxy averages about 15 releases per month, while the wide proxy averages about 44 releases per month. Finnish-language content supply does not appear saturated.

## 6. AI Music Acceptance

### 6.1 AI Interest

Scope: Google Trends Finland, Past 12 Months CSV export, averaged across weekly trend scores.

{rows(["Keyword", "Trend Index"], ((key, f"{value:.1f}") for key, value in AI_TRENDS.items()))}

AI Interest Index = **{"N/A" if ai_interest is None else f"{ai_interest:.1f} / 100"}**

AI acceptance conclusion: **Suno and AI Music show visible search interest in Finland, while Udio remains much lower. Overall AI Interest is Medium**.

## 7. Final Assessment

1. Is the Finnish-language market large enough?  
   **Medium-small.** Finland has a population of 5.65M and 97.6% internet penetration. Online reach is strong, but the absolute Finnish-language audience ceiling is limited.

2. Which platform has the largest user reach?  
   **Spotify leads clearly in the Finland App Store rating-count proxy.** YouTube overall ad reach is 4.10M, indicating strong YouTube ecosystem reach, but this is not YouTube Music MAU.

3. Which platform has the strongest monetization?  
   **Apple Music has the highest per-stream estimate.** Spotify uses creator-reported estimates, YouTube should be estimated through Music / Art Track, own channel videos, and Content ID paths, and iTunes has verified Finland Store prices but low download-market share.

4. Is Finnish-language music competition intense?  
   **Medium.** The MusicBrainz wide `lang:fin` proxy shows 344 active artist-credits in the past 12 months, indicating a stable local creator base but not a highly saturated large-language market.

5. Is Finnish-language content supply saturated?  
   **No clear saturation.** The strict proxy shows 180 annual releases and 15 per month; the wide `lang:fin` proxy shows 530 annual releases, which is not a high supply volume.

6. Has the local market started accepting AI music?  
   **There is visible user interest.** Google Trends Finland over the past 12 months shows Suno at 60.5, AI Music at 55.4, and Udio at 13.1, with an AI Interest Index of 43.0/100.

7. Is it worth continuing to release AI music?  
   **Yes, for small-scale testing.** Use Spotify to validate streaming performance, YouTube for discovery and content cold start, and Apple Music for higher per-stream estimate coverage. Heavy investment is not recommended yet.

## Overall Rating

{rows(["Dimension", "Rating"], [
    ("Demand", "Medium, with platform MAU data gap"),
    ("Monetization", "Medium / scenario-based"),
    ("Competition", "Medium"),
    ("Supply Saturation", "Low"),
    ("AI Interest", "Medium"),
])}

Final Market Opportunity: **Medium-Low to Medium**

Recommendation: **Monitor / Small-Scale Test**

## Practical Recommendation

Priority validation platforms: **Spotify + YouTube + Apple Music**  
Rationale: Spotify leads in the App Store rating-count proxy, YouTube has strong reach, and Apple Music has a higher per-stream estimate.

Recommended actions:

- Release 3-5 Finnish-language AI/AI-assisted songs per month and track save rate, skip rate, playlist adds, and 30-day streams.
- Record real Finland-region data from Spotify for Artists / distributor dashboards to replace missing public MAU data.
- Use YouTube lyric videos, visualizers, and Shorts cutdowns for discovery, search, and cold start.
- Keep Apple Music distribution active as a higher per-stream estimate channel.
- Keep iTunes as distribution coverage only, not as a main growth channel.

"""
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help="Markdown output file path. Defaults to Finland_AI_Music_Market_Report.md",
    )
    parser.add_argument("--refresh-itunes", action="store_true")
    parser.add_argument("--refresh-musicbrainz", action="store_true")
    args = parser.parse_args()

    if args.refresh_itunes:
        print(json.dumps(refresh_itunes(), ensure_ascii=False, indent=2))
        return

    if args.refresh_musicbrainz:
        print(json.dumps(refresh_musicbrainz_monthly(), ensure_ascii=False, indent=2))
        return

    output_path = Path(args.output)
    output_path.write_text(generate_report(), encoding="utf-8-sig")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
