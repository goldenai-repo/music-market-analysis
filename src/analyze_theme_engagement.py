from pathlib import Path

import pandas as pd


INPUT_PATH = Path("data/processed/turkish_lyric_embedding_results_8.csv")
OUTPUT_DIR = Path("outputs")
SUMMARY_PATH = OUTPUT_DIR / "turkish_theme_engagement_summary.csv"
SONG_LEVEL_PATH = OUTPUT_DIR / "turkish_theme_engagement_song_level.csv"
FINDINGS_PATH = Path("research/turkish_theme_engagement_findings.md")


REQUIRED_COLUMNS = {
    "video_id",
    "artist_name",
    "song_title",
    "predicted_theme",
    "view_count",
    "like_count",
    "comment_count",
    "like_rate",
    "comment_rate",
    "score_margin",
    "transcript_quality",
    "channel_type",
}


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Input file not found: {path}")

    df = pd.read_csv(path)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(sorted(missing_columns))
        )

    numeric_columns = [
        "view_count",
        "like_count",
        "comment_count",
        "like_rate",
        "comment_rate",
        "score_margin",
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=[
            "predicted_theme",
            "view_count",
            "like_rate",
            "comment_rate",
        ]
    )

    return df


def create_song_level_table(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "video_id",
        "artist_name",
        "song_title",
        "predicted_theme",
        "view_count",
        "like_count",
        "comment_count",
        "like_rate",
        "comment_rate",
        "score_margin",
        "transcript_quality",
        "channel_type",
    ]

    return (
        df[columns]
        .sort_values(
            by=["predicted_theme", "view_count"],
            ascending=[True, False],
        )
        .reset_index(drop=True)
    )


def create_theme_summary(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby("predicted_theme", dropna=False)
        .agg(
            song_count=("video_id", "count"),
            mean_view_count=("view_count", "mean"),
            median_view_count=("view_count", "median"),
            mean_like_count=("like_count", "mean"),
            median_like_count=("like_count", "median"),
            mean_comment_count=("comment_count", "mean"),
            median_comment_count=("comment_count", "median"),
            mean_like_rate=("like_rate", "mean"),
            median_like_rate=("like_rate", "median"),
            mean_comment_rate=("comment_rate", "mean"),
            median_comment_rate=("comment_rate", "median"),
            mean_score_margin=("score_margin", "mean"),
            median_score_margin=("score_margin", "median"),
        )
        .reset_index()
    )

    theme_order = [
        "Romance / heartbreak",
        "Hometown / nostalgia",
        "Local food / culture",
        "Party / dance",
        "Healing / relaxing",
        "Other / emerging theme",
    ]

    summary["predicted_theme"] = pd.Categorical(
        summary["predicted_theme"],
        categories=theme_order,
        ordered=True,
    )

    return (
        summary.sort_values("predicted_theme")
        .reset_index(drop=True)
    )


def format_percent(value: float) -> str:
    return f"{value * 100:.4f}%"


def write_findings(
    df: pd.DataFrame,
    summary: pd.DataFrame,
    path: Path,
) -> None:
    theme_counts = df["predicted_theme"].value_counts()

    highest_views = summary.loc[summary["median_view_count"].idxmax()]
    highest_like_rate = summary.loc[summary["median_like_rate"].idxmax()]
    highest_comment_rate = summary.loc[
        summary["median_comment_rate"].idxmax()
    ]

    low_margin_count = int((df["score_margin"] < 0.005).sum())

    lines = [
        "# Preliminary Theme–Engagement Analysis",
        "",
        "## Scope",
        "",
        (
            f"This exploratory analysis uses {len(df)} Turkish songs with "
            "usable lyric transcripts and embedding-assisted theme labels."
        ),
        "",
        "## Theme Distribution",
        "",
    ]

    for theme, count in theme_counts.items():
        lines.append(f"- {theme}: {count} song(s)")

    lines.extend(
        [
            "",
            "## Preliminary Observations",
            "",
            (
                f"- **{highest_views['predicted_theme']}** has the highest "
                f"median view count "
                f"({highest_views['median_view_count']:,.0f})."
            ),
            (
                f"- **{highest_like_rate['predicted_theme']}** has the highest "
                f"median like rate "
                f"({format_percent(highest_like_rate['median_like_rate'])})."
            ),
            (
                f"- **{highest_comment_rate['predicted_theme']}** has the "
                f"highest median comment rate "
                f"({format_percent(highest_comment_rate['median_comment_rate'])})."
            ),
            (
                f"- {low_margin_count} of {len(df)} songs have a theme score "
                "margin below 0.005, indicating uncertain separation between "
                "the top two predicted themes."
            ),
            "",
            "## Interpretation",
            "",
            (
                "The current results should be treated as preliminary "
                "descriptive patterns rather than evidence of a causal or "
                "statistically significant relationship between lyrical "
                "themes and engagement."
            ),
            "",
            "## Limitations",
            "",
            "- The sample contains only eight songs.",
            "- Theme groups are highly unbalanced.",
            (
                "- Several embedding classifications have small score margins "
                "and should be treated as tentative."
            ),
            (
                "- Raw view counts are affected by upload age, artist "
                "popularity, channel type, promotion, and other confounding "
                "factors."
            ),
            (
                "- The sample includes only songs with usable Turkish "
                "transcripts, which may introduce transcript-availability "
                "selection bias."
            ),
        ]
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data(INPUT_PATH)
    song_level = create_song_level_table(df)
    summary = create_theme_summary(df)

    song_level.to_csv(SONG_LEVEL_PATH, index=False)
    summary.to_csv(SUMMARY_PATH, index=False)
    write_findings(df, summary, FINDINGS_PATH)

    print(f"Input songs: {len(df)}")
    print(f"Song-level output: {SONG_LEVEL_PATH}")
    print(f"Theme summary output: {SUMMARY_PATH}")
    print(f"Findings output: {FINDINGS_PATH}")
    print()
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()