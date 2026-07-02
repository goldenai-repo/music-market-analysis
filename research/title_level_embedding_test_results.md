# Title-Level Embedding Mini Test Results

## Purpose
This note summarizes the first title-level embedding similarity test for Turkish YouTube sample songs.

## Test Setup
The test compares selected song titles with predefined theme labels using embedding similarity.

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
| Gül Rengi | Romance / heartbreak | Other / emerging theme | 0.3462 |
| Üsküdar'a Gider İken | Hometown / nostalgia or Local food / culture | Hometown / nostalgia | 0.4496 |
| İmkansızım | Romance / heartbreak or Other / emerging theme | Romance / heartbreak | 0.2254 |
| Gesi Bağları | Hometown / nostalgia or Local food / culture | Healing / relaxing | 0.4743 |

## Preliminary Observations
- Embedding results partially align with current manual tags.
- Üsküdar'a Gider İken and İmkansızım matched reasonably well with the manual interpretation.
- Gül Rengi and Gesi Bağları did not fully align, suggesting that title-only embedding may be limited for metaphorical or culturally specific songs.

## Next Step
Add lyric excerpts to test whether lyric-level embedding improves theme classification.