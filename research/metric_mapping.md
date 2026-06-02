# Metric Mapping

## Purpose

The goal is to map which platforms can provide performance and engagement metrics that complement the existing iTunes metadata baseline.

## Metric Mapping

| Dimension | Metric | Possible Source | Notes |
|---|---|---|---|
| Sales | Sales volume | Chart ranking, third-party data | Direct sales volume is not available from iTunes Search API |
| Popularity | Popularity score | Spotify Web API | Spotify can provide track-level popularity |
| Play volume | Views / play count | YouTube Data API, NetEase, QQ Music | Useful for estimating listening demand |
| Engagement | Likes / comments | YouTube Data API, NetEase, QQ Music | Useful for measuring audience response |
| Metadata | Track, artist, genre, release date, price | iTunes Search API | Existing baseline dimensions from the iTunes dataset |

## Next Step

Explore Spotify Web API to collect track-level popularity scores as the next performance metric.