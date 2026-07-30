# Workflows

Step-by-step guides for common end-to-end scenarios. All commands run from the **repo root**.  
See [tools.md](tools.md) for full flag reference for each script.

---

## 1. Turkish Music Pipeline (end to end)

Discover Turkish YouTube videos, collect transcripts, annotate, and run theme embedding.

```
Step 1 — collect candidates
Step 2 — clean & flag for review        [automated]
Step 3 — manual review
Step 4 — collect transcripts            [automated]
Step 5 — prepare review sheet           [automated]
Step 6 — manual annotation
Step 7 — filter to analysis-ready       [automated]
Step 8 — run embedding                  [automated]
```

```bash
# Step 1: search YouTube for Turkish music videos
python src/collect_turkish_youtube_samples.py
# → data/processed/turkish_youtube_auto_sample.csv

# Step 2: clean and add AI-related flags
python src/clean_turkish_youtube_samples.py
# → data/processed/turkish_youtube_review_flagged_sample.csv

# Step 3: open the flagged CSV and manually mark which videos to keep
#         (edit the review column; save as turkish_youtube_review_sample.csv)

# Step 4: fetch transcripts for reviewed videos (process 50 at a time)
python src/collect_transcripts.py --limit 50
# → data/processed/turkish_transcripts.csv

# Step 5: generate a review sheet with suggested quality/language columns
python src/prepare_transcript_review.py
# → data/processed/turkish_transcript_review_21.csv

# Step 6: open that CSV and fill in transcript_quality and lyric_language_verified

# Step 7: filter to usable, verified-Turkish rows
python src/prepare_analysis_ready.py
# → data/processed/turkish_transcript_analysis_ready.csv

# Step 8: run lyric-level theme embedding
python src/lyric_level_embedding.py
# → data/processed/turkish_lyric_embedding_results_8.csv
```

---

## 2. Artist-Song Search Pipeline

Start from a curated artist-song seed list rather than broad keyword search.

```bash
# Step 1: search YouTube using the seed list (process all songs, all query variants)
python src/search_turkish_artist_songs.py \
  --max-songs 0 \
  --query-variant all \
  --results-per-song 5
# → data/processed/turkish_artist_song_candidates.csv

# Step 2: manually review candidates, keep the best video per song

# Step 3: collect transcripts for reviewed candidates
python src/collect_transcripts.py \
  --input data/processed/turkish_artist_song_candidates_reviewed.csv \
  --output data/processed/turkish_artist_song_transcripts.csv \
  --limit 100

# Step 4: prepare review sheet → annotate → filter → embed (same as steps 5–8 above)
python src/prepare_transcript_review.py
python src/prepare_analysis_ready.py
python src/lyric_level_embedding.py
```

---

## 3. AI/Suno-Only Analysis

Focus the entire pipeline on videos flagged as Suno-AI-related. Useful for a targeted
comparison of AI-generated vs. non-AI content.

```bash
# Collect transcripts only for AI-flagged rows
python src/collect_transcripts.py --ai-only --limit 100

# Prepare and filter (same defaults as above)
python src/prepare_transcript_review.py
python src/prepare_analysis_ready.py

# Run embedding scoped to AI-flagged rows only
python src/lyric_level_embedding.py --ai-only
# → data/processed/turkish_lyric_embedding_results_8.csv  (AI rows only)
```

---

## 4. Incremental Transcript Collection

When the candidate list is large, collect transcripts in batches across multiple sessions
without losing progress (the script skips videos already written to the output file).

```bash
# Session 1
python src/collect_transcripts.py --limit 25

# Session 2 (picks up where session 1 left off automatically)
python src/collect_transcripts.py --limit 25

# Re-fetch any videos that failed previously
python src/collect_transcripts.py --retry-existing --limit 10
```

---

## 5. Transcript Spot-Check

Verify a single video before committing to a full batch run, or debug a transcript
that looks wrong in the output CSV.

```bash
# Fetch and print the transcript for one video
python src/test_youtube_transcript_single.py <video_id>

# Example
python src/test_youtube_transcript_single.py dQw4w9WgXcQ
```

---

## 6. Embedding Model Comparison

Run `lyric_level_embedding.py` with two different models and compare theme scores
to choose the best model for the dataset.

```bash
# Model A (default multilingual MiniLM)
python src/lyric_level_embedding.py \
  --model sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2 \
  --output data/processed/embedding_results_minilm.csv

# Model B (larger multilingual MPNet)
python src/lyric_level_embedding.py \
  --model sentence-transformers/paraphrase-multilingual-mpnet-base-v2 \
  --output data/processed/embedding_results_mpnet.csv

# Quick sanity checks (print to stdout, no file output)
python src/title_level_embedding_similarity_test.py
python src/lyric_excerpt_level_embedding_similarity_test.py
```

---

## 7. iTunes Data Collection & Analysis

Fetch iTunes chart/search data and produce a cleaned dataset with a summary report.

```bash
# Step 1: fetch from the iTunes Search API (no auth needed)
python src/fetch_itunes.py
# → data/raw/itunes_music_data.csv

# Step 2: clean and summarize
python src/analyze_itunes.py
# → data/processed/itunes_music_cleaned.csv
# → data/processed/itunes_analysis_summary.txt
```

---

## 8. YouTube Lo-Fi Sample Collection & Visualization

Collect a lo-fi YouTube sample and generate exploratory charts.

```bash
# Step 1: fetch video metadata (requires YOUTUBE_API_KEY)
python src/fetch_youtube.py
# → data/processed/youtube_lofi_sample.csv

# Step 2: generate matplotlib charts
python src/visualize_youtube.py
```

---

## 9. Spotify Mainstream Sample Collection

Fetch a sample of mainstream tracks from Spotify for cross-platform comparison.

```bash
# Requires SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET in .env
python src/fetch_spotify.py
# → data/processed/spotify_tracks_mainstream_sample.csv
```

After collection, this dataset can be used alongside the iTunes and YouTube datasets
for cross-platform genre or engagement analysis.
