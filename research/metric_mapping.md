# Metric Mapping

## Purpose

The goal is to map which platforms can provide performance and engagement metrics that complement the existing iTunes metadata baseline.

## Metric Mapping

| Dimension | Metric | Possible Source | Notes |
|---|---|---|---|
| Sales | Sales volume | Chart ranking, third-party data | Direct sales volume is not available from iTunes Search API |
| Popularity | Popularity score | Spotify Web API | API access tested; the Search response did not include the popularity field in the sample |
| Play volume | Views / play count | YouTube Data API, NetEase, QQ Music | YouTube API tested; view count was available in the sample |
| Engagement | Likes / comments | YouTube Data API, NetEase, QQ Music | YouTube API tested; like and comment counts were available in the sample |
| Metadata | Track, artist, genre, release date, price | iTunes Search API | Existing baseline dimensions from the iTunes dataset |

## Next Step

Use YouTube sample data to build initial visualizations for video-level engagement metrics.