import os
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


load_dotenv()

SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_SEARCH_URL = "https://api.spotify.com/v1/search"

# Uses a mainstream track query to test whether Spotify returns popularity
DEFAULT_QUERY = "Taylor Swift Anti-Hero"
DEFAULT_LIMIT = 10

OUTPUT_PATH = Path("data/processed/spotify_tracks_mainstream_sample.csv")


def get_access_token() -> str:
    """Get a Spotify access token using Client Credentials Flow."""
    client_id = os.getenv("SPOTIFY_CLIENT_ID")
    client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET must be set in your .env file."
        )

    response = requests.post(
        SPOTIFY_TOKEN_URL,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
        timeout=10,
    )
    response.raise_for_status()

    return response.json()["access_token"]


def search_tracks(token: str, query: str = DEFAULT_QUERY, limit: int = DEFAULT_LIMIT) -> list[dict]:
    """Search Spotify tracks for a given query."""
    headers = {"Authorization": f"Bearer {token}"}
    params = {
        "q": query,
        "type": "track",
        "limit": limit,
        "market": "US",
    }

    response = requests.get(
        SPOTIFY_SEARCH_URL,
        headers=headers,
        params=params,
        timeout=10,
    )

    if response.status_code != 200:
        print("Status code:", response.status_code)
        print("Response text:", response.text)

    response.raise_for_status()

    return response.json().get("tracks", {}).get("items", [])


def parse_results(items: list[dict]) -> pd.DataFrame:
    """Parse Spotify API track results into a dataframe."""
    rows = []

    for i, track in enumerate(items):
        if i == 0:
            print("First track fields:", list(track.keys()))
            print("Popularity field:", track.get("popularity"))

        rows.append(
            {
                "track_name": track.get("name"),
                "artist_name": ", ".join(
                    artist.get("name", "") for artist in track.get("artists", [])
                ),
                "album_name": track.get("album", {}).get("name"),
                "release_date": track.get("album", {}).get("release_date"),
                "duration_ms": track.get("duration_ms"),
                "explicit": track.get("explicit"),
                "spotify_id": track.get("id"),
                "popularity": track.get("popularity"),
                "spotify_url": track.get("external_urls", {}).get("spotify"),
            }
        )

    return pd.DataFrame(rows)


def save_results(df: pd.DataFrame, output_path: Path = OUTPUT_PATH) -> None:
    """Save dataframe to CSV."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)


def main(query: str = DEFAULT_QUERY, limit: int = DEFAULT_LIMIT) -> None:
    print(f"Fetching Spotify tracks for: '{query}'")

    try:
        token = get_access_token()
        items = search_tracks(token, query=query, limit=limit)
    except EnvironmentError as error:
        print(f"Credential error: {error}")
        return
    except requests.RequestException as error:
        print(f"Spotify API request error: {error}")
        return

    if not items:
        print("No tracks returned.")
        return

    df = parse_results(items)
    save_results(df)

    print(f"Saved {len(df)} tracks to {OUTPUT_PATH}")
    print(df[["track_name", "artist_name", "popularity"]].head())


if __name__ == "__main__":
    main()