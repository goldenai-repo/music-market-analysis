# Workflows

Step-by-step guides for common end-to-end scenarios on `branch-runze`.  
See [tools.md](tools.md) for full flag reference for each script.

---

## 1. Five-Country YouTube A/B Test Data Collection

Collect 2025 YouTube music video data across five European countries (Finland, Norway,
Czechia, Hungary, Greece) to compare AI music performance by market.

```bash
# Requires YOUTUBE_API_KEY in environment or .env
export YOUTUBE_API_KEY=your_key_here

python A_B_Test/youtube_five_country_2025_collector.py
# → A_B_Test/youtube_five_country_2025_data.md    (Markdown summary)
# → A_B_Test/youtube_five_country_2025_raw.json   (raw search results)
# → A_B_Test/youtube_five_country_2025_candidates.json
# → A_B_Test/youtube_five_country_2025_details.json
```

Review `A_B_Test/Five_Country_Test_Plan.md` first for the experiment design:
20 AI-generated songs per country, targeting revenue optimization across 5 markets.

---

## 2. Country-Level AI Music Market Research

Generate or refresh a structured market report for a specific country. Currently
scripted for Finland and Norway; other countries have pre-generated reports.

```bash
# Finland
python "Market Research/Finland/finland_ai_music_market_research.py"
# → Market Research/Finland/Finland_AI_Music_Market_Report.md

# Norway
python "Market Research/Norway/norway_ai_music_market_research.py"
# → Market Research/Norway/Norway_Norwegian_AI_Music_Market_Report.md

# Force-refresh underlying data sources
python "Market Research/Finland/finland_ai_music_market_research.py" \
  --refresh-itunes \
  --refresh-musicbrainz
```

Pre-generated reports (no script needed):
- `Market Research/Czechia/Czechia_Czech_Language_AI_Music_Market_Report.md`
- `Market Research/Greece/Greece_Greek_Language_AI_Music_Market_Report.md`
- `Market Research/Hungary/Hungary_Hungarian_Language_AI_Music_Market_Report.md`
- `Market Research/Thailand/Thailand_Thai_Language_AI_Music_Market_Report.md`

---

## 3. Investment Matrix & Chart Generation

Produce visual comparisons of the seven-country AI music investment matrix.

```bash
# Step 1: review/edit the matrix data
open "Market Research/Seven_Country_AI_Music_Matrix.md"

# Step 2: generate charts (Pillow only, no matplotlib needed)
python "Market Research/generate_matrix_charts.py"
# → Market Research/Charts/comprehensive_score_bar.png
# → Market Research/Charts/ai_interest_market_value_bubble.png
```

The matrix covers: Czechia, Finland, Greece, Hungary, Norway, Thailand, Vietnam —
with population, YouTube ad reach, music revenue, and AI interest index.

---

## 4. iTunes US Top 100 Collection & Analysis

Fetch the current iTunes US Top 100 and review the analysis output.

```bash
# Step 1: fetch (no API key needed)
python "Data - Runze/raw data/itunes_us_top100_md.py"
# → Data - Runze/raw data/itunes_us_top100.md

# Step 2: review the pre-generated analysis
open "Data - Runze/Data Analysis/itunes_us_top100_analysis.md"
```

---

## 5. YouTube Top 100 by Likes Collection & Analysis

Fetch the top 100 most-liked YouTube music videos globally.

```bash
# Requires YOUTUBE_API_KEY
python "Data - Runze/raw data/youtube_music_top100_likes.py"
# → Data - Runze/raw data/youtube_music_top100_likes.md
# → Data - Runze/raw data/youtube_raw_candidates.json
# → Data - Runze/raw data/youtube_video_details.json

# Review pre-generated analysis
open "Data - Runze/Data Analysis/youtube_music_top100_likes_analysis_en.md"
```

---

## 6. Full Research Run (All Countries)

Run the complete research pipeline: collect data, generate country reports, then
produce investment matrix charts.

```bash
# 1. Collect YouTube benchmark data
python "Data - Runze/raw data/youtube_music_top100_likes.py"
python "Data - Runze/raw data/itunes_us_top100_md.py"

# 2. Collect five-country A/B test data
python A_B_Test/youtube_five_country_2025_collector.py

# 3. Generate/refresh country reports
python "Market Research/Finland/finland_ai_music_market_research.py" --refresh-itunes --refresh-musicbrainz
python "Market Research/Norway/norway_ai_music_market_research.py" --refresh-itunes --refresh-musicbrainz

# 4. Update Seven_Country_AI_Music_Matrix.md with any new findings, then
python "Market Research/generate_matrix_charts.py"
```

---

## 7. Adding a New Country

To add a new country to the market research pipeline:

1. Create a directory: `Market Research/<CountryName>/`
2. Copy an existing script (e.g. `finland_ai_music_market_research.py`) as a template
3. Update `OUTPUT_FILE`, country-specific queries, iTunes store ID, and MusicBrainz area
4. Run the script to generate the report
5. Add the country's metrics to `Market Research/Seven_Country_AI_Music_Matrix.md`
6. Re-run `generate_matrix_charts.py` to update the charts
