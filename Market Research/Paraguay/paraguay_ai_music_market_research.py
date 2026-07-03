#!/usr/bin/env python3
"""Generate the Paraguay Guarani-language AI music market report."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


REPORT_DATE = "2026-07-03"
OUTPUT_FILE = "Paraguay_Guarani_AI_Music_Market_Report.md"

POPULATION = 7_030_000
INTERNET_USERS = 5_840_000
INTERNET_PENETRATION = 83.1
YOUTUBE_AD_REACH = 4_300_000
YOUTUBE_AD_REACH_POP_PCT = 61.1
YOUTUBE_AD_REACH_INTERNET_PCT = 73.6

GUARANI_PRIMARY_SHARE = 27.9
BILINGUAL_SHARE = 38.7
GUARANI_PRIMARY_USERS = 1_587_817
BILINGUAL_USERS = 2_204_477

APP_STORE_RATING_PROXY = [
    ("Spotify", "Spotify: Music and Podcasts", 216_276, "1"),
    ("YouTube Music", "YouTube Music", 4_722, "7"),
    ("SoundCloud", "SoundCloud: Music and Playlists", 4_384, "Not in the top 50"),
    ("Deezer", "Deezer: Music and Podcasts", 3_705, "Not in the top 50"),
    ("Apple Music", "Apple Music", 2_668, "49"),
    ("Audiomack", "Audiomack - Stream Music", 2_085, "Not in the top 50"),
    ("Amazon Music", "Amazon Music: Music and Podcasts", 408, "Not in the top 50"),
    ("Claro Music", "Claro Music", 317, "Not in the top 50"),
    ("Bandcamp", "Bandcamp", 6, "Not in the top 50"),
]

RECORDED_MUSIC_2020_PYG_B = 39.1650
STREAMING_2020_PYG_B = 20.7035
PAID_AUDIO_2020_PYG_B = 10.4098
AD_AUDIO_2020_PYG_B = 8.4680
VIDEO_STREAMING_2020_PYG_B = 1.8257
COLLECTIVE_MANAGEMENT_2020_PYG_B = 18.2915
PYG_PER_USD_2020 = 6_771.09742519652

YOUTUBE_MUSIC_RPM = [
    ("Low $0.50 RPM", 0.50),
    ("Baseline $1.00 RPM", 1.00),
    ("High $2.00 RPM", 2.00),
]
YOUTUBE_VIDEO_RPM = [
    ("Low $1.00 RPM", 1.00),
    ("Baseline $2.00 RPM", 2.00),
    ("High $3.00 RPM", 3.00),
]
CONTENT_ID_RPM = [
    ("Low $0.25 RPM", 0.25),
    ("Baseline $0.75 RPM", 0.75),
    ("High $1.50 RPM", 1.50),
]
SPOTIFY_PER_STREAM = [
    ("Low $0.0024", 0.0024),
    ("2024 sample mean $0.0030", 0.0030),
    ("High $0.0036", 0.0036),
]
APPLE_MUSIC_PER_STREAM = [
    ("Low $0.0062", 0.0062),
    ("base $0.0080", 0.0080),
    ("High $0.0100", 0.0100),
]

MUSICBRAINZ_ARTIST_PROFILES = 266
MUSICBRAINZ_ACTIVE_ARTISTS = 10
SOUNDCHARTS_ARTIST_PROFILES = "About 2.6K"
MONTHLY_PARAGUAY_ARTIST_RELEASES = {
    "2025-07": 0,
    "2025-08": 0,
    "2025-09": 1,
    "2025-10": 2,
    "2025-11": 0,
    "2025-12": 1,
    "2026-01": 4,
    "2026-02": 1,
    "2026-03": 0,
    "2026-04": 1,
    "2026-05": 1,
    "2026-06": 1,
}
MONTHLY_PARAGUAY_RELEASE_COUNTRY = {
    "2025-07": 3,
    "2025-08": 11,
    "2025-09": 5,
    "2025-10": 10,
    "2025-11": 9,
    "2025-12": 10,
    "2026-01": 3,
    "2026-02": 5,
    "2026-03": 2,
    "2026-04": 1,
    "2026-05": 1,
    "2026-06": 0,
}
MONTHLY_GLOBAL_GUARANI_RELEASES = {
    "2025-07": 0,
    "2025-08": 0,
    "2025-09": 0,
    "2025-10": 0,
    "2025-11": 0,
    "2025-12": 0,
    "2026-01": 0,
    "2026-02": 0,
    "2026-03": 0,
    "2026-04": 0,
    "2026-05": 1,
    "2026-06": 0,
}

AI_TRENDS = {
    "Suno": {"average": 35.4, "maximum": 100, "nonzero_weeks": 30},
    "Udio": {"average": 0.1, "maximum": 5, "nonzero_weeks": 1},
    "AI Music": {"average": 5.5, "maximum": 78, "nonzero_weeks": 7},
}
AI_TRENDS_WEEK_COUNT = 53
AI_TRENDS_DATE_RANGE = "2025-06-29 to 2026-06-28"
AI_REGIONAL_INTEREST = [
    (
        "Suno",
        "Boqueron 100; Asuncion 51; Itapua 44; Cordillera 43; "
        "Paraguari 42; Alto Parana 37; San Pedro 34; Canindeyu 33; "
        "Central 31; Caaguazu 20; Presidente Hayes 3; Guaira 2",
    ),
    ("Udio", "Asuncion 100; Central 54; No data available for other regions"),
    (
        "AI Music",
        "Asuncion 100; Cordillera 81; Alto Parana 37; Central 26; "
        "No data can be displayed in other regions",
    ),
]


def pct(value: float) -> str:
    return f"{value:.1f}%"


def int_fmt(value: int) -> str:
    return f"{value:,}"


def money_usd(value: float) -> str:
    return f"${value:,.2f}"


def pyg_b_to_usd_m(value: float) -> float:
    return value * 1_000_000_000 / PYG_PER_USD_2020 / 1_000_000


def rows(headers: Iterable[str], body: Iterable[Iterable[object]]) -> str:
    headers = list(headers)
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]
    for row in body:
        lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
    return "\n".join(lines)


def app_store_rows() -> list[tuple[object, ...]]:
    total = sum(rating for _, _, rating, _ in APP_STORE_RATING_PROXY)
    return [
        (
            index,
            platform,
            app_name,
            android_rank,
            int_fmt(rating),
            pct(rating / total * 100),
        )
        for index, (platform, app_name, rating, android_rank) in enumerate(
            APP_STORE_RATING_PROXY, start=1
        )
    ]


def rpm_table(
    title: str, unit: str, benchmarks: list[tuple[str, float]]
) -> str:
    body = []
    for volume in (1_000, 10_000, 100_000, 1_000_000):
        values = [money_usd(volume / 1_000 * rpm) for _, rpm in benchmarks]
        body.append((f"{volume:,} {unit}", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def per_stream_table(
    title: str, benchmarks: list[tuple[str, float]]
) -> str:
    body = []
    for volume in (1_000, 10_000, 100_000, 1_000_000):
        values = [money_usd(volume * rate) for _, rate in benchmarks]
        body.append((f"{volume:,} streams", *values))
    return rows([title, *[name for name, _ in benchmarks]], body)


def monthly_release_rows() -> list[tuple[object, ...]]:
    return [
        (
            month,
            MONTHLY_PARAGUAY_ARTIST_RELEASES[month],
            MONTHLY_PARAGUAY_RELEASE_COUNTRY[month],
            MONTHLY_GLOBAL_GUARANI_RELEASES[month],
        )
        for month in MONTHLY_PARAGUAY_ARTIST_RELEASES
    ]


def high_low(values: dict[str, int]) -> tuple[str, str]:
    high = max(values.values())
    low = min(values.values())
    high_months = [month for month, value in values.items() if value == high]
    low_months = [month for month, value in values.items() if value == low]
    return (
        f"{' / '.join(high_months)} ({high})",
        f"{' / '.join(low_months)} ({low})",
    )


def ai_interest_rows() -> list[tuple[object, ...]]:
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
    app_rating_total = sum(
        rating for _, _, rating, _ in APP_STORE_RATING_PROXY
    )
    guarani_relevant_users = GUARANI_PRIMARY_USERS + BILINGUAL_USERS
    guarani_relevant_share = GUARANI_PRIMARY_SHARE + BILINGUAL_SHARE

    artist_total = sum(MONTHLY_PARAGUAY_ARTIST_RELEASES.values())
    country_total = sum(MONTHLY_PARAGUAY_RELEASE_COUNTRY.values())
    guarani_total = sum(MONTHLY_GLOBAL_GUARANI_RELEASES.values())
    artist_high, artist_low = high_low(MONTHLY_PARAGUAY_ARTIST_RELEASES)
    country_high, country_low = high_low(MONTHLY_PARAGUAY_RELEASE_COUNTRY)

    return f"""# Paraguayan Guaraní AI Music Market Research

Report Date: {REPORT_DATE}

## Executive Summary

Paraguay has a population of approximately **7.03 million** and **5.84 million** internet users. YouTube ads reach approximately **4.3 million people**; about **66.6%** of the population age 5+ speaks primarily Guaraní or both Guaraní and Spanish. Spotify leads both Paraguay’s Android music-app ranking and App Store rating-count proxy. Very few Guaraní release tags appear in public databases, but this is inconsistent with the large speaker population and more likely reflects gaps in metadata and digital-release coverage. The Google Trends-based AI Interest Index is **{ai_interest_index():.1f}/100**, mainly driven by Suno. The market is therefore suitable for small-scale testing focused on Guaraní or Guaraní/Spanish hybrid content, not an immediate large-scale rollout.

Final Judgment: **Market Opportunity = Moderate**
Recommendation: **Small-scale testing / continued monitoring**

## 1. Platform overview and market structure

### 1.1 Mainstream Music Platform User-Scale Proxy Ranking

{rows(
    ["Rank", "Platform", "Paraguay App Store App", "Android Free Music Rank", "App Store Rating Count", "Approx. Proxy Share"],
    app_store_rows(),
)}

Note: Platforms were screened using locally available apps in Paraguay, the [Similarweb Paraguay Music & Audio Android ranking](https://www.similarweb.com/top-apps/google/paraguay/music-audio/), and the Apple Paraguay storefront. Similarweb ranked Spotify No. 1, YouTube Music No. 7, and Apple Music No. 49 on 2026-05-03. Most apps ranked No. 2-No. 5 were offline players rather than streaming services through which creators can distribute music and earn stream-based royalties, so they were not treated as primary distribution platforms.

App Store rating data was queried through the [Apple Search / Lookup API](https://itunes.apple.com/lookup?id=324684580&country=py) on 2026-07-03. Approx. Proxy Share = platform rating count / the combined **{int_fmt(app_rating_total)}** ratings across the checked music platforms. This reflects relative usage signals from the local storefront; it is not downloads, monthly active users, or official market share. Claro Music was included because it is locally available in Paraguay, although its rating count is small.

### 1.2 Market Size

{rows(
    ["Metric", "Amount in 2020", "USD at 2020 Average Exchange Rate"],
    [
        ("Total revenue from recorded music", "₲39.1650B", f"${pyg_b_to_usd_m(RECORDED_MUSIC_2020_PYG_B):.2f}M"),
        ("Streaming revenue", "₲20.7035B", f"${pyg_b_to_usd_m(STREAMING_2020_PYG_B):.2f}M"),
        ("Paid Audio Subscription", "₲10.4098B", f"${pyg_b_to_usd_m(PAID_AUDIO_2020_PYG_B):.2f}M"),
        ("Ad-Supported Audio", "₲8.4680B", f"${pyg_b_to_usd_m(AD_AUDIO_2020_PYG_B):.2f}M"),
        ("Video Streaming", "₲1.8257B", f"${pyg_b_to_usd_m(VIDEO_STREAMING_2020_PYG_B):.2f}M"),
        ("Collective management revenue", "₲18.2915B", f"${pyg_b_to_usd_m(COLLECTIVE_MANAGEMENT_2020_PYG_B):.2f}M"),
    ],
)}

This is the latest freely accessible national market value found for Paraguay, from the [IFPI Latin America Paraguay 2020 report](https://ifpilatina.org/content/uploads/Informe_Nacional_2020_PARAGUAY_f505931b81.pdf); it is not a 2026 market estimate. USD conversions use the World Bank's 2020 official average exchange rate of **₲{PYG_PER_USD_2020:,.1f} / US$**. Streaming accounted for approximately **{STREAMING_2020_PYG_B / RECORDED_MUSIC_2020_PYG_B * 100:.1f}%** of recorded-music revenue in 2020, showing that the market was already substantially digitized.

## 2. Market demand

### 2.1 Population, Internet, and Language Profile

{rows(
    ["Metrics", "Data"],
    [
        ("Total population", int_fmt(POPULATION)),
        ("Internet users", int_fmt(INTERNET_USERS)),
        ("Internet penetration rate", pct(INTERNET_PENETRATION)),
        ("Population mainly speaking Guaraní (5 years and older)", f"{int_fmt(GUARANI_PRIMARY_USERS)} / {pct(GUARANI_PRIMARY_SHARE)}"),
        ("Guaraní- and Spanish-bilingual population (5+)", f"{int_fmt(BILINGUAL_USERS)} / {pct(BILINGUAL_SHARE)}"),
        ("Guaraní-relevant language audience", f"{int_fmt(guarani_relevant_users)} / {pct(guarani_relevant_share)}"),
    ],
)}

Population and Internet data are from [DataReportal Digital 2026 Paraguay](https://datareportal.com/reports/digital-2026-paraguay), corresponding to the end of 2025. Linguistic data comes from Paraguay INE's EPHC 2025 annual survey, published by [Paraguay TV government media](https://www.paraguaytv.gov.py/2026/02/20/paraguay-resguarda-su-riqueza-linguistica-387-de-hogares-son-bilingues-guarani-castellano/); survey excludes Boqueron, Alto Paraguay, Indigenous communities and collective settlements, and is therefore not a complete national language census.

### 2.2 Music Platform User-Scale Proxies

{rows(
    ["Metric", "Reach / Ranking", "Meaning"],
    [
        ("YouTube ad reach", int_fmt(YOUTUBE_AD_REACH), "YouTube ecosystem potential ad reach, not YouTube Music MAU"),
        ("YouTube reach as a share of total population", pct(YOUTUBE_AD_REACH_POP_PCT), "Digital music video-discovery coverage"),
        ("YouTube reach as a share of internet users", pct(YOUTUBE_AD_REACH_INTERNET_PCT), "Online audience reach"),
        ("Spotify Android music rank", "No. 1", "Ranking signal of local music-app demand"),
        ("Spotify App Store rating-count proxy", "216,276 / 92.2%", "Clear leader among the checked music platforms"),
    ],
)}

No published monthly active user figures for Paraguay were found for Spotify, YouTube Music, Apple Music, or other platforms. YouTube ad reach, local Android rankings, and App Store ratings are therefore used as popularity proxies; they should not be interpreted as actual platform user counts.

### 2.3 Demand Conclusion

Demand Rating: **Medium-High**. Paraguay has **5.84 million** internet users, a YouTube ad reach of **4.3 million**, and approximately **3.79 million** people who primarily speak Guaraní or are bilingual in Guaraní and Spanish. This audience is large enough to support smaller-language music testing, but no public data was found on the actual number of paid music subscribers.

## 3. Platform monetization

### 3.1 YouTube / YouTube Music

YouTube does not publish a fixed RPM for Paraguayan music content. The following are budget ranges and are not official or guaranteed revenue for Paraguay; actual amounts depend on country of audience, advertising, subscriptions, rights attribution and publisher share. [YouTube for Artists](https://artists.youtube.com/intl/es/) confirms music revenue and distribution paths, and [Duetti 2024 Music Economics Report](https://report.duetti.co/) shows that the average YouTube independent artist sample is approximately **$4.80** per thousand streams, but different revenue sources vary widely.

#### YouTube Music / Art Track Play

{rpm_table("YouTube Music / Art Track", "Streams", YOUTUBE_MUSIC_RPM)}

#### Own YouTube channel videos

{rpm_table("Own channel video", "Views", YOUTUBE_VIDEO_RPM)}

#### Content ID / UGC claimed for viewing

{rpm_table("Content ID / UGC", "Views", CONTENT_ID_RPM)}

### 3.2 Spotify

{per_stream_table("Spotify streams", SPOTIFY_PER_STREAM)}

Note: A sample of independent artists from [Duetti 2024](https://report.duetti.co/) shows that Spotify averages about **$3.00 / 1,000 streams**. The low and high levels are used for budget sensitivity analysis; Spotify does not announce a fixed per-stream rate for Paraguay, and the final amount received will also be affected by the distribution of publishers, record companies, and songwriting rights.

### 3.3 Apple Music

{per_stream_table("Apple Music stream volume", APPLE_MUSIC_PER_STREAM)}

Note: The [Duetti 2024](https://report.duetti.co/) sample is about **$6.20 / 1,000 streams**. [Apple Music for Artists](https://artists.apple.com/support/1124-apple-music-insights-royalty-rate) reported a 2020 global average of about **$0.01 / stream** for individual paid plans and states that rates vary by country and subscription plan. These are not fixed Paraguay rates.

### 3.4 iTunes

{rows(
    ["iTunes Paraguay", "Actual price"],
    [
        ("single price sample", "$0.69-$0.99"),
        ("Album Price Sample", "$6.99-$8.99"),
        ("The artist's actual share", "depends on the publisher, record company and copyright contract"),
    ],
)}

The price was obtained through [Apple Search API Paraguay storefront](https://itunes.apple.com/search?term=Taylor%20Swift&country=py&media=music&entity=song&limit=20) on 2026-07-03. It is a store sample rather than a unified selling price for all works.

### 3.5 Other locally available platforms

SoundCloud, Deezer, Audiomack, Amazon Music, and Claro Music are available in Paraguay and show usage signals in the local storefront. No public Paraguay per-stream payout was found for these platforms, so this report does not provide local revenue estimates for them. They can supplement distribution but do not replace Spotify and YouTube as the primary test channels.

### 3.6 Monetization Conclusion

Monetization Rating: **Medium / Based on public benchmarks**. Spotify has the strongest local scale signal, Apple Music has the higher public per-stream benchmark, and YouTube offers discovery, channel advertising, and Content ID paths. Fixed Paraguay rates are not public, so these estimates are for budgeting only and are not guaranteed payouts.

## 4. Level of competition

{rows(
    ["Metrics", "Data"],
    [
        ("MusicBrainz artist country:PY artist profile", int_fmt(MUSICBRAINZ_ARTIST_PROFILES)),
        ("Paraguayan artist profiles with visible releases in the past 12 months", int_fmt(MUSICBRAINZ_ACTIVE_ARTISTS)),
        ("Soundcharts all-time artist-country Paraguay profiles", SOUNDCHARTS_ARTIST_PROFILES),
    ],
)}

Methodology: 2026-07-03 Query `artist country:PY` through [MusicBrainz Search API](https://musicbrainz.org/doc/MusicBrainz_API/Search), then use the artist MBID to search for releases from 2025-07-01 to 2026-06-30 and remove duplicates. `country:PY` indicates the country association of artist profiles; MusicBrainz relies on community input and cannot be regarded as the total number of Paraguayan creators.

Soundcharts showed approximately **2.6K** artist profiles under `Artist country = Paraguay` on 2026-07-03. This all-time country-profile count is not language-specific and does not represent artists active in the past 12 months.

Competition conclusion: **Recently visible competition is low, but an all-time creator base is established**. MusicBrainz has **10** Paraguayan artist profiles with visible releases during the study period; Soundcharts has approximately **2.6K** Paraguay-associated artist profiles across all time. Their time ranges and coverage differ, so the values cannot be directly compared or divided.

## 5. Content supply

{rows(
    ["Month", "Releases by Paraguay-Associated Artists", "Releases with Paraguay Territory", "Global Guaraní-Tagged Releases"],
    monthly_release_rows(),
)}

{rows(
    ["Metrics", "Data"],
    [
        ("Total release count associated with Paraguayan artist profiles", artist_total),
        ("Average monthly Paraguay-associated artist releases", f"{artist_total / 12:.1f}"),
        ("Highest month for artist-associated releases", artist_high),
        ("Lowest month for artist-associated releases", artist_low),
        ("Total releases with Paraguay territory", country_total),
        ("Average monthly releases with Paraguay territory", f"{country_total / 12:.1f}"),
        ("Highest month for Paraguay-territory releases", country_high),
        ("Lowest month for Paraguay-territory releases", country_low),
        ("Total global Guaraní-tagged releases", guarani_total),
    ],
)}

The three methodologies are not interchangeable: the first column tracks artists with Paraguayan country profiles; the second counts releases that list Paraguay as a release territory in MusicBrainz and may include international artists; the third counts only global releases with `lang:grn` metadata. Although Guaraní is widely spoken, only **1** release carries this language tag in the dataset. This indicates severe metadata undercoverage and does not mean that only one Guaraní work exists in the real market.

No reviewable Soundcharts song-volume or Guaraní-lyrics filter result was available for Paraguay, so the supply table retains only MusicBrainz data and adds no estimated values.

Supply conclusion: **Visible supply is low, creating an opportunity signal but not proving that the market is empty**. There were only **12** releases linked to Paraguayan artist profiles and **60** Paraguay-territory release records during the study period. Guaraní digital works may be missing from the database, lack language tags, or appear in Spanish/Jopara hybrid form.

## 6. AI music acceptance

### 6.1 AI Search Interest

{rows(
    ["Keywords", "Average index", "Peak index", "Weeks with data"],
    ai_interest_rows(),
)}

AI Interest Index = **{ai_interest_index():.1f} / 100**

Scope: Google Trends Paraguay in the past 12 months, a total of **{AI_TRENDS_WEEK_COUNT} weeks**, the time series is **{AI_TRENDS_DATE_RANGE}**. The data comes from `multiTimeline (3).csv` exported by the user; the AI ​​Interest Index is the arithmetic mean of the average trend index of the three keywords Suno, Udio and AI Music. The trend index is the relative search popularity, not the number of searches.

#### Regional distribution

{rows(["Keywords", "Regional Trend Index"], AI_REGIONAL_INTEREST)}

Region data comes from `geoMap (14).csv`, `geoMap (15).csv` and `geoMap (16).csv`. Each keyword is ranked with its most popular area as 100. The absolute search volume cannot be compared between different keywords; a blank means that Google Trends does not have enough data, which does not mean that there is absolutely no search.

[Similarweb Paraguay Android Music Chart](https://www.similarweb.com/top-apps/google/paraguay/music-audio/) also shows Suno ranked 20th, which is consistent with the results in Google Trends where Suno is clearly ahead.

AI adoption conclusion: **Low to Medium-Low; initial tool interest is visible**. Suno's average index is **35.4**, with measurable searches in **30 / 53** weeks; AI Music averages only **5.5**, and Udio shows almost no sustained interest. These results indicate local interest in AI music tools, but do not prove that listeners will keep listening to AI-generated songs.

## 7. Final evaluation

1. Is the Guaraní market size in Paraguay suitable for testing AI music in smaller languages?
   **Suitable.** Paraguay has a population of **7.03 million** and **5.84 million** internet users. About **3.79 million** people in the surveyed population primarily speak Guaraní or are bilingual in Guaraní and Spanish, fitting the objectives of a smaller-language market test.

2. Which platform has the highest coverage value?
   **Spotify has the strongest music-app signal, while YouTube has the largest verifiable audience reach.** Spotify ranks No. 1 on the Android music chart and has an approximate **92.2%** App Store rating-count proxy share; YouTube ads reach approximately **4.3 million people**.

3. Which platform has the strongest monetization ability?
   **Apple Music has the higher public per-stream benchmark; Spotify is more important for local scale and testing.** YouTube also offers channel advertising and Content ID revenue, but no platform publishes a fixed Paraguay rate.

4. Is competition fierce for local music in Paraguay?
   **Recently visible competition is low, but there is already a certain base of local creators.**MusicBrainz has **10** Paraguayan artist profiles with visible releases in the past 12 months; Soundcharts has approximately **2.6K** Paraguayan artist profiles for the entire period, and the two methodologies cannot be directly compared.

5. Is the supply of Guaraní content saturated?
   **There is no evidence of saturation.** Visible release counts are very low, while the Guaraní-speaking population is far larger than the number of Guaraní tags in the database. This is an opportunity signal, but demand still needs to be validated through real campaign results.

6. Has the local market started paying attention to AI music?
   **There is initial interest, but overall interest remains low.** The AI Interest Index is **{ai_interest_index():.1f}/100**; Suno’s average index is **35.4**, well above AI Music at **5.5** and Udio at **0.1**.

7. Is it worth continuing to invest in AI music?
   **Worth testing at small scale.** Prioritize Guaraní and Guaraní/Spanish hybrid versions, using Spotify and YouTube as the primary observation channels. Current evidence is insufficient to support immediate budget expansion.

## Comprehensive rating

{rows(
    ["Dimension", "Rating"],
    [
        ("Market Demand", "Medium-High"),
        ("Monetization", "Moderate / Based on public benchmarks"),
        ("Competition level", "Low/Insufficient Data Coverage"),
        ("Content supply opportunity", "High / Requires real campaign validation"),
        ("AI Search Interest", "Low to Medium-Low / Mainly driven by Suno"),
        ("Platform fit", "Medium-High"),
    ],
)}

Final Market Opportunity: **Medium**

Recommendation: **Small-scale testing / continued monitoring**
"""


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
