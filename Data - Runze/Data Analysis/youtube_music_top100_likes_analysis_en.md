# YouTube Music Videos Top 100 by Likes: Analysis Report

Data source: `youtube_music_top100_likes.md`  
Analysis date: 2026-06-04  
Sample scope: Top 100 YouTube music-video candidates ranked by public like count. This is not an official YouTube historical chart.

## 1. Executive Summary

This ranking should not be read only as "which videos have the most likes." A more useful interpretation is that it reveals two different success models:

1. **Mass-reach global hits**: videos with extremely high view counts, where likes accumulate through long-term global consumption. Examples include `Despacito`, `See You Again`, `Shape of You`, and `Uptown Funk`.
2. **Fan-engagement hits**: videos whose view counts are not always the highest, but whose like rates and comment rates are far above average. BTS / HYBE LABELS videos are the clearest examples.

Across the Top 100, high-like performance is mainly driven by three forces:

- Long-term view accumulation from global pop hits
- High engagement efficiency from K-pop and fan-driven communities
- Cross-context amplification from film, sports, and social events

## 2. Data Quality Notes

The source file is a Markdown table with the following fields:

| Field | Meaning |
| --- | --- |
| Rank | Ranking by like count |
| Title | Video title |
| Channel | Publishing channel |
| Published | Publication date |
| Views | View count |
| Likes | Like count |
| Comments | Comment count |
| Duration | Video duration |
| Thumbnail | Thumbnail URL |
| YouTube Link | Video URL |

Important caveats:

- Some titles may appear garbled in certain terminal environments, but names such as BTS, Agust D, and ROSÉ can be restored when the file is read as UTF-8.
- `Channel` is not always the same as artist. For example, `HYBE LABELS` includes BTS, Agust D, and other projects.
- The ranking mixes official music videos, lyric videos, soundtrack videos, and videos tied to films or sports events. A stricter market analysis should add a `video_type` field.
- This dataset is a point-in-time snapshot. YouTube metrics continue to change.

## 3. Core Overview

| Metric | Value |
| --- | ---: |
| Number of videos | 100 |
| Total views | 253,903,002,490 |
| Total likes | 1,767,218,870 |
| Total comments | 124,596,873 |
| Top 1 likes | 56,284,016 |
| Top 100 likes | 11,759,162 |
| Top 10 share of likes | 19.11% |
| Top 10 share of views | 16.81% |
| Overall like rate | 0.696% |
| Median like rate | 0.670% |
| Median comment rate | 0.022% |

The Top 100 shows a clear head effect, but it is not dominated only by the first few videos. The Top 10 account for about 19.11% of total likes, meaning the top is strong while the middle of the ranking still carries substantial weight.

## 4. Top-Ranking Observations

| Rank | Video | Channel | Year | Views | Likes | Comments |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | Luis Fonsi - Despacito ft. Daddy Yankee | LuisFonsiVEVO | 2017 | 9,031,571,429 | 56,284,016 | 4,370,666 |
| 2 | Wiz Khalifa - See You Again ft. Charlie Puth | Wiz Khalifa Music | 2015 | 7,001,805,010 | 46,577,759 | 2,353,792 |
| 3 | BTS - Dynamite | HYBE LABELS | 2020 | 2,090,902,501 | 39,279,524 | 15,924,662 |
| 4 | Ed Sheeran - Shape of You | Ed Sheeran | 2017 | 6,733,123,742 | 35,594,333 | 1,230,735 |
| 5 | BTS - Boy With Luv feat. Halsey | HYBE LABELS | 2019 | 1,934,990,482 | 29,559,337 | 6,459,355 |

The top entries already show the split between the two models:

- `Despacito`, `See You Again`, and `Shape of You` are super-high-view global hits.
- `Dynamite` and `Boy With Luv` have lower view counts than those mass-reach hits, but their comment counts and engagement efficiency are much higher.

## 5. Top 10 by Views: Mass-Reach Power

| Rank | Video | Channel | Views | Like Rate |
| ---: | --- | --- | ---: | ---: |
| 1 | Despacito | LuisFonsiVEVO | 9,031,571,429 | 0.62% |
| 2 | See You Again | Wiz Khalifa Music | 7,001,805,010 | 0.67% |
| 3 | Shape of You | Ed Sheeran | 6,733,123,742 | 0.53% |
| 4 | Uptown Funk | MarkRonsonVEVO | 5,823,859,445 | 0.40% |
| 5 | Waka Waka | shakiraVEVO | 4,545,443,114 | 0.56% |
| 6 | Counting Stars | OneRepublicVEVO | 4,428,559,057 | 0.43% |
| 7 | Sugar | Maroon5VEVO | 4,384,053,627 | 0.39% |
| 8 | Roar | KatyPerryVEVO | 4,318,426,141 | 0.42% |
| 9 | Dark Horse | KatyPerryVEVO | 4,177,992,991 | 0.45% |
| 10 | Perfect | Ed Sheeran | 4,164,325,075 | 0.57% |

These videos are defined by enormous view counts, while their like rates are mostly below or near the overall median. They represent broad mass consumption rather than highly concentrated fan mobilization.

## 6. Top 10 by Like Rate: Fan Engagement Strength

Like rate = Likes / Views. This metric measures how efficiently views convert into likes.

| Rank | Video | Channel | Year | Like Rate | Views | Likes |
| ---: | --- | --- | ---: | ---: | ---: | ---: |
| 1 | BTS - ON | HYBE LABELS | 2020 | 3.68% | 350,528,384 | 12,886,376 |
| 2 | Agust D - Daechwita | HYBE LABELS | 2020 | 3.13% | 488,425,115 | 15,296,708 |
| 3 | BTS - Life Goes On | HYBE LABELS | 2020 | 3.11% | 596,201,846 | 18,551,690 |
| 4 | Lil Dicky - Earth | Lil Dicky | 2019 | 2.60% | 469,781,729 | 12,231,473 |
| 5 | BTS - Permission to Dance | HYBE LABELS | 2021 | 2.50% | 717,704,805 | 17,925,432 |
| 6 | BTS - Black Swan | HYBE LABELS | 2020 | 2.30% | 598,302,805 | 13,749,718 |
| 7 | BTS - Butter | HYBE LABELS | 2021 | 2.20% | 1,089,729,341 | 24,001,436 |
| 8 | BTS - Dynamite | HYBE LABELS | 2020 | 1.88% | 2,090,902,501 | 39,279,524 |
| 9 | BTS - FAKE LOVE | HYBE LABELS | 2018 | 1.61% | 1,387,177,483 | 22,358,266 |
| 10 | Ariana Grande - thank u, next | ArianaGrandeVevo | 2018 | 1.59% | 881,112,641 | 14,053,477 |

The conclusion is clear: the like-rate ranking is heavily dominated by HYBE / BTS-related content. These videos are not simply accumulating likes through massive view counts; each view is much more likely to convert into a like.

This usually reflects several mechanisms:

- Active fan support and repeated engagement
- Concentrated attention around music-video premieres
- Community-driven ranking, sharing, and commenting behavior
- Stronger identity attachment between artist and audience

## 7. Top 10 by Comment Rate: Community Discussion Strength

Comment rate = Comments / Views. Compared with like rate, comment rate better reflects community activity and emotional participation.

| Rank | Video | Channel | Comment Rate | Comments |
| ---: | --- | --- | ---: | ---: |
| 1 | BTS - Life Goes On | HYBE LABELS | 0.85% | 5,069,217 |
| 2 | BTS - Butter | HYBE LABELS | 0.82% | 8,962,236 |
| 3 | BTS - ON | HYBE LABELS | 0.77% | 2,687,912 |
| 4 | BTS - Dynamite | HYBE LABELS | 0.76% | 15,924,662 |
| 5 | BTS - Permission to Dance | HYBE LABELS | 0.47% | 3,372,630 |
| 6 | BTS - DNA | HYBE LABELS | 0.37% | 6,209,395 |
| 7 | BTS - Boy With Luv | HYBE LABELS | 0.33% | 6,459,355 |
| 8 | BTS - FAKE LOVE | HYBE LABELS | 0.32% | 4,445,821 |
| 9 | Agust D - Daechwita | HYBE LABELS | 0.28% | 1,378,138 |
| 10 | BTS - Blood Sweat & Tears | HYBE LABELS | 0.24% | 2,446,697 |

The entire comment-rate Top 10 is occupied by HYBE LABELS videos. This shows that K-pop's YouTube advantage is not limited to likes; it reflects a fuller pattern of community interaction.

## 8. Top 10 by Likes per Year: New-Release Growth Speed

Likes per year = Likes / years since publication. This metric reduces the advantage older videos have from longer accumulation time.

| Rank | Video | Channel | Year | Likes per Year |
| ---: | --- | --- | ---: | ---: |
| 1 | ROSÉ & Bruno Mars - APT. | ROSÉ | 2024 | 11,142,195 |
| 2 | Lady Gaga, Bruno Mars - Die With A Smile | LadyGagaVEVO | 2024 | 7,695,892 |
| 3 | BTS - Dynamite | HYBE LABELS | 2020 | 6,789,799 |
| 4 | Despacito | LuisFonsiVEVO | 2017 | 5,995,257 |
| 5 | BTS - Butter | HYBE LABELS | 2021 | 4,764,415 |
| 6 | See You Again | Wiz Khalifa Music | 2015 | 4,173,829 |
| 7 | BTS - Boy With Luv | HYBE LABELS | 2019 | 4,136,608 |
| 8 | Shape of You | Ed Sheeran | 2017 | 3,810,325 |
| 9 | BTS - Permission to Dance | HYBE LABELS | 2021 | 3,655,647 |
| 10 | Billie Eilish, Khalid - lovely | BillieEilishVEVO | 2018 | 3,593,057 |

This perspective is especially useful: `APT.` and `Die With A Smile` are not yet among the very top videos by total likes, but their annualized like growth is extremely strong. Recent songs can still enter historical like rankings, but they need more time to accumulate.

## 9. Year Distribution

| Publication Year | Number of Videos |
| ---: | ---: |
| 2007 | 1 |
| 2009 | 6 |
| 2010 | 5 |
| 2011 | 6 |
| 2012 | 3 |
| 2013 | 4 |
| 2014 | 5 |
| 2015 | 11 |
| 2016 | 12 |
| 2017 | 16 |
| 2018 | 13 |
| 2019 | 7 |
| 2020 | 6 |
| 2021 | 3 |
| 2024 | 2 |

The core period is 2015-2018, which together contributes 52 videos, more than half of the Top 100. This roughly corresponds to the strongest window for global YouTube music-video distribution, when streaming and social sharing were both mature enough to amplify music videos worldwide.

The decline in post-2020 entries does not necessarily mean newer songs are weaker. It may reflect several factors:

- Newer videos have had less time to accumulate views and likes.
- Music consumption has become more fragmented across TikTok, Spotify, Shorts, and other platforms.
- Long-form YouTube music videos may be less central than they were during the 2010s.
- Fan-driven videos can still generate high engagement, but mass-reach mega music videos are harder to produce.

## 10. Channel Concentration

| Channel | Videos | Total Likes | Total Views | Aggregate Like Rate | Total Comments |
| --- | ---: | ---: | ---: | ---: | ---: |
| HYBE LABELS | 13 | 275,998,751 | 14,916,610,006 | 1.85% | 64,439,328 |
| EminemVEVO | 5 | 77,109,154 | 10,700,366,111 | 0.72% | 3,745,359 |
| Ed Sheeran | 3 | 75,243,036 | 14,906,627,731 | 0.50% | 2,215,847 |
| BillieEilishVEVO | 3 | 62,246,456 | 4,802,214,832 | 1.30% | 1,927,661 |
| JustinBieberVEVO | 3 | 58,409,593 | 8,598,648,938 | 0.68% | 6,450,787 |
| LuisFonsiVEVO | 1 | 56,284,016 | 9,031,571,429 | 0.62% | 4,370,666 |
| Wiz Khalifa Music | 1 | 46,577,759 | 7,001,805,010 | 0.67% | 2,353,792 |
| ShawnMendesVEVO | 3 | 46,205,324 | 6,415,406,802 | 0.72% | 1,392,094 |
| ArianaGrandeVevo | 3 | 43,890,529 | 4,903,813,443 | 0.90% | 2,049,779 |
| Maroon5VEVO | 2 | 39,837,856 | 8,406,474,074 | 0.47% | 1,127,767 |

HYBE LABELS is the most prominent channel in this dataset:

- Most chart entries: 13 videos
- Highest total likes: about 276.0 million
- Highest total comments: about 64.4 million
- Aggregate like rate far above most traditional Western pop channels

However, Ed Sheeran's total views are almost as high as HYBE LABELS, which highlights the difference between their strengths:

- HYBE: high engagement, high comments, strong fan mobilization
- Ed Sheeran: high views, broad mass reach, long-cycle consumption

## 11. Market Insights

### 11.1 Like Count Is Not a Single-Dimension Popularity Metric

`Despacito` ranks first by likes and also first by views, but not every high-like video is driven by ultra-high views. Several BTS videos enter the upper ranks through much higher like rates despite lower view counts than traditional global hits.

Like count is therefore a combination of:

- Global reach and exposure
- Audience willingness to actively express support

### 11.2 K-pop's Advantage Is Engagement Efficiency

HYBE / BTS-related content clearly leads in like rate and comment rate. This suggests that K-pop's YouTube strength is not only song distribution, but a full fan-participation system.

In this model, a music video becomes an event, not just a piece of content.

### 11.3 2015-2018 Was a Golden Window for YouTube Music Videos

The years 2015, 2016, 2017, and 2018 contribute 52 videos in total. These songs have had enough time to accumulate metrics and were released during a peak period for global music-video circulation on YouTube.

### 11.4 Latin Music Has Strong Global Distribution Advantages

`Despacito`, `Mi Gente`, `Bailando`, `Taki Taki`, and `Havana` all show Latin music's strong global reach on YouTube. The advantages usually come from:

- Danceable rhythm and strong movement appeal
- High acceptance across multilingual markets
- Visual and dance-friendly music-video formats
- A large Spanish-speaking audience with strong cross-regional spread

### 11.5 Film, Sports, and Event Tie-Ins Amplify Reach

`See You Again`, `Sunflower`, `Heathens`, and `Waka Waka` are tied to films, the World Cup, or other strong cultural contexts. These songs benefit from:

- Emotional entry points beyond music itself
- Easier cross-audience circulation
- Longer life cycles through anniversaries, film rewatching, and event memory

## 12. Conclusion

The Top 100 ranking shows that historical success on YouTube music videos does not follow one single model.

One model is the global mass-reach hit, represented by `Despacito`, `See You Again`, and `Shape of You`. These videos build their advantage through huge view counts and long-term accumulation.

The other model is the high-engagement fan hit, represented by BTS / HYBE. These videos do not always dominate by view count, but they stand out strongly in like rate, comment rate, and community participation.

Therefore, the most important market conclusion from this dataset is: **music-video popularity on YouTube has evolved from a pure view-count race into a dual competition of global reach and fan engagement efficiency.**
