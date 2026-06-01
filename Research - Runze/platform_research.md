# Music Platform API Integration and Data Comparison

Research date: 2026-05-30

| Platform | API Integration Difficulty | Auth / Access Method | Music Data Available | Main Limits | Simple Recommendation |
| --- | --- | --- | --- | --- | --- |
| iTunes / iTunes Songs | Very easy | Usually no OAuth needed; direct HTTP requests to the iTunes Search API | Songs, albums, artists, music videos, artwork, preview URLs, prices, country/region, genres, release dates, iTunes IDs, store links | Mainly iTunes Store data, not user data; preview audio must follow Apple usage rules | Best for quickly filling basic metadata, cover art, and preview links |
| Spotify | Medium | OAuth 2.0; app token for public catalog data, user authorization for user data | Tracks, albums, artists, playlists, search results, artwork, ISRC, popularity, saved tracks, user playlists, recently played, top tracks/artists | No full audio files; rate limits; user data requires authorization; some audio analysis features should not be relied on | Strong mainstream option for playlists, user taste analysis, and catalog metadata |
| Deezer | Easy | Public data can be queried directly; user data and write actions require OAuth | Tracks, albums, artists, playlists, charts, genres, radio, artwork, 30-second previews, user favorites/playlists | No full audio; user-related data requires authorization; limited deep audio analysis data | Good lightweight music metadata source |
| SoundCloud | Medium | OAuth 2.1; some public data can be queried, user actions require authorization | Tracks, users, playlists, search results, artwork, descriptions, tags, public interaction data such as plays/likes/comments, some stream information | More UGC-focused than a traditional licensed catalog; some tracks cannot be streamed off-platform; access depends on uploader settings | Best for independent music, UGC audio, and creator data |
| KKBOX | Medium | OAuth 2.0; requires developer account and client id/secret | Tracks, albums, artists, playlists, charts, new releases, featured playlists, localized catalog data | Catalog is strongly region-dependent, such as TW/HK/JP/SG/MY; full playback depends on SDK/licensing | Useful for Mandarin and Asian music market data |
| Napster | Easy | Developer account + API key; user data requires additional authorization | Tracks, albums, artists, playlists, genres, charts, trending music, artist images, album art, preview clips, listen counts | Catalog coverage and market relevance are lower than Spotify; music content usage must follow Napster terms | Good supplementary metadata source with low integration cost |
| YouTube | Medium | API key for public data; OAuth for private data or write actions; quota applies | Videos, channels, playlists, search results, thumbnails, titles, descriptions, publish dates, view counts, like counts, comments, channel subscriber counts | Not a pure music catalog API; no official public YouTube Music API; search and bulk collection can consume quota quickly | Best for music videos, MVs, Shorts, channel popularity, and public video data |

## Recommended Integration Order

| Priority | Platform | Reason |
| --- | --- | --- |
| 1 | iTunes / iTunes Songs | Easiest to use; direct search; good for basic metadata |
| 2 | Deezer | Lightweight integration with solid track/album/artist/playlist data |
| 3 | Napster | API key based, clear docs, useful as a supplemental catalog |
| 4 | Spotify | High-value data, but OAuth and usage limits require more work |
| 5 | YouTube | Valuable video popularity data, but not a pure music API |
| 6 | SoundCloud | Good for UGC and independent music, not ideal as the only standard catalog source |
| 7 | KKBOX | Valuable for Asian music, but region and token handling add complexity |

## References

- iTunes Search API: https://performance-partners.apple.com/resources/documentation/itunes-store-web-service-search-api/
- Spotify Web API: https://developer.spotify.com/documentation/web-api
- Deezer API: https://developers.deezer.com/api
- SoundCloud API: https://developers.soundcloud.com/docs/api/
- KKBOX Open API: https://developer.kkbox.com
- Napster API: https://developer.prod.napster.com/
- YouTube Data API: https://developers.google.com/youtube/v3/docs
