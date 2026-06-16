# Lyrics / Title Content Analysis Plan

## 1. Research Question

How do song titles and lyric content relate to engagement performance for released / online-generated songs in non-mainstream language markets?

This analysis explores whether title style, title keywords, lyric themes, and emotional tone may help explain why some non-mainstream language songs perform better than others.

---

## 2. Data Sources

- **YouTube:** views, likes, comments
- **DistroKid:** streaming / platform performance data if available
- **iTunes:** title, genre, release date
- **Spotify:** complementary metadata
- **Released / Online-Generated Suno Songs:** needed for the final lyrics/title analysis

Current YouTube/iTunes/Spotify data can help test the framework, but the final analysis should use actual released / online-generated Suno songs with available titles, lyrics, and engagement metrics.

---

## 3. Methodology

Build a content tagging framework to turn title and lyric features into structured variables.

If full lyrics are not available at first, the demo can start with title/content positioning and later expand to lyric-level analysis once lyrics are collected.

**Framework:**

Title / lyric content variables → engagement metrics

The analysis can start with one target market, such as Turkish, to reduce cross-market noise and improve interpretability.

As a small framework test, I created two Turkish Suno demo songs with lyrics. These songs are not released, so they are only used to test content tagging, not engagement analysis.

**Mini Observation:** The demo shows that the framework can distinguish different title styles under the same language, genre, and theme. “Uzakta Ev Hasreti” is more direct, while “Evinin Sesi” is more metaphorical.

---

## 4. Content Tagging Framework

| Variable | Description | Example |
|---|---|---|
| Title Keywords | Keywords in title | love, night, goodbye |
| Title Style | Title format | emotional, descriptive, story-based |
| Lyric / Content Theme | Main theme / content angle | love, heartbreak, hope |
| Emotional Tone | Overall mood | sad, romantic, energetic |
| Hook Strength | Content memorability, scored manually | 1-5 score |
| Localization | Local language/culture | localized / non-localized |

---

## 5. Potential Analysis

Compare engagement performance across:

- title styles
- lyric / content themes
- localized vs. non-localized titles
- high-performing vs. average-performing songs

Possible metrics:

- views / streams
- like rate = likes / views
- comment rate = comments / views
- engagement rate = (likes + comments) / views

---

## 6. A/B Test Ideas

Control for language, genre, and release timing; change one content variable at a time:

- **Title Style:** emotional vs. descriptive
- **Lyric Theme:** heartbreak vs. hopeful
- **Localization:** localized vs. English-style title

---

## 7. Data Risks & Next Steps

**Main risks:** incomplete lyrics, missing released Suno song-level data, limited DistroKid data access, inconsistent genre labels, sparse comments, release timing effects, and uncertain Suno API / keyword search access. Unofficial API options exist but need further validation.

**Next steps:** confirm available data fields → select one target market → refine tagging / text extraction framework → select sample songs → tag or classify content variables → calculate engagement metrics → identify preliminary patterns.

---

## 8. Text Information Extraction / NLP Extension

This analysis can be extended from manual tagging to NLP-based text information extraction.

For actual released / online-generated songs, titles and lyrics can be classified into broader content categories, such as romance, hometown/nostalgia, and local food/culture. These categories can then be compared with engagement metrics.

Turkish can be used as the first market-level case study. The current Turkish demo songs only test the hometown/nostalgia category and are used to validate the tagging framework; the actual analysis should focus on released / online-generated songs with observable engagement data.