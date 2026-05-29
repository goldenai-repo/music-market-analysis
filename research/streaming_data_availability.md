# Streaming Platform Data Availability

| Platform / API | Access | Available Data | Limitations | Sample Request / Endpoint |
|---|---|---|---|---|
| iTunes Search API | Easy, no API key required | Track, artist, album, genre, release date, duration, preview URL, artwork | No stream counts or listener data | `https://itunes.apple.com/search?term=lofi+study&media=music&entity=song&limit=200` |
| YouTube Data API | Medium, needs API key | Video title, channel, publish date, views, likes, comments | More video-based than music-specific; YouTube Music data is limited | `search.list`, `videos.list` |
| Apple Music API | Medium to hard, needs developer authorization | Songs, albums, artists, playlists, charts | No public stream counts; user data needs permission | `/v1/catalog/{storefront}/search` |
| Spotify Web API | Medium, needs authentication | Tracks, artists, albums, playlists, popularity score | No exact stream counts or listener demographics; requires authentication | `/v1/search`, `/v1/tracks/{id}`, `/v1/artists/{id}` |

## Initial Conclusion

The iTunes Search API is the most accessible option for the first data-fetching demo because it returns structured music metadata without requiring authentication. Other platforms may provide useful data, but they require API keys or authorization, so they are documented as possible future sources.