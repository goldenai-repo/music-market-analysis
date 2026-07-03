#!/usr/bin/env python3
"""Generate the Kuwait Arabic / Gulf Arabic AI music market report."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


REPORT_DATE = "2026-07-02"
OUTPUT_FILE = "Kuwait_Kuwaiti_Arabic_AI_Music_Market_Report.md"


POPULATION = 4_980_000
INTERNET_USERS = 4_940_000
INTERNET_PENETRATION = 99.0
YOUTUBE_AD_REACH = 3_240_000
YOUTUBE_AD_REACH_POP_PCT = 65.0
YOUTUBE_AD_REACH_INTERNET_PCT = 65.7


APP_STORE_RATING_PROXY = [
    ("Spotify", "Spotify: Music and Podcasts", 74_353),
    ("SoundCloud", "SoundCloud: The Music You Love", 37_916),
    ("Anghami", "Anghami: Play Music & Podcasts", 28_197),
    ("YouTube Music", "YouTube Music", 4_938),
    ("Audiomack", "Audiomack - Play Music Offline", 1_859),
    ("Apple Music", "Apple Music", 1_112),
    ("Deezer", "Deezer: Music & Podcast Player", 309),
    ("Bandcamp", "Bandcamp", 8),
]


GCC_MUSIC_STREAMING_MARKET_2024_USD_M = 549.67
GCC_POPULATION_2024_M = 61.2
KUWAIT_GCC_POPULATION_2024_M = 4.9
GCC_GDP_2024_USD_BN = 2_300.0
KUWAIT_GDP_2024_USD_BN = 160.23


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


# MusicBrainz snapshot queried on 2026-06-30.
# Artist profiles use country:KW. Releases are linked to those artist MBIDs.
MUSICBRAINZ_KUWAIT_ARTIST_PROFILES = 100
MUSICBRAINZ_ACTIVE_KUWAIT_ARTIST_PROFILES = 7
MONTHLY_KUWAIT_ARTIST_RELEASES = {
    "2025-07": 0,
    "2025-08": 2,
    "2025-09": 1,
    "2025-10": 1,
    "2025-11": 0,
    "2025-12": 1,
    "2026-01": 1,
    "2026-02": 0,
    "2026-03": 2,
    "2026-04": 0,
    "2026-05": 1,
    "2026-06": 0,
}
MONTHLY_KUWAIT_ARTIST_ARABIC_RELEASES = {
    "2025-07": 0,
    "2025-08": 1,
    "2025-09": 0,
    "2025-10": 1,
    "2025-11": 0,
    "2025-12": 0,
    "2026-01": 0,
    "2026-02": 0,
    "2026-03": 0,
    "2026-04": 0,
    "2026-05": 1,
    "2026-06": 0,
}

# Soundcharts snapshot, queried on 2026-07-02.
# Filters: artist country KW, release date by month, no performance minimum.
# Local-language counts also use Lyrics: Language = Arabic (Beta).
SOUNDCHARTS_ARTIST_PROFILES = 302
SOUNDCHARTS_MONTHLY_KW_ARTIST_SONGS = {
    "2025-07": 65,
    "2025-08": 53,
    "2025-09": 51,
    "2025-10": 154,
    "2025-11": 104,
    "2025-12": 29,
    "2026-01": 73,
    "2026-02": 25,
    "2026-03": 28,
    "2026-04": 50,
    "2026-05": 20,
    "2026-06": 9,
}
SOUNDCHARTS_MONTHLY_KW_ARABIC_SONGS = {
    "2025-07": 3,
    "2025-08": 3,
    "2025-09": 4,
    "2025-10": 9,
    "2025-11": 7,
    "2025-12": 3,
    "2026-01": 5,
    "2026-02": 6,
    "2026-03": 3,
    "2026-04": 5,
    "2026-05": 3,
    "2026-06": 0,
}

AI_TRENDS = {
    "Suno": {"average": 38.4, "maximum": 100, "nonzero_weeks": 34},
    "Udio": {"average": 0.1, "maximum": 3, "nonzero_weeks": 2},
    "AI Music": {"average": 24.2, "maximum": 72, "nonzero_weeks": 28},
}
AI_TRENDS_WEEK_COUNT = 53
AI_REGIONAL_INTEREST = [
    (
        "Suno",
        "Greater Mubarak Al-Kabeer Governorate 100; Farwaniya Governorate 85; Al Ahmadi Governorate 72; "
        "Khawali Province 70; Capital Province 53; Jahra Province 47",
    ),
    ("Udio", "Farwaniya Governorate 100; Hawalli Governorate 36; no data to display for other regions"),
    (
        "AI Music",
        "Farwaniya Governorate 100; Al Ahmadi Governorate 34; Greater Mubarak Al-Kabeer Governorate 27; "
        "Khawali Province 25; Capital Province 18; Jahra Province less than 1",
    ),
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
        for idx, (platform, app_name, rating) in enumerate(
            APP_STORE_RATING_PROXY, start=1
        )
    ]


def rpm_table(
    title: str, unit: str, benchmarks: list[tuple[str, float]]
) -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    body = []
    for volume in volumes:
        values = [money_usd(volume / 1000 * rpm) for _, rpm in benchmarks]
        body.append((f"{volume:,} {unit}", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def per_stream_table(
    title: str, benchmarks: list[tuple[str, float]]
) -> str:
    volumes = [1_000, 10_000, 100_000, 1_000_000]
    body = []
    for volume in volumes:
        values = [money_usd(volume * rate) for _, rate in benchmarks]
        body.append((f"{volume:,} streams", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def monthly_release_rows() -> list[tuple[str, int, int]]:
    return [
        (
            month,
            MONTHLY_KUWAIT_ARTIST_RELEASES[month],
            MONTHLY_KUWAIT_ARTIST_ARABIC_RELEASES[month],
        )
        for month in MONTHLY_KUWAIT_ARTIST_RELEASES
    ]


def release_summary_rows() -> list[tuple[str, object]]:
    all_total = sum(MONTHLY_KUWAIT_ARTIST_RELEASES.values())
    arabic_total = sum(MONTHLY_KUWAIT_ARTIST_ARABIC_RELEASES.values())
    high_value = max(MONTHLY_KUWAIT_ARTIST_RELEASES.values())
    low_value = min(MONTHLY_KUWAIT_ARTIST_RELEASES.values())
    high_months = [
        month
        for month, value in MONTHLY_KUWAIT_ARTIST_RELEASES.items()
        if value == high_value
    ]
    low_months = [
        month
        for month, value in MONTHLY_KUWAIT_ARTIST_RELEASES.items()
        if value == low_value
    ]
    return [
        ("Kuwait-associated artist releases", all_total),
        ("Releases tagged as Arabic", arabic_total),
        ("Average monthly release count", f"{all_total / 12:.1f}"),
        ("Average monthly Arabic-tagged release count", f"{arabic_total / 12:.1f}"),
        ("Highest month", f"{' / '.join(high_months)} ({high_value})"),
        ("Lowest month", f"{' / '.join(low_months)} ({low_value})"),
    ]


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
    return sum(
        values["average"] for values in AI_TRENDS.values()
    ) / len(AI_TRENDS)


def generate_report() -> str:
    population_based_market_usd_m = (
        GCC_MUSIC_STREAMING_MARKET_2024_USD_M
        * KUWAIT_GCC_POPULATION_2024_M
        / GCC_POPULATION_2024_M
    )
    gdp_based_market_usd_m = (
        GCC_MUSIC_STREAMING_MARKET_2024_USD_M
        * KUWAIT_GDP_2024_USD_BN
        / GCC_GDP_2024_USD_BN
    )
    market_low_usd_m = min(
        population_based_market_usd_m, gdp_based_market_usd_m
    )
    market_high_usd_m = max(
        population_based_market_usd_m, gdp_based_market_usd_m
    )
    market_midpoint_usd_m = (
        population_based_market_usd_m + gdp_based_market_usd_m
    ) / 2

    report = f"""# Kuwaiti Arabic/Gulf Arabic AI Music Market Research

Report Date: {REPORT_DATE}

## Executive Summary

Kuwait has a population of approximately 4.98 million, 99.0% internet penetration, and a YouTube advertising reach of about 3.24 million people. Its overall music streaming market is estimated at US$38.3M-$44.0M per year. Spotify leads the Kuwait App Store rating-count proxy, while Anghami ranks third. Public databases show a limited supply of Kuwait-associated artists and Arabic releases, although coverage is incomplete. The Google Trends-based AI Interest Index is 20.9/100, mainly driven by Suno. The market is therefore suitable for small-scale testing, not an immediate large-scale rollout.

Final Judgment: **Market Opportunity = Moderate**
Recommendation: **continued monitoring/small-scale testing**

## 1. Platform overview and market structure

### 1.1 Mainstream Music Platform User-Scale Proxy Ranking

{rows(["Rank", "Platform", "Kuwait App Store App", "Rating Count", "Approx. Proxy Share"], proxy_share_rows())}

Note: Approx. Proxy Share = the app's Kuwait App Store rating count / the total rating count across the checked music apps. Data was queried through the [Apple Lookup API](https://itunes.apple.com/lookup?id=324684580&country=kw) on 2026-06-30. It is not official market share, downloads, or monthly active users (MAU). Apple Music may be undercounted because it is integrated into iOS. TIDAL and Qobuz did not return usable Kuwait App Store records and were not included.

### 1.2 Market Size

{rows(
    ["Metric", "Amount"],
    [
        ("GCC music streaming market size (2024)", "$549.67M (approximately US$550 million)"),
        (
            "Based on Kuwait's share of GCC population",
            f"${population_based_market_usd_m:.1f}M (approximately US${population_based_market_usd_m:.1f} million)",
        ),
        (
            "Calculated as Kuwait's share of GCC GDP",
            f"${gdp_based_market_usd_m:.1f}M (approximately US${gdp_based_market_usd_m:.1f} million)",
        ),
        (
            "Kuwait Music Streaming Market Estimation Range",
            f"${market_low_usd_m:.1f}M-${market_high_usd_m:.1f}M / year",
        ),
        ("Midpoint reference value", f"${market_midpoint_usd_m:.1f}M / year"),
    ],
)}

The GCC is the Gulf Cooperation Council and includes Kuwait, Saudi Arabia, the United Arab Emirates, Qatar, Oman and Bahrain. The above amounts are based on [Market Research Future](https://www.marketresearchfuture.com/reports/gcc-music-streaming-market-60943)'s 2024 GCC music streaming market of $549.67M, and then use GCC-Stat's [GCC population 61.2 million, Kuwait population 4.9 million](https://www.argaam.com/en/article/articledetail/id/1827299), [GCC GDP is about $2.3T](https://gccstat.org/images/gccstat/docman/publications/GCC_YEAR_BOOK_2024.pdf) and the World Bank’s [Kuwait GDP $160.23B](https://data.worldbank.org/country/KW), calculated by population and GDP respectively; it is an estimate of the overall streaming market, not the official revenue of Kuwait Arabic music.

## 2. Market demand

### 2.1 Population and Internet Access

{rows(
    ["Metric", "Data", "Source"],
    [
        ("Total population of Kuwait", int_fmt(POPULATION), "[DataReportal Digital 2025](https://datareportal.com/reports/digital-2025-kuwait)"),
        ("Internet users", int_fmt(INTERNET_USERS), "DataReportal / Kepios"),
        ("Internet penetration rate", pct(INTERNET_PENETRATION), "DataReportal / Kepios"),
    ],
)}

### 2.2 YouTube reach

{rows(
    ["Metric", "Data", "Meaning"],
    [
        ("YouTube total ad reach", int_fmt(YOUTUBE_AD_REACH), "YouTube ecosystem potential ad reach, not YouTube Music MAU"),
        ("YouTube reach as a share of total population", pct(YOUTUBE_AD_REACH_POP_PCT), "Measures video-discovery channel reach"),
        ("YouTube reach as a share of internet users", pct(YOUTUBE_AD_REACH_INTERNET_PCT), "Measures online content-channel reach"),
    ],
)}

### 2.3 Demand Conclusion

Demand Rating: **Medium**. Kuwait has a population of approximately **4.98 million** and **4.94 million** Internet users, and YouTube ads reach approximately **3.24 million**; the population size is limited, but the digital channel coverage is high enough to support small-scale song testing.

## 3. Platform monetization

### 3.1 YouTube / YouTube Music

Note: YouTube does not publish fixed RPMs for Kuwaiti music content. The following is a budget range combined with public industry data such as [Duetti Music Economics Report](https://report.duetti.co/), which is not Kuwait’s official or guaranteed revenue; [YouTube for Artists](https://artists.youtube/intl/en-GB/resources/monetization/) illustrates that artists’ revenue will change with advertising, subscriptions and rights relationships.

#### YouTube Music / Art Track Play

{rpm_table("YouTube Music / Art Track", "Streams", YOUTUBE_MUSIC_PLAY_BENCHMARKS)}

#### Own YouTube channel videos

{rpm_table("Own YouTube channel videos", "views", YOUTUBE_VIDEO_BENCHMARKS)}

#### Content ID / UGC claimed for viewing

{rpm_table("Content ID / UGC", "Views", CONTENT_ID_BENCHMARKS)}

### 3.2 Anghami

{rows(
    ["Anghami Metrics", "Data"],
    [
        ("Number of Kuwait App Store ratings", "28,197"),
        ("Approx. App Store proxy share", "19.0%"),
        ("Payout model", "No fixed Kuwait per-stream payout found"),
        ("Role in Kuwait strategy", "Regional Arabic platforms should be included in distribution and channel testing"),
    ],
)}

Description: Anghami is an Arabic music platform for MENA, ranked third among Kuwait App Store rating-count proxies. Since fixed Kuwait per-stream revenue is not disclosed, this report does not provide a guaranteed revenue estimate.

### 3.3 Spotify

Note: Spotify does not have a fixed per-stream rate in Kuwait. The following table combines creator and industry public data such as [Duetti Music Economics Report](https://report.duetti.co/) to form a planning range, and is not the official revenue of Spotify Kuwait.

{per_stream_table("Spotify streams", SPOTIFY_BENCHMARKS)}

### 3.4 Apple Music

Note: Apple Music does not have a fixed per-stream rate in Kuwait. The table below combines public creator and industry data such as [Duetti Music Economics Report](https://report.duetti.co/) to form a reference range and should be used as an estimate.

{per_stream_table("Apple Music stream volume", APPLE_MUSIC_BENCHMARKS)}

### 3.5 iTunes

{rows(
    ["iTunes Kuwait", "Price / Revenue"],
    [
        ("Single price", "Apple Search API did not return a verifiable price"),
        ("Album Price", "Apple Search API did not return a verifiable price"),
        ("Artist share", "Depends on the distributor or record-label contract"),
    ],
)}

Note: Kuwait Storefront's Apple Search API can return song and album records, but this sample does not return the purchase price, so prices from other countries are not used instead.

### 3.6 Monetization Conclusion

Monetization Rating: **Medium / Based on reference ranges**. Apple Music has the higher public per-stream benchmark, Spotify has the strongest local scale proxy, Anghami is relevant for Arabic audiences, and YouTube offers both discovery and Content ID revenue paths. No platform publishes a fixed local per-stream payout for Kuwait.

## 4. Level of competition

{rows(
    ["Metrics", "Data"],
    [
        ("MusicBrainz Kuwait related artist profile", int_fmt(MUSICBRAINZ_KUWAIT_ARTIST_PROFILES)),
        ("Kuwait-affiliated artists with visible releases in the past 12 months", int_fmt(MUSICBRAINZ_ACTIVE_KUWAIT_ARTIST_PROFILES)),
        ("Soundcharts artist-country KW artist profile", int_fmt(SOUNDCHARTS_ARTIST_PROFILES)),
    ],
)}

Methodology: First obtain artist profiles whose main associated country is Kuwait through `artist country:KW` of [MusicBrainz Search API](https://musicbrainz.org/doc/MusicBrainz_API/Search), and then query the releases of these artists from July 2025 to June 2026. The artist country field and work inclusion may be missing, so it is a public database proxy value, not the total number of Kuwaiti creators.

Soundcharts' **302** profiles are all-time artist-country KW results without restrictions on language or recent active status, so they are not directly comparable to MusicBrainz's 7 recently active artists.

Competition conclusion: **Publicly visible competition is low to moderate, but data coverage is incomplete**. Both databases show that the number of artists associated with Kuwait is limited, but the methodology is different, and neither is the official total number of creators.

## 5. Content supply

{rows(
    ["Month", "Kuwait-Associated Artist Releases", "Arabic-Tagged Releases"],
    monthly_release_rows(),
)}

{rows(["Metric", "Data"], release_summary_rows())}

Scope: July 2025 to June 2026. Arabic supply uses the MusicBrainz `lang:ara` tag, which represents Arabic generally and not the Kuwaiti dialect specifically. The database may also miss releases with incomplete language metadata or works that have not been indexed.

### Soundcharts Supply Proxy

{rows(
    ["Month", "Songs with a KW-Tagged Artist", "Songs with Arabic Lyrics (Beta)"],
    [
        (
            month,
            SOUNDCHARTS_MONTHLY_KW_ARTIST_SONGS[month],
            SOUNDCHARTS_MONTHLY_KW_ARABIC_SONGS[month],
        )
        for month in SOUNDCHARTS_MONTHLY_KW_ARTIST_SONGS
    ],
)}

{rows(
    ["Metrics", "Data"],
    [
        ("Soundcharts songs with a KW-tagged artist", sum(SOUNDCHARTS_MONTHLY_KW_ARTIST_SONGS.values())),
        ("Songs with Arabic lyrics", sum(SOUNDCHARTS_MONTHLY_KW_ARABIC_SONGS.values())),
        ("Monthly average KW artist country tag songs", f"{sum(SOUNDCHARTS_MONTHLY_KW_ARTIST_SONGS.values()) / 12:.1f}"),
        ("Monthly average Arabic lyrics songs", f"{sum(SOUNDCHARTS_MONTHLY_KW_ARABIC_SONGS.values()) / 12:.1f}"),
        ("Highest month, all languages", "2025-10 (154)"),
        ("Lowest month, all languages", "2026-06 (9; platform snapshot month is incomplete)"),
        ("Highest month, Arabic lyrics", "2025-10 (9)"),
        ("Lowest month, Arabic lyrics", "2026-06 (0; platform snapshot month incomplete)"),
    ],
)}

Soundcharts methodology: artist country = Kuwait, release date is July 2025 to June 2026, no minimum stream threshold is set; the Arabic column also uses Beta `Lyrics: Language = Arabic`. Songs count as long as at least one named artist carries the KW country tag, so it's broader than album/single releases; Arabic doesn't specifically refer to the Kuwaiti dialect either.

Supply conclusion: **The publicly visible supply is small, forming an initial opportunity signal**. Soundcharts recorded **661** songs with KW artist country tags, **51** of which were identified as having Arabic lyrics; MusicBrainz's original **9 / 3** proxies remain, but Soundcharts indicates that the actual visible supply is significantly higher than the single database results.

## 6. AI music acceptance

### 6.1 AI Search Interest

{rows(
    ["Keywords", "Average index", "Peak index", "Weeks with data"],
    ai_interest_rows(),
)}

AI Interest Index = **{ai_interest_index():.1f} / 100**

Scope: [Google Trends Kuwait](https://trends.google.com/trends/explore?date=today%2012-m&geo=KW&q=Suno,Udio,AI%20Music) Past 12 months, **53 weeks**. AI Interest Index is the arithmetic mean of the average trend index of the three keywords Suno, Udio and AI Music.

#### Regional distribution

{rows(["Keywords", "Regional Trend Index"], AI_REGIONAL_INTEREST)}

The region data for each keyword is based on its highest region of 100, so absolute search volumes cannot be directly compared between different keywords.

AI adoption conclusion: **Low to Medium-Low**. Suno has the highest average search interest and covers all six provinces, AI Music shows some search interest, and Udio has almost no sustained searches; these data indicate local interest in AI music tools, but cannot directly prove that listeners have accepted AI-generated songs.

## 7. Final evaluation

1. Is the Kuwaiti Arabic/Gulf Arabic market suitable for a localized AI music strategy?
   **Suitable for small-scale testing.** The population is approximately **4.98 million**, the Internet penetration rate is **99.0%**, and digital channels are fully covered, which is in line with the test objectives of the smaller-language market.

2. Which platform has the strongest proxy signal for local user scale?
   **Spotify ranks first.** It has **74,353** Kuwait App Store ratings and an approximate proxy share of **50.0%**; SoundCloud and Anghami rank second and third.

3. Is Anghami important to the Kuwaiti market?
   **Important.** Anghami has an approximate local rating-count proxy share of **19.0%** and directly serves the MENA Arabic market.

4. Which platform has the strongest monetization ability?
   **Apple Music has the higher public per-stream benchmark; Spotify has the stronger local scale proxy.** YouTube supports discovery and Content ID monetization, but the estimates are not official Kuwait rates.

5. Is there a lot of competition in Kuwaiti Arabic/Gulf Arabic music?
   **Publicly visible competition is low-to-moderate.** MusicBrainz has **7** recently active Kuwait-associated artist profiles, while Soundcharts has **302** all-time profiles tagged to artist country KW. The methodologies differ, and neither value is a complete creator count.

6. Is there less content supply and does it create an opportunity?
   **Yes; this is a preliminary opportunity signal.** Soundcharts shows **661** songs with a KW-tagged artist, of which **51** are identified as having Arabic lyrics. The Arabic-lyrics count is limited relative to total supply, but actual platform data is needed for validation.

7. Has the local market shown interest in AI music?
   **There is preliminary interest, but overall interest remains low.** AI Interest Index is **20.9/100**; Suno has the highest search interest, AI Music shows some search interest, and Udio is close to zero.

8. Is it worth continuing to release Kuwaiti Arabic/Gulf Arabic AI music?
   **Worth advancing to a small-scale test.** Spotify, Anghami, and YouTube should be the primary test channels, with Apple Music as supplementary distribution. Expansion should depend on actual streams, completion rates, and repeat listening.

## Comprehensive rating

{rows(
    ["Dimension", "Rating"],
    [
        ("Market Demand", "Medium"),
        ("Monetization", "Medium / Based on reference ranges"),
        ("Competition level", "Low-to-Moderate / Incomplete Data Coverage"),
        ("Content supply opportunity", "High / Incomplete data coverage"),
        ("AI Search Interest", "Low to Medium-Low"),
        ("Platform fit", "Medium-High"),
    ],
)}

Final Market Opportunity: **Medium**

Recommendation: **continued monitoring/small-scale testing**
"""
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / OUTPUT_FILE,
        help="Markdown output path",
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(generate_report(), encoding="utf-8-sig")
    print(f"Wrote {args.output}")


if __name__ == "__main__":
    main()
