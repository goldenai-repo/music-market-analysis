import requests
import pandas as pd
from pathlib import Path


ITUNES_API_URL = "https://itunes.apple.com/search"
OUTPUT_PATH = Path("data/raw/itunes_music_data.csv")


def fetch_itunes_music(search_term: str = "lofi study", limit: int = 200) -> list[dict]:
    params = {
        "term": search_term,
        "media": "music",
        "entity": "song",
        "limit": limit,
    }
    headers = {
        "User-Agent": "music-market-analysis/1.0"
    }

    response = requests.get(ITUNES_API_URL, params=params, headers=headers, timeout=10)
    response.raise_for_status()
    return response.json().get("results", [])


def parse_results(results: list[dict]) -> pd.DataFrame:
    rows = []

    for item in results:
        rows.append({
            "track_name": item.get("trackName"),
            "artist_name": item.get("artistName"),
            "album_name": item.get("collectionName"),
            "genre": item.get("primaryGenreName"),
            "release_date": item.get("releaseDate"),
            "duration_ms": item.get("trackTimeMillis"),
            "track_price": item.get("trackPrice"),
            "currency": item.get("currency"),
            "country": item.get("country"),
            "preview_url": item.get("previewUrl"),
            "artwork_url": item.get("artworkUrl100"),
        })

    return pd.DataFrame(rows)


def main(search_term: str = "lofi study", limit: int = 200):
    print(f"Fetching iTunes data for: '{search_term}'")

    try:
        results = fetch_itunes_music(search_term, limit)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return

    if not results:
        print("No results returned.")
        return

    df = parse_results(results)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    print(f"Saved {len(df)} rows to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()