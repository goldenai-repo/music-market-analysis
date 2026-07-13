#!/usr/bin/env python3
"""
Generate the Oman Omani Arabic / Gulf Arabic AI music market report.

The script is snapshot-first: it stores public/API-verifiable desk-research
values as constants, then generates a Markdown report from those values.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


REPORT_DATE = "2026-07-02"
OUTPUT_FILE = "Oman_Omani_Arabic_AI_Music_Market_Report.md"


POPULATION = 5_400_000
INTERNET_USERS = 5_140_000
INTERNET_PENETRATION = 95.3
YOUTUBE_AD_REACH = 3_290_000
YOUTUBE_AD_REACH_POP_PCT = 60.9
YOUTUBE_AD_REACH_INTERNET_PCT = 64.0


APP_STORE_RATING_PROXY = [
    ("Spotify", "Spotify: Music and Podcasts", 39_095),
    ("SoundCloud", "SoundCloud: The Music You Love", 17_866),
    ("Anghami", "Anghami: Play Music & Podcasts", 10_091),
    ("Audiomack", "Audiomack - Play Music Offline", 2_157),
    ("YouTube Music", "YouTube Music", 1_957),
    ("Apple Music", "Apple Music", 886),
    ("Deezer", "Deezer: Music & Podcast Player", 96),
    ("Bandcamp", "Bandcamp", 4),
]


GCC_MUSIC_STREAMING_MARKET_2024_USD_M = 549.67
GCC_POPULATION_2024_M = 61.2
OMAN_GCC_POPULATION_2024_M = 5.3
GCC_GDP_2024_USD_BN = 2_300.0
OMAN_GDP_2024_USD_BN = 106.94
USD_PER_OMR = 2.6008


YOUTUBE_MUSIC_PLAY_BENCHMARKS = [
    ("Low $0.5 RPM", 0.50),
    ("Baseline $1 RPM", 1.00),
    ("High $2 RPM", 2.00),
]
YOUTUBE_VIDEO_BENCHMARKS = [
    ("Low $1 RPM", 1.00),
    ("Baseline $2 RPM", 2.00),
    ("High $3 RPM", 3.00),
]
CONTENT_ID_BENCHMARKS = [
    ("Low $0.25 RPM", 0.25),
    ("Baseline $0.75 RPM", 0.75),
    ("High $1.5 RPM", 1.50),
]
SPOTIFY_BENCHMARKS = [
    ("Low $0.0035", 0.0035),
    ("Baseline $0.0045", 0.0045),
    ("High $0.0052", 0.0052),
]
APPLE_MUSIC_BENCHMARKS = [
    ("Low $0.007", 0.007),
    ("Baseline $0.010", 0.010),
    ("High $0.012", 0.012),
]


ITUNES_SINGLE_USD = 1.29
ITUNES_ALBUM_BASE_USD = 9.99
ITUNES_ALBUM_SAMPLE_RANGE = "$8.99-$14.99"


# MusicBrainz proxy, queried on 2026-06-26.
# Scope: country:OM, Jul 2025-Jun 26 2026.
MONTHLY_COUNTRY_OM_RELEASES = {
    "2025-07": 3,
    "2025-08": 11,
    "2025-09": 6,
    "2025-10": 10,
    "2025-11": 9,
    "2025-12": 9,
    "2026-01": 3,
    "2026-02": 5,
    "2026-03": 2,
    "2026-04": 0,
    "2026-05": 1,
    "2026-06": 0,
}
MUSICBRAINZ_COUNTRY_OM_UNIQUE_RELEASES = 58
MUSICBRAINZ_COUNTRY_OM_ACTIVE_ARTIST_CREDITS = 45

# Soundcharts snapshot, queried on 2026-07-02.
# Filters: artist country OM, release date by month, no performance minimum.
# Local-language counts also use Lyrics: Language = Arabic (Beta).
SOUNDCHARTS_ARTIST_PROFILES = 164
SOUNDCHARTS_MONTHLY_OM_ARTIST_SONGS = {
    "2025-07": 44,
    "2025-08": 29,
    "2025-09": 28,
    "2025-10": 40,
    "2025-11": 20,
    "2025-12": 28,
    "2026-01": 14,
    "2026-02": 13,
    "2026-03": 5,
    "2026-04": 5,
    "2026-05": 5,
    "2026-06": 2,
}
SOUNDCHARTS_MONTHLY_OM_ARABIC_SONGS = {
    "2025-07": 0,
    "2025-08": 3,
    "2025-09": 1,
    "2025-10": 1,
    "2025-11": 0,
    "2025-12": 3,
    "2026-01": 2,
    "2026-02": 0,
    "2026-03": 0,
    "2026-04": 0,
    "2026-05": 0,
    "2026-06": 0,
}

AI_TRENDS = {
    "Suno": {"average": 32.4, "maximum": 100, "nonzero_weeks": 27},
    "Udio": {"average": 0.1, "maximum": 3, "nonzero_weeks": 1},
    "AI Music": {"average": 15.0, "maximum": 72, "nonzero_weeks": 17},
}
AI_TRENDS_WEEK_COUNT = 53
AI_REGIONAL_INTEREST = [
    ("Suno", "Muscat 100; Dhofar 83; Al Batinah 63 / 62; Ad Dakhiliyah 50; Ad Dhahirah 3"),
    ("Udio", "Muscat 100; No data can be displayed in other regions"),
    ("AI Music", "Muscat 100; Al Batinah 39; Dhofar 32; Ad Dakhiliyah 27"),
]


def pct(value: float) -> str:
    return f"{value:.1f}%"


def int_fmt(value: int | float) -> str:
    if isinstance(value, float) and not value.is_integer():
        return f"{value:,.1f}"
    return f"{int(value):,}"


def money_usd(value: float) -> str:
    return f"${value:,.2f}"


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
        body.append((f"{volume:,} streams", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def monthly_release_rows() -> list[tuple[str, int]]:
    return [
        (month, MONTHLY_COUNTRY_OM_RELEASES[month])
        for month in MONTHLY_COUNTRY_OM_RELEASES
    ]


def release_summary_rows() -> list[tuple[str, object]]:
    annual_total = sum(MONTHLY_COUNTRY_OM_RELEASES.values())
    high_month = max(MONTHLY_COUNTRY_OM_RELEASES, key=MONTHLY_COUNTRY_OM_RELEASES.get)
    low_value = min(MONTHLY_COUNTRY_OM_RELEASES.values())
    low_months = [month for month, value in MONTHLY_COUNTRY_OM_RELEASES.items() if value == low_value]
    return [
        ("Annual release count (country:OM proxy value)", annual_total),
        ("MusicBrainz country:OM duplicate release count", MUSICBRAINZ_COUNTRY_OM_UNIQUE_RELEASES),
        ("Average monthly release count (country:OM proxy value)", f"{annual_total / 12:.1f}"),
        ("Highest month", f"{high_month} ({MONTHLY_COUNTRY_OM_RELEASES[high_month]})"),
        ("Lowest month", f"{' / '.join(low_months)} ({low_value}; possible metadata gap)"),
    ]


def ai_regional_interest_rows() -> list[tuple[str, str]]:
    return AI_REGIONAL_INTEREST


def ai_interest_rows() -> list[tuple[str, str, int, str]]:
    return [
        (
            keyword,
            f"{values['average']:.1f}",
            values["maximum"],
            f"{values['nonzero_weeks']} / {AI_TRENDS_WEEK_COUNT}",
        )
        for keyword, values in AI_TRENDS.items()
    ]


def ai_interest_index() -> float:
    return sum(values["average"] for values in AI_TRENDS.values()) / len(AI_TRENDS)


def generate_report() -> str:
    population_based_market_usd_m = (
        GCC_MUSIC_STREAMING_MARKET_2024_USD_M
        * OMAN_GCC_POPULATION_2024_M
        / GCC_POPULATION_2024_M
    )
    gdp_based_market_usd_m = (
        GCC_MUSIC_STREAMING_MARKET_2024_USD_M
        * OMAN_GDP_2024_USD_BN
        / GCC_GDP_2024_USD_BN
    )
    market_midpoint_usd_m = (
        population_based_market_usd_m + gdp_based_market_usd_m
    ) / 2
    market_low_omr_m = gdp_based_market_usd_m / USD_PER_OMR
    market_high_omr_m = population_based_market_usd_m / USD_PER_OMR

    report = f"""# Omani Arabic/Gulf Arabic AI Music Market Research

Report Date: {REPORT_DATE}

## Executive Summary

Oman has high internet penetration and a YouTube advertising reach of about 3.29 million people. Its overall music streaming market is estimated at US$25.6M-$47.6M per year, providing a basis for small-scale song testing. This estimate is not Omani Arabic market revenue, and data on local-language supply, competition, platform MAU, and actual payouts remains incomplete. The Google Trends-based AI Interest Index is only 15.8/100, so the evidence does not support sustained large-scale investment at this stage.

Final Judgment: **Market Opportunity = Medium-Low**
Recommendation: **continued monitoring/small-scale testing**

## 1. Platform overview and market structure

### 1.1 Mainstream Music Platform User-Scale Proxy Ranking

{rows(["Rank", "Platform", "Oman App Store App", "Rating Count", "Approx. Proxy Share"], proxy_share_rows())}

Note: Approx. Proxy Share = the app's Oman App Store rating count / the total rating count across the checked music apps. It is not official market share, downloads, or monthly active users (MAU). Apple Music may be undercounted because it is integrated into iOS. TIDAL and Qobuz were excluded because the Oman App Store query did not return usable rating counts.

### 1.2 Market Size

{rows(["Metric", "Amount"], [
    ("GCC Music Streaming Market Size (2024)", f"${GCC_MUSIC_STREAMING_MARKET_2024_USD_M:.2f}M (approximately US$550 million)"),
    ("Based on Oman's proportion of GCC population", f"${population_based_market_usd_m:.1f}M (approximately US$47.6 million)"),
    ("Calculated as Oman's share of GCC GDP", f"${gdp_based_market_usd_m:.1f}M (approximately US$25.6 million)"),
    ("Oman music streaming market estimate range", f"${gdp_based_market_usd_m:.1f}M-${population_based_market_usd_m:.1f}M / year (approximately US$25.6 million-47.6 million)"),
    ("Midpoint reference value", f"${market_midpoint_usd_m:.1f}M / year (approximately US$36.6 million)"),
    ("Omani Rial Estimation Range", f"OMR {market_low_omr_m:.1f}M-{market_high_omr_m:.1f}M / year"),
])}

The GCC is the Gulf Cooperation Council and includes Oman, Saudi Arabia, the United Arab Emirates, Qatar, Kuwait and Bahrain. The above amount is based on Market Research Future's estimate of the GCC music streaming market of $549.67M in 2024, and is calculated based on GCC-Stat population data and 2024 GDP data, assuming that Oman accounts for 8.7% of the GCC population and 4.65% of GDP respectively. Therefore, it is a market size estimation and is not Oman's official revenue announcement.

## 2. Market demand

### 2.1 Population and Internet Access

{rows(["Metric", "Data", "Source"], [
    ("Total population of Oman", int_fmt(POPULATION), "DataReportal Digital 2025"),
    ("Internet users", int_fmt(INTERNET_USERS), "DataReportal Digital 2025"),
    ("Internet penetration rate", pct(INTERNET_PENETRATION), "DataReportal / Kepios"),
])}

### 2.2 YouTube reach

{rows(["Metric", "Data", "Meaning"], [
    ("YouTube total ad reach", int_fmt(YOUTUBE_AD_REACH), "YouTube ecosystem potential ad reach, not YouTube Music MAU"),
    ("YouTube reach as a share of total population", pct(YOUTUBE_AD_REACH_POP_PCT), "Measures video-discovery channel reach"),
    ("YouTube reach as a share of internet users", pct(YOUTUBE_AD_REACH_INTERNET_PCT), "Measures online content-channel reach"),
])}

### 2.3 Demand Conclusion

Demand Rating: **Medium**. Oman has a population of **5.4 million** and **5.14 million** Internet users. YouTube ads reach approximately **3.29 million** people, providing an audience base for small-scale song testing.

## 3. Platform monetization

### 3.1 YouTube / YouTube Music

Note: YouTube does not publish fixed RPMs for Omani music content. The following is a planning estimate based on creators’ publicly reported examples and industry ranges, and is not official or guaranteed revenue for Oman.

#### YouTube Music / Art Track Play

{rpm_table("YouTube Music / Art Track", "Streams", YOUTUBE_MUSIC_PLAY_BENCHMARKS)}

#### Own YouTube channel videos

{rpm_table("Own YouTube channel videos", "views", YOUTUBE_VIDEO_BENCHMARKS)}

#### Content ID / UGC claimed for viewing

{rpm_table("Content ID / UGC", "Views", CONTENT_ID_BENCHMARKS)}

### 3.2 Anghami

{rows(["Anghami Metric", "Data"], [
    ("Oman App Store rating number", int_fmt(APP_STORE_RATING_PROXY[2][2])),
    ("Approx. App Store proxy share", pct(APP_STORE_RATING_PROXY[2][2] / sum(r for _, _, r in APP_STORE_RATING_PROXY) * 100)),
    ("Payout model", "No published fixed Oman per-stream payout"),
    ("Role in Oman Strategy", "Important regional Arabic platform should be included in distribution and discovery channels"),
])}

Description: Anghami is an Arabic music platform for MENA and therefore more relevant to Oman than Finland or Norway. This report does not provide a guaranteed revenue estimate as no public revenue per stream for Oman was found.

### 3.3 Spotify

Note: Spotify does not report fixed revenue per stream for Oman. The following table is a planning estimate based on creators’ publicly reported examples and industry ranges, and is not Spotify Oman’s official data.

{per_stream_table("Spotify streams", SPOTIFY_BENCHMARKS)}

### 3.4 Apple Music

Note: Apple Music does not report fixed revenue per stream for Oman. The table below uses publicly available creator and industry reference ranges and should be used as estimates.

{per_stream_table("Apple Music stream volume", APPLE_MUSIC_BENCHMARKS)}

### 3.5 iTunes

{rows(["iTunes Oman", "Price / Revenue"], [
    ("Single price", money_usd(ITUNES_SINGLE_USD)),
    ("Album selling price", f"Basic sample {money_usd(ITUNES_ALBUM_BASE_USD)}; observation range {ITUNES_ALBUM_SAMPLE_RANGE}"),
    ("artist share", "depends on publisher or record company contract"),
])}

Description: Oman iTunes prices are directly verified via Apple Search API samples. iTunes can be used to supplement library coverage, but should not be used as the primary growth channel.

### 3.6 Monetization Conclusion

Monetization Rating: **Medium / Based on reference ranges**. Apple Music has the higher public per-stream benchmark, Spotify leads the Oman App Store user-scale proxy, Anghami supports Arabic/MENA discovery, and YouTube offers both content discovery and Content ID revenue paths. None of these platforms publishes a fixed local per-stream payout for Oman.

## 4. Level of competition

{rows(["Metric", "Data"], [
    ("MusicBrainz active artist-credit proxy, country:OM releases", MUSICBRAINZ_COUNTRY_OM_ACTIVE_ARTIST_CREDITS),
    ("MusicBrainz deduplicated releases, country:OM", MUSICBRAINZ_COUNTRY_OM_UNIQUE_RELEASES),
    ("Soundcharts artist-country OM profiles", SOUNDCHARTS_ARTIST_PROFILES),
])}

Scope: MusicBrainz `country:OM` release data, from July 2025 to June 26, 2026, deduplicated by artist-credit. Omani Arabic dialects are not stably annotated in public music databases, so this is a proxy indicator at the national level and does not fully represent the number of creators of this dialect.

Soundcharts' **164** profiles are all-time artist-country OM results without restrictions on language or recent activity status, so are not directly comparable to MusicBrainz's 45 active artist credits.

Competition Conclusion: **Low-to-Moderate, but local language competition still cannot be accurately judged**. Both databases show that the number of artists associated with Oman is limited, but the methodology is different, and neither is the official total number of creators.

## 5. Content supply

{rows(["Month", "MusicBrainz country:OM Release Count"], monthly_release_rows())}

{rows(["Metric", "Data"], release_summary_rows())}

Scope: July 2025 to June 26, 2026. `country:OM` indicates that the country of release is marked as Oman and does not limit the song language.

### Soundcharts Supply Proxy

{rows(
    ["Month", "Songs with an OM-Tagged Artist", "Songs with Arabic Lyrics (Beta)"],
    [
        (
            month,
            SOUNDCHARTS_MONTHLY_OM_ARTIST_SONGS[month],
            SOUNDCHARTS_MONTHLY_OM_ARABIC_SONGS[month],
        )
        for month in SOUNDCHARTS_MONTHLY_OM_ARTIST_SONGS
    ],
)}

{rows(["Metric", "Data"], [
    ("Soundcharts songs with an OM-tagged artist", sum(SOUNDCHARTS_MONTHLY_OM_ARTIST_SONGS.values())),
    ("Songs with Arabic lyrics", sum(SOUNDCHARTS_MONTHLY_OM_ARABIC_SONGS.values())),
    ("Monthly Average OM Artist Country Tag Songs", f"{sum(SOUNDCHARTS_MONTHLY_OM_ARTIST_SONGS.values()) / 12:.1f}"),
    ("Monthly average Arabic lyrics songs", f"{sum(SOUNDCHARTS_MONTHLY_OM_ARABIC_SONGS.values()) / 12:.1f}"),
    ("Highest month, all languages", "2025-07 (44)"),
    ("Lowest month, all languages", "2026-06 (2; platform snapshot month is incomplete)"),
    ("Highest Month, Arabic Lyrics", "2025-08 / 2025-12 (3)"),
    ("Lowest month, Arabic lyrics", "Multiple zero months"),
])}

Soundcharts methodology: artist country = Oman, release date is July 2025 to June 2026, no minimum stream threshold is set; the Arabic column also uses Beta `Lyrics: Language = Arabic`. Songs count as long as at least one named artist carries the OM country tag, so it's broader than album/single releases; Arabic doesn't specifically refer to the Omani dialect either.

Supply conclusion: **The publicly visible supply is small, forming an initial opportunity signal**. Soundcharts recorded **233** songs with OM artist country tags, of which only **10** were identified as having Arabic lyrics; this is wider coverage than MusicBrainz, but still not representative of official full releases for the Omani market.

## 6. AI music acceptance

### 6.1 AI Search Interest

#### National Weekly Trends

{rows(["Keywords", "Average index", "Peak index", "Weeks with data"], ai_interest_rows())}

AI Interest Index = **{ai_interest_index():.1f} / 100**

Coverage: Google Trends Oman, last 12 months, **{AI_TRENDS_WEEK_COUNT} weeks**. AI Interest Index is the arithmetic mean of the average trend index of the three keywords Suno, Udio and AI Music.

#### Regional distribution

{rows(["Keywords", "Regional Trend Index"], ai_regional_interest_rows())}

In the regional data, each keyword has its highest region of 100, so the absolute search volume cannot be directly compared between different keywords; the two Al Batinah entries in the original file are retained at 63 / 62.

AI adoption conclusion: **Low to Medium-Low**. Suno has the highest search interest and covers the widest area, AI Music has some intermittent interest, Udio search volume is close to zero; Muscat is the highest measurable area for the three keywords.

## 7. Final evaluation

1. Is the Omani Arabic/Gulf Arabic market suitable for a localized AI music strategy?
   **Suitable for low-cost controlled testing.** Oman has a population of **5.4 million**, **95.3%** internet penetration, and a YouTube advertising reach of approximately **3.29 million**. The overall streaming market appears large enough for testing, but this cannot be treated as Omani Arabic market revenue.

2. Which platform has the strongest proxy signal for local user scale?
   **Spotify ranks first in the Oman App Store rating-count proxy**, with **39,095** ratings and a **54.2%** proxy share. SoundCloud and Anghami are also worth monitoring.

3. Is Anghami important to the Omani market?
   **Important.** Anghami ranks third in the Oman App Store rating-count proxy. As an Arabic music platform serving MENA, it should be included in distribution and channel tracking.

4. Which platform has the strongest monetization ability?
   **Apple Music has the highest public per-stream benchmark; Spotify has the strongest local scale proxy.** YouTube is better suited to content discovery and Content ID monetization, but these estimates are not official Oman rates.

5. Is there a lot of competition in Omani Arabic/Gulf Arabic music?
   **Proxy results suggest low-to-moderate competition, but local-language competition cannot be measured accurately.** MusicBrainz records **45** active artist credits and Soundcharts records **164** all-time OM artist-country profiles; neither has a reliable Omani-dialect creator field.

6. Is there less content supply and does it create an opportunity?
   **Yes, but only as a preliminary opportunity signal.** Soundcharts recorded **233** OM artist country tag songs, **10** of which were identified as having Arabic lyrics; MusicBrainz's original data is still retained, but neither methodology is an official distribution total.

7. Has the local market shown interest in AI music?
   **There is preliminary interest, but overall interest remains low.** AI Interest Index is **15.8/100**; Suno has the highest search interest, AI Music shows some search interest, and Udio is close to zero.

8. Is it worth continuing to release Omani Arabic/Gulf Arabic AI music?
   **Worth testing at small scale, but not suitable for sustained large-scale investment.** Prioritize using Spotify, Anghami and YouTube to verify real stream and retention performance, while retaining Apple Music; whether to expand investment should be determined by actual test results.

## Comprehensive rating

{rows(["Dimension", "Rating"], [
    ("Market Demand", "Medium"),
        ("Monetization", "Medium / Based on reference ranges"),
    ("Competition level", "Low-to-Moderate / Insufficient Local Language Data"),
        ("Content supply opportunity", "Medium / Insufficient local-language data"),
    ("AI Search Interest", "Low to Medium-Low"),
    ("Platform fit", "Medium"),
])}

Final Market Opportunity: **Medium-Low**

Recommendation: **continued monitoring/small-scale testing**
"""
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default=OUTPUT_FILE,
        help="Markdown output file path. Defaults to Oman_Omani_Arabic_AI_Music_Market_Report.md",
    )
    args = parser.parse_args()

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path(__file__).resolve().parent / output_path
    output_path.write_text(generate_report(), encoding="utf-8-sig")
    print(f"Wrote {output_path}")


if __name__ == "__main__":
    main()
