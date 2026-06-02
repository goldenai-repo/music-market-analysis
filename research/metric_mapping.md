# Metric Mapping

## Purpose

The goal is to map which platforms can provide performance and engagement metrics that complement the existing iTunes metadata baseline.

## Metric Mapping

| Dimension | Metric | Possible Source | Notes |
|---|---|---|---|
| Sales | Sales volume | Chart ranking, third-party data | Direct sales volume is not available from iTunes Search API |
| Popularity | Popularity score | Spotify Web API | API access tested; Search response did not include the popularity field in the current sample |
| Play volume | Views / play count | YouTube Data API, NetEase, QQ Music | Useful for estimating listening demand |
| Engagement | Likes / comments | YouTube Data API, NetEase, QQ Music | Useful for measuring audience response |
| Metadata | Track, artist, genre, release date, price | iTunes Search API | Existing baseline dimensions from the iTunes dataset |

## Next Step

Explore YouTube Data API for public engagement metrics such as views, likes, and comments.