# Lyric-Level Embedding Mini Test Results

## Purpose
This note summarizes two exploratory lyric-level embedding tests for Turkish YouTube songs:
- Test 1 used manually selected lyric excerpts.
- Test 2 used reviewed full transcripts collected through the transcript pipeline.

## Candidate Theme Labels
- Romance / heartbreak
- Hometown / nostalgia
- Local food / culture
- Party / dance
- Healing / relaxing
- Other / emerging theme

## Test 1: Lyric Excerpts
| Song | Manual Tag | Top Embedding Match | Similarity Score |
|---|---|---|---:|
| Gül Rengi | Romance / heartbreak | Romance / heartbreak | 0.5430 |
| Üsküdar'a Gider İken | Local food / culture | Hometown / nostalgia | 0.2307 |
| İmkansızım | Romance / heartbreak | Romance / heartbreak | 0.2520 |
| Gesi Bağları | Hometown / nostalgia or Local food / culture | Healing / relaxing | 0.2638 |

## Test 2: Reviewed Full Transcripts
| Song | Top Match | Score | Second-Best Match | Margin |
|---|---|---:|---|---:|
| Kesik Çayır Biçilir mi? | Hometown / nostalgia | 0.4018 | Local food / culture | 0.0375 |
| Vay Canım Vay | Romance / heartbreak | 0.3745 | Healing / relaxing | 0.0263 |
| Aramam | Healing / relaxing | 0.3886 | Romance / heartbreak | 0.0149 |
| New Turkish Viral Song 2026 | Party / dance | 0.5098 | Romance / heartbreak | 0.0620 |
| Şimdi Uzaklardasın | Romance / heartbreak | 0.5159 | Hometown / nostalgia | 0.0414 |

## Observations
- Full transcripts produced broadly reasonable predictions, particularly for songs with clear romance or party-related language.
- Related themes still overlapped (e.g., Romance / heartbreak with Healing / relaxing, and Hometown / nostalgia with Local food / culture).
- Smaller score margins may indicate greater semantic overlap or classification uncertainty.
- These findings remain exploratory because the sample is small.

## Test 3: Expanded 8-Song Evaluation
The pipeline was applied to eight reviewed Turkish songs. Results showed frequent overlap between Romance / heartbreak and Healing / relaxing, small score margins, and weaker performance on social-protest themes and noisy transcripts.

The results are best treated as machine-assisted pre-labeling and preserved as a baseline while the next phase focuses on pipeline automation and the DistroKid release test.

## Output
- Script: `src/lyric_level_embedding.py`
- Results: `data/processed/turkish_lyric_embedding_results.csv`
- Expanded results: `data/processed/turkish_lyric_embedding_results_8.csv`

## Next Step
Prioritize pipeline automation and the DistroKid release test. Revisit theme descriptions after collecting more samples.