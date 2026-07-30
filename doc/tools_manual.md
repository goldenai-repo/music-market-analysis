# Tools Reference

All scripts live in `src/` and should be run from the **repo root**.

## Setup

```bash
pip install -r requirements.txt
```

Create a `.env` file in the repo root (never commit it):

```
YOUTUBE_API_KEY=your_key_here
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

---

## Data Collection

### `fetch_itunes.py`
Fetches music data from the iTunes Search API. No auth required.

```bash
python src/fetch_itunes.py
```

Output: `data/raw/itunes_music_data.csv`

---

### `fetch_youtube.py`
Fetches YouTube video metadata (e.g. lo-fi sample). Requires `YOUTUBE_API_KEY`.

```bash
python src/fetch_youtube.py
```

Output: `data/processed/youtube_lofi_sample.csv`

---

### `fetch_spotify.py`
Fetches a mainstream track sample from Spotify. Requires `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET`.

```bash
python src/fetch_spotify.py
```

Output: `data/processed/spotify_tracks_mainstream_sample.csv`

---

### `collect_turkish_youtube_samples.py`
Searches YouTube for Turkish music videos and saves raw candidates. Requires `YOUTUBE_API_KEY`.

```bash
python src/collect_turkish_youtube_samples.py
```

Output: `data/processed/turkish_youtube_auto_sample.csv`

---

### `search_turkish_artist_songs.py`
Searches YouTube for candidate videos using an artist-song seed list. Requires `YOUTUBE_API_KEY`.

```bash
# Default: 3 results per song, process 5 seed songs, base query
python src/search_turkish_artist_songs.py

# Options
python src/search_turkish_artist_songs.py \
  --input data/processed/turkish_artist_song_pipeline.csv \
  --output data/processed/turkish_artist_song_candidates.csv \
  --results-per-song 5 \
  --max-songs 0 \                    # 0 = process all seeds
  --query-variant all \              # base | ai | suno | cover | all
  --region-code TR \
  --relevance-language tr \
  --order relevance                  # relevance | date | rating | title | viewCount
```

Output: `data/processed/turkish_artist_song_candidates.csv`

---

### `collect_transcripts.py`
Batch-fetches YouTube transcripts for videos in a reviewed CSV. Uses `youtube-transcript-api` (no API key needed).

```bash
# Default: process up to 10 new videos from the default review CSV
python src/collect_transcripts.py

# Options
python src/collect_transcripts.py \
  --input data/processed/turkish_youtube_review_sample.csv \
  --output data/processed/turkish_transcripts.csv \
  --limit 50 \           # max new videos to process
  --sleep 2.0 \          # seconds between requests
  --ai-only \            # only rows where ai_suno_related=yes
  --retry-existing       # reprocess videos already in the output
```

Output: `data/processed/turkish_transcripts.csv` (default)

---

### `fetch_youtube_transcripts.py`
Fetches transcripts for manually validated Turkish music videos (simplified single-batch version).

```bash
python src/fetch_youtube_transcripts.py
```

---

### `test_youtube_transcript_single.py`
Fetches the transcript for a single YouTube video ID. Useful for spot-checking.

```bash
python src/test_youtube_transcript_single.py <video_id>
# e.g.
python src/test_youtube_transcript_single.py dQw4w9WgXcQ
```

---

## Data Cleaning & Preparation

### `clean_turkish_youtube_samples.py`
Cleans the raw Turkish YouTube sample and adds AI-related review flags.

```bash
python src/clean_turkish_youtube_samples.py
```

Input: `data/processed/turkish_youtube_auto_sample.csv`  
Output: `data/processed/turkish_youtube_review_flagged_sample.csv`

---

### `prepare_transcript_review.py`
Takes raw transcripts and produces a review-ready CSV with suggested quality/language columns for manual annotation.

```bash
python src/prepare_transcript_review.py
```

Input: `data/processed/turkish_transcripts_21.csv`  
Output: `data/processed/turkish_transcript_review_21.csv`

---

### `prepare_analysis_ready.py`
Filters the manually reviewed transcript CSV, keeping only rows with usable transcript quality and verified Turkish lyrics. Output feeds into the embedding step.

```bash
python src/prepare_analysis_ready.py

# Options
python src/prepare_analysis_ready.py \
  --input data/processed/turkish_transcript_review_21.csv \
  --output data/processed/turkish_transcript_analysis_ready.csv
```

Output: `data/processed/turkish_transcript_analysis_ready.csv`

---

## Analysis & Embedding

### `lyric_level_embedding.py`
Runs multilingual sentence-transformer embeddings on Turkish lyrics and scores them against theme labels.

```bash
# Default: all eligible rows, default model
python src/lyric_level_embedding.py

# Options
python src/lyric_level_embedding.py \
  --input data/processed/turkish_transcript_analysis_ready.csv \
  --output data/processed/turkish_lyric_embedding_results_8.csv \
  --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
  --ai-only \          # only rows where ai_suno_related=yes
  --limit 50 \         # 0 = all eligible rows
  --batch-size 32
```

Output: `data/processed/turkish_lyric_embedding_results_8.csv`

---

### `lyric_excerpt_level_embedding_similarity_test.py`
Quick test: runs excerpt-level embedding similarity and prints results to stdout. No file output.

```bash
python src/lyric_excerpt_level_embedding_similarity_test.py
```

---

### `title_level_embedding_similarity_test.py`
Quick test: runs title-level embedding similarity against theme labels and prints results. No file output.

```bash
python src/title_level_embedding_similarity_test.py
```

---

### `analyze_itunes.py`
Cleans raw iTunes data and writes a summary report.

```bash
python src/analyze_itunes.py
```

Input: `data/raw/itunes_music_data.csv`  
Output: `data/processed/itunes_music_cleaned.csv`, `data/processed/itunes_analysis_summary.txt`

---

## Visualization

### `visualize_youtube.py`
Generates matplotlib charts from the YouTube lo-fi sample data.

```bash
python src/visualize_youtube.py
```

Input: `data/processed/youtube_lofi_sample.csv`

---

## Tests

```bash
# Run all tests
pytest

# Run a single test
pytest tests/test_fetch.py::test_function_name
```


See [workflows.md](workflows.md) for step-by-step guides covering common end-to-end scenarios.
