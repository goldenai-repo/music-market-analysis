import pandas as pd
from pathlib import Path

RAW_DATA_PATH = Path("data/raw/itunes_music_data.csv")
PROCESSED_DATA_PATH = Path("data/processed/itunes_music_cleaned.csv")
SUMMARY_OUTPUT_PATH = Path("data/processed/itunes_analysis_summary.txt")


def load_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year
    df["duration_min"] = df["duration_ms"] / 60000

    return df


def generate_summary(df: pd.DataFrame) -> str:
    total_tracks = len(df)
    unique_artists = df["artist_name"].nunique()
    unique_genres = df["genre"].nunique()
    avg_duration = df["duration_min"].mean()
    median_duration = df["duration_min"].median()

    top_genres = df["genre"].value_counts().head(10)
    top_artists = df["artist_name"].value_counts().head(10)
    release_years = df["release_year"].value_counts().sort_index().tail(10)

    summary = []
    summary.append("iTunes Music Data Analysis Summary")
    summary.append("=" * 40)
    summary.append(f"Total tracks: {total_tracks}")
    summary.append(f"Unique artists: {unique_artists}")
    summary.append(f"Unique genres: {unique_genres}")
    summary.append(f"Average duration: {avg_duration:.2f} minutes")
    summary.append(f"Median duration: {median_duration:.2f} minutes")

    summary.append("\nTop Genres:")
    summary.append(top_genres.to_string())

    summary.append("\nTop Artists:")
    summary.append(top_artists.to_string())

    summary.append("\nRecent Release Year Distribution:")
    summary.append(release_years.to_string())

    return "\n".join(summary)


def main() -> None:
    df = load_data(RAW_DATA_PATH)
    cleaned_df = clean_data(df)

    PROCESSED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    cleaned_df.to_csv(PROCESSED_DATA_PATH, index=False)

    summary = generate_summary(cleaned_df)
    SUMMARY_OUTPUT_PATH.write_text(summary)

    print(summary)
    print(f"\nSaved cleaned data to {PROCESSED_DATA_PATH}")
    print(f"Saved summary to {SUMMARY_OUTPUT_PATH}")


if __name__ == "__main__":
    main()