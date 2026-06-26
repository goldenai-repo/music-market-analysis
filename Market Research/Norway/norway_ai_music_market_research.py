#!/usr/bin/env python3
"""
Generate the Norway Norwegian-language AI music market report.

This is a snapshot-first research script: public/API-verifiable data points are
stored as constants, and derived tables are generated from those values.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


REPORT_DATE = "2026-06-25"
OUTPUT_FILE = "Norway_Norwegian_AI_Music_Market_Report.md"


POPULATION = 5_600_000
INTERNET_USERS = 5_550_000
INTERNET_PENETRATION = 99.0
YOUTUBE_AD_REACH = 4_340_000
YOUTUBE_AD_REACH_POP_PCT = 77.5
YOUTUBE_AD_REACH_INTERNET_PCT = 78.2


APP_STORE_RATING_PROXY = [
    ("Spotify", "Spotify: Music and Podcasts", 792_892),
    ("SoundCloud", "SoundCloud: The Music You Love", 15_061),
    ("TIDAL", "TIDAL Music: HiFi Sound", 10_937),
    ("YouTube Music", "YouTube Music", 9_906),
    ("Apple Music", "Apple Music", 6_535),
    ("Audiomack", "Audiomack - Play Music Offline", 2_689),
    ("Deezer", "Deezer: Music & Podcast Player", 694),
    ("Qobuz", "Qobuz: Music & Editorial", 651),
    ("Bandcamp", "Bandcamp", 314),
]


# IFPI Norge official statistics page, chart data for 2020, NOK.
IFPI_STREAMING_NOK = 981_400_000
IFPI_DOWNLOAD_NOK = 23_500_000
IFPI_PHYSICAL_NOK = 70_800_000


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
SPOTIFY_BENCHMARKS = [
    ("Low $0.0035", 0.0035),
    ("Base $0.0045", 0.0045),
    ("High $0.0052", 0.0052),
]
APPLE_MUSIC_BENCHMARKS = [
    ("Low $0.007", 0.007),
    ("Base $0.010", 0.010),
    ("High $0.012", 0.012),
]


ITUNES_SINGLE_NOK = 12.00
ITUNES_ALBUM_NOK = 125.00


# MusicBrainz query scope: lang:nor / lang:nob / lang:nno, Jul 2025-Jun 25 2026.
# Monthly counts are grouped by actual release date YYYY-MM after fetching releases.
STRICT_MONTHLY_RELEASES = {
    "2025-07": 10,
    "2025-08": 2,
    "2025-09": 5,
    "2025-10": 7,
    "2025-11": 15,
    "2025-12": 1,
    "2026-01": 7,
    "2026-02": 5,
    "2026-03": 3,
    "2026-04": 2,
    "2026-05": 2,
    "2026-06": 0,
}
WIDE_MONTHLY_RELEASES = {
    "2025-07": 20,
    "2025-08": 9,
    "2025-09": 18,
    "2025-10": 26,
    "2025-11": 28,
    "2025-12": 6,
    "2026-01": 20,
    "2026-02": 13,
    "2026-03": 8,
    "2026-04": 6,
    "2026-05": 4,
    "2026-06": 2,
}
MUSICBRAINZ_WIDE_ACTIVE_ARTIST_CREDITS = 139
MUSICBRAINZ_STRICT_UNIQUE_RELEASES = 67
MUSICBRAINZ_WIDE_UNIQUE_RELEASES = 170


AI_TRENDS = {
    "Suno": 58.3,
    "Udio": 1.2,
    "AI Music": 38.1,
    "KI-musikk": 0.0,
}
AI_TREND_MAX = {
    "Suno": 100,
    "Udio": 14,
    "AI Music": 66,
    "KI-musikk": 0,
}
AI_TREND_NONZERO_WEEKS = {
    "Suno": 53,
    "Udio": 9,
    "AI Music": 53,
    "KI-musikk": 0,
}


def pct(value: float) -> str:
    return f"{value:.1f}%"


def int_fmt(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{int(value):,}"


def money_usd(value: float) -> str:
    return f"${value:,.2f}"


def money_nok(value: float) -> str:
    return f"NOK {value:,.2f}"


def rows(headers: Iterable[str], body: Iterable[Iterable[object]]) -> str:
    headers = list(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def proxy_share_rows() -> list[tuple[object, ...]]:
    total = sum(rating for _, _, rating in APP_STORE_RATING_PROXY)
    return [
        (idx, platform, app_name, int_fmt(rating), pct(rating / total * 100))
        for idx, (platform, app_name, rating) in enumerate(APP_STORE_RATING_PROXY, start=1)
    ]


def format_market_rows() -> list[tuple[str, str, str]]:
    total = IFPI_STREAMING_NOK + IFPI_DOWNLOAD_NOK + IFPI_PHYSICAL_NOK
    return [
        ("Streaming", money_nok(IFPI_STREAMING_NOK), pct(IFPI_STREAMING_NOK / total * 100)),
        ("Downloads", money_nok(IFPI_DOWNLOAD_NOK), pct(IFPI_DOWNLOAD_NOK / total * 100)),
        ("Physical", money_nok(IFPI_PHYSICAL_NOK), pct(IFPI_PHYSICAL_NOK / total * 100)),
    ]


def rpm_table(title: str, unit: str, benchmarks: list[tuple[str, float]]) -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    body = []
    for volume in volumes:
        values = [money_usd(volume / 1000 * rpm) for _, rpm in benchmarks]
        body.append((f"{volume:,} {unit}", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def per_stream_table(title: str, benchmarks: list[tuple[str, float]]) -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    body = []
    for volume in volumes:
        values = [money_usd(volume * rate) for _, rate in benchmarks]
        body.append((f"{volume:,} Streams", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def monthly_release_rows() -> list[tuple[str, int, int]]:
    return [
        (month, STRICT_MONTHLY_RELEASES[month], WIDE_MONTHLY_RELEASES[month])
        for month in STRICT_MONTHLY_RELEASES
    ]


def release_summary_rows() -> list[tuple[str, object]]:
    strict_total = sum(STRICT_MONTHLY_RELEASES.values())
    wide_total = sum(WIDE_MONTHLY_RELEASES.values())
    high_month = max(WIDE_MONTHLY_RELEASES, key=WIDE_MONTHLY_RELEASES.get)
    low_month = min(WIDE_MONTHLY_RELEASES, key=WIDE_MONTHLY_RELEASES.get)
    return [
        ("Annual Releases, strict dated proxy", strict_total),
        ("Annual Releases, wide dated proxy", wide_total),
        ("MusicBrainz strict unique releases", MUSICBRAINZ_STRICT_UNIQUE_RELEASES),
        ("MusicBrainz wide unique releases", MUSICBRAINZ_WIDE_UNIQUE_RELEASES),
        ("Monthly Average, wide dated proxy", f"{wide_total / 12:.1f}"),
        ("Highest Month, wide proxy", f"{high_month} ({WIDE_MONTHLY_RELEASES[high_month]})"),
        ("Lowest Month, wide proxy", f"{low_month} ({WIDE_MONTHLY_RELEASES[low_month]}; partial month)"),
    ]


def ai_interest_rows() -> list[tuple[str, str]]:
    return [
        (
            keyword,
            f"{score:.1f}",
            AI_TREND_MAX[keyword],
            f"{AI_TREND_NONZERO_WEEKS[keyword]} / 53",
        )
        for keyword, score in AI_TRENDS.items()
    ]


def ai_interest_index() -> float:
    core_keywords = ["Suno", "Udio", "AI Music"]
    return sum(AI_TRENDS[keyword] for keyword in core_keywords) / len(core_keywords)


def ai_interest_index_all_terms() -> float:
    return sum(AI_TRENDS.values()) / len(AI_TRENDS)


def generate_report() -> str:
    report = f"""# Norway Norwegian-Language AI Music Market Research

Report date: {REPORT_DATE}

## Executive Summary

Norwegian-language AI music is worth small-scale testing. Norway is not a large-population market, but internet penetration is high, recorded music consumption is strongly streaming-led, Norwegian-language content supply is limited, and Spotify clearly leads the Norway App Store user-scale proxy.

Final judgment: **Market Opportunity = Medium**  
Recommendation: **Monitor / Small-Scale Test**

## 1. Platform Availability & Market Structure

### 1.1 Main Platform User-Scale Proxy Ranking

{rows(["Rank", "Platform", "Norway App Store App", "Rating Count", "Approx. Proxy Share"], proxy_share_rows())}

Note: Approx. Proxy Share = Norway App Store rating count for the app / total rating count across the checked music apps. It is not official market share, downloads, or MAU. Apple Music may be undercounted because it is integrated into iOS. Amazon Music was not included because the Norway App Store lookup did not return a clear official app result.

### 1.2 Verified Market Structure

{rows(["Format", "Revenue", "Share"], format_market_rows())}

IFPI Norge official statistics show a strongly streaming-driven recorded music market. Even though the visible official chart data is 2020, the structure is useful: Norwegian-language AI music should prioritize streaming platforms, while downloads should be treated as secondary coverage.

## 2. Demand

### 2.1 Population & Internet Base

{rows(["Indicator", "Data", "Source"], [
    ("Norway population", int_fmt(POPULATION), "DataReportal Digital 2025"),
    ("Internet users", int_fmt(INTERNET_USERS), "DataReportal Digital 2025"),
    ("Internet penetration", pct(INTERNET_PENETRATION), "DataReportal / Kepios"),
])}

### 2.2 Music App / Streaming Usage

{rows(["Indicator", "Data", "Meaning"], [
    ("Recorded music streaming revenue share", "91.2%", "Streaming is the main paid music format, not just a discovery channel"),
    ("YouTube overall ad reach", int_fmt(YOUTUBE_AD_REACH), "Large online video/music discovery reach; not YouTube Music MAU"),
    ("YouTube reach vs population", pct(YOUTUBE_AD_REACH_POP_PCT), "Shows broad local digital content reach"),
    ("Spotify Norway App Store rating count", int_fmt(APP_STORE_RATING_PROXY[0][2]), "User-scale proxy; not MAU"),
])}

### 2.3 Demand Conclusion

Demand rating: **Medium**. Norway is a small-language market, but **5.55M internet users**, **99.0% internet penetration**, a **91.2% streaming revenue share**, and strong Spotify App Store proxy data show that local digital music usage is mature enough for controlled Norwegian-language AI song testing.

## 3. Monetization

### 3.1 YouTube / YouTube Music

Note: YouTube does not publish a fixed Norway music RPM. The tables below are planning estimates based on creator-reported and industry benchmark ranges, not guaranteed Norway-specific revenue.

#### YouTube Music / Art Track Plays

{rpm_table("YouTube Music / Art Track", "Plays", YOUTUBE_MUSIC_PLAY_BENCHMARKS)}

#### Own YouTube Channel Videos

{rpm_table("Own YouTube Channel Video", "Views", YOUTUBE_VIDEO_BENCHMARKS)}

#### Content ID / UGC Claimed Views

{rpm_table("Content ID / UGC", "Views", CONTENT_ID_BENCHMARKS)}

### 3.2 iTunes

{rows(["iTunes Norway", "Price / Revenue"], [
    ("Single Sale", money_nok(ITUNES_SINGLE_NOK)),
    ("Album Sale", money_nok(ITUNES_ALBUM_NOK)),
    ("Artist Share", "Depends on distributor / label contract"),
])}

Note: Norway iTunes prices are directly verified through Apple Search API samples. iTunes is useful for catalog coverage, but the IFPI market structure suggests downloads should not be the main growth channel.

### 3.3 Spotify

Note: Spotify does not publish a fixed Norway per-stream payout. The table below is a planning estimate based on creator-reported and industry benchmark ranges, not official Norway data.

{per_stream_table("Spotify Streams", SPOTIFY_BENCHMARKS)}

### 3.4 Apple Music

Note: Apple Music per-stream payout is not published as a fixed Norway rate. The table below uses public creator/industry benchmark ranges and should be treated as an estimate.

{per_stream_table("Apple Music Streams", APPLE_MUSIC_BENCHMARKS)}

### 3.5 Monetization Conclusion

Monetization rating: **Medium / scenario-based**. Apple Music has the higher per-stream estimate, Spotify has the strongest Norway App Store user-scale proxy, YouTube is useful for discovery and Content ID-style revenue paths, and iTunes is mainly supplemental.

## 4. Competition

{rows(["Indicator", "Data"], [
    ("Norwegian-language active artist-credit proxy", MUSICBRAINZ_WIDE_ACTIVE_ARTIST_CREDITS),
])}

Scope: MusicBrainz `lang:nor`, `lang:nob`, and `lang:nno` release data, Jul 2025-Jun 25 2026, deduplicated by artist-credit. This means artists who released Norwegian-language music in the past 12 months, not all historical Norwegian-language artists.

Competition conclusion: **Medium-Low to Medium**. The active artist-credit proxy is smaller than large-language music markets, which supports testing new AI-assisted Norwegian-language content.

## 5. Supply

{rows(["Month", "Strict Releases", "Wide Releases"], monthly_release_rows())}

{rows(["Indicator", "Data"], release_summary_rows())}

Strict proxy = `lang:nor/nob/nno AND country:NO`; wide proxy = `lang:nor/nob/nno`. Monthly counts are grouped by actual release date after fetching MusicBrainz releases.

Supply conclusion: **High opportunity due to low saturation**. The wide dated proxy shows about **160 releases** across the past 12 months, or **13.3 per month**. For a niche-language AI music strategy, limited supply is an opportunity rather than a negative signal.

## 6. AI Music Acceptance

### 6.1 AI Interest

Scope: Google Trends Norway, Past 12 Months CSV export, 53 weekly data points.

{rows(["Keyword", "Average Trend Index", "Peak Index", "Nonzero Weeks"], ai_interest_rows())}

AI Interest Index = **{ai_interest_index():.1f} / 100**  
AI Interest Index including local term `KI-musikk` = **{ai_interest_index_all_terms():.1f} / 100**

AI acceptance conclusion: **Medium-Low to Medium**. `Suno` shows consistent search interest in Norway, and `AI Music` also has visible interest. `Udio` is much weaker, and the local-language term `KI-musikk` shows no measurable search volume in this export.

## 7. Final Assessment

1. Is the Norwegian-language market suitable for a niche-language AI music strategy?  
   **Yes, for controlled testing.** Norway is small in population, but that fits the goal of finding smaller language markets. High internet penetration and streaming-led music consumption make it suitable for low-cost validation.

2. Which platform has the strongest local user-scale proxy?  
   **Spotify.** Spotify has **792,892** Norway App Store ratings and accounts for **94.4%** of the checked music-app rating-count proxy.

3. Which platform has the strongest monetization?  
   **Apple Music has the highest per-stream estimate, while Spotify has the strongest platform-scale proxy.** YouTube should be treated as discovery plus secondary monetization. iTunes is coverage only.

4. Is Norwegian-language music competition intense?  
   **Medium-Low to Medium.** MusicBrainz shows **139** active Norwegian-language artist-credit proxies in the past 12 months.

5. Is Norwegian-language content supply low, and is that an opportunity?  
   **Yes.** The wide dated proxy shows **160** releases in the past 12 months. Low saturation is a positive opportunity signal for AI-assisted niche-language content testing.

6. Has the local market started showing AI music interest?  
   **Yes, but unevenly.** Google Trends Norway shows `Suno` at **58.3**, `AI Music` at **38.1**, `Udio` at **1.2**, and `KI-musikk` at **0.0**. The core AI Interest Index is **32.5/100**.

7. Is it worth continuing to release Norwegian-language AI music?  
   **Yes, for small-scale testing.** The best-supported case is Spotify-first distribution, with YouTube for discovery and Apple Music kept active for higher per-stream estimate coverage.

## Overall Rating

{rows(["Dimension", "Rating"], [
    ("Demand", "Medium"),
    ("Monetization", "Medium / scenario-based"),
    ("Competition", "Medium-Low to Medium"),
    ("Supply Opportunity", "High, due to low saturation"),
    ("AI Interest", "Medium-Low to Medium"),
])}

Final Market Opportunity: **Medium**

Recommendation: **Monitor / Small-Scale Test**
"""
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help="Markdown output file path. Defaults to Norway_Norwegian_AI_Music_Market_Report.md",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path
    output_path.write_text(generate_report(), encoding="utf-8-sig")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
