# Lyric-Level Embedding Mini Test Results

## Purpose
This note summarizes the first lyric excerpt-level embedding similarity test for Turkish YouTube sample songs.

## Test Setup
The test compares selected lyric excerpts with predefined theme labels using embedding similarity.

## Candidate Theme Labels
- Romance / heartbreak
- Hometown / nostalgia
- Local food / culture
- Party / dance
- Healing / relaxing
- Other / emerging theme

## Results

| Song | Manual Tag | Top Embedding Match | Similarity Score |
|---|---|---|---|
| Gül Rengi | Romance / heartbreak | Romance / heartbreak | 0.5430 |
| Üsküdar'a Gider İken | Local food / culture | Hometown / nostalgia | 0.2307 |
| İmkansızım | Romance / heartbreak | Romance / heartbreak | 0.2520 |
| Gesi Bağları | Hometown / nostalgia or Local food / culture | Healing / relaxing | 0.2638 |

## Preliminary Observations
- Lyric-level embedding aligned with the manual tags for Gül Rengi and İmkansızım.
- Gül Rengi improved compared with the title-level result, suggesting that lyric excerpts may add useful thematic context.
- Üsküdar'a Gider İken and Gesi Bağları still show limitations, suggesting that culturally specific or traditional songs may require manual interpretation.

## Next Step
Expand the Turkish YouTube sample with an AI-assisted collection script, then compare title-level and lyric-level embeddings on the larger dataset.