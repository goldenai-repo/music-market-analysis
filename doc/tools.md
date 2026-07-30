# Tools Reference

This branch (`branch-runze`) focuses on multi-country AI music market research,
YouTube data collection, and geo A/B test design. All scripts run from the **repo root**
unless otherwise noted.

## Setup

Scripts use only Python standard-library modules plus `Pillow` for chart generation.
No `requirements.txt` exists on this branch; install as needed:

```bash
pip install Pillow
```

API keys go in a `.env` file or as environment variables (never commit them):

```
YOUTUBE_API_KEY=your_key_here
```

---

## Data Collection

### `Data - Runze/raw data/itunes_us_top100_md.py`
Fetches the iTunes US Top 100 most-played songs via Apple's RSS marketing API and
writes results as a Markdown table. No API key required.

```bash
python "Data - Runze/raw data/itunes_us_top100_md.py"
```

Output: `Data - Runze/raw data/itunes_us_top100.md`

---

### `Data - Runze/raw data/youtube_music_top100_likes.py`
Fetches the top 100 YouTube music videos by likes using broad search queries across
genres and major artists. Requires `YOUTUBE_API_KEY`.

```bash
python "Data - Runze/raw data/youtube_music_top100_likes.py"
```

Outputs:
- `Data - Runze/raw data/youtube_music_top100_likes.md` — ranked Markdown table
- `Data - Runze/raw data/youtube_raw_candidates.json` — raw search results
- `Data - Runze/raw data/youtube_video_details.json` — detailed video metadata

---

### `A_B_Test/youtube_five_country_2025_collector.py`
Collects YouTube video data for five European countries (Finland, Norway, Czechia,
Hungary, Greece) scoped to 2025 releases. Targets ~40 videos per country using
country-specific queries and filters out karaoke, covers, reactions, and playlists.
Requires `YOUTUBE_API_KEY`.

```bash
python A_B_Test/youtube_five_country_2025_collector.py
```

Outputs (written next to the script in `A_B_Test/`):
- `youtube_five_country_2025_data.md` — collected video data as Markdown
- `youtube_five_country_2025_raw.json` — raw search results
- `youtube_five_country_2025_candidates.json` — filtered candidates
- `youtube_five_country_2025_details.json` — detailed video metadata

---

## Market Research Scripts

Each country under `Market Research/` has a dedicated research script that pulls data
from iTunes, MusicBrainz, and public sources to produce a structured AI music market
report. Scripts share the same interface.

### `Market Research/Finland/finland_ai_music_market_research.py`

```bash
# Default output
python "Market Research/Finland/finland_ai_music_market_research.py"

# Options
python "Market Research/Finland/finland_ai_music_market_research.py" \
  --output Finland_AI_Music_Market_Report.md \
  --refresh-itunes \         # re-fetch iTunes data
  --refresh-musicbrainz      # re-fetch MusicBrainz data
```

Output: `Market Research/Finland/Finland_AI_Music_Market_Report.md`

---

### `Market Research/Norway/norway_ai_music_market_research.py`

```bash
python "Market Research/Norway/norway_ai_music_market_research.py"
```

Output: `Market Research/Norway/Norway_Norwegian_AI_Music_Market_Report.md`

---

### Country Reports (pre-generated, no script)

These reports were produced manually or by earlier script runs and live as Markdown files:

| Country | Report |
|---|---|
| Czechia | `Market Research/Czechia/Czechia_Czech_Language_AI_Music_Market_Report.md` |
| Greece | `Market Research/Greece/Greece_Greek_Language_AI_Music_Market_Report.md` |
| Hungary | `Market Research/Hungary/Hungary_Hungarian_Language_AI_Music_Market_Report.md` |
| Thailand | `Market Research/Thailand/Thailand_Thai_Language_AI_Music_Market_Report.md` |

---

## Visualization

### `Market Research/generate_matrix_charts.py`
Reads `Market Research/Seven_Country_AI_Music_Matrix.md` and generates two chart images
using Pillow (no matplotlib required).

```bash
python "Market Research/generate_matrix_charts.py"
```

Outputs:
- `Market Research/Charts/comprehensive_score_bar.png` — bar chart of composite investment scores
- `Market Research/Charts/ai_interest_market_value_bubble.png` — bubble chart of AI interest vs. market value

---

## Key Reference Documents

| Document | Description |
|---|---|
| `A_B_Test/Five_Country_Test_Plan.md` | Geo A/B test design: 5 European countries, 20 AI songs each, revenue optimization focus |
| `A_B_Test/youtube_five_country_2025_data.md` | Collected YouTube data for the 5-country test |
| `Market Research/Seven_Country_AI_Music_Matrix.md` | Investment scoring matrix across 7 countries |
| `Data - Runze/Data Analysis/itunes_us_top100_analysis.md` | iTunes US Top 100 analysis |
| `Data - Runze/Data Analysis/youtube_music_top100_likes_analysis_en.md` | YouTube Top 100 likes analysis |

---

See [workflows.md](workflows.md) for step-by-step guides.
