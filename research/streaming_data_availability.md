# Streaming Platform Data Availability

| Platform / API | Access | Available Data | Limitations | Sample Request / Endpoint |
|---|---|---|---|---|
| iTunes Search API | Easy, no API key required | Track, artist, album, genre, release date, duration, preview URL, artwork | No stream counts or listener data | `https://itunes.apple.com/search?term=lofi+study&media=music&entity=song&limit=200` |
| YouTube Data API | Medium, needs API key | Video title, channel, publish date, views, likes, comments | More video-based than music-specific; YouTube Music data is limited | `search.list`, `videos.list` |
| Apple Music API | Medium to hard, needs developer authorization | Songs, albums, artists, playlists, charts | No public stream counts; user data needs permission | `/v1/catalog/{storefront}/search` |
| Spotify Web API | Medium, needs authentication | Tracks, artists, albums, playlists, popularity score | No exact stream counts or listener demographics; requires authentication | `/v1/search`, `/v1/tracks/{id}`, `/v1/artists/{id}` |

## Initial Conclusion

The iTunes Search API is the most accessible option for the first data-fetching demo because it returns structured music metadata without requiring authentication. Other platforms may provide useful data, but they require API keys or authorization, so they are documented as possible future sources.

## iTunes Search API Finding

The iTunes Search API is useful for collecting structured music metadata, including artist, genre, release date, duration, price, preview URL, and artwork. These metadata fields are important dimensions for grouping and explaining music performance.

However, iTunes does not provide direct performance metrics such as sales, stream counts, listener data, popularity scores, likes, or comments.

Therefore, iTunes can be used as the metadata baseline, while additional sources are needed to collect performance and engagement metrics.

## Next Steps
- Use iTunes Search API as the metadata baseline.
- Explore YouTube Data API for public engagement metrics (views, likes, and comments).
- Explore Spotify Web API for track-level popularity score.
- Compare NetEase and QQ Music as potential Chinese-market data sources.