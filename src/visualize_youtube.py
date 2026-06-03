import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd


INPUT_PATH = Path("data/processed/youtube_lofi_sample.csv")
OUTPUT_DIR = Path("outputs/figures")

TITLE_MAX_LEN = 30


def compact_count(x, _) -> str:
    if x >= 1_000_000:
        return f"{x / 1_000_000:.0f}M"
    if x >= 1_000:
        return f"{x / 1_000:.0f}K"
    return f"{x:.0f}"


def load_data(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")
    return pd.read_csv(path)


def to_ascii(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    ascii_only = normalized.encode("ascii", errors="ignore").decode("ascii")
    return re.sub(r"\s+", " ", ascii_only).strip()


def make_chart_labels(df: pd.DataFrame, max_len: int = TITLE_MAX_LEN) -> pd.Series:
    def build_label(row) -> str:
        title = to_ascii(str(row["title"]))
        if len(title) > max_len:
            title = title[:max_len].rstrip() + "..."

        channel = to_ascii(str(row["channel_title"]))
        if not channel:
            channel = to_ascii(str(row["channel_title"])[:15])

        return f"{title} - {channel}"

    return df.apply(build_label, axis=1)


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["chart_label"] = make_chart_labels(df)
    df["engagement_rate"] = (df["like_count"] + df["comment_count"]) / df["view_count"]
    return df


def save_bar_chart(
    labels: pd.Series,
    values: pd.Series,
    title: str,
    xlabel: str,
    output_path: Path,
    xformatter=None,
) -> None:
    n = len(labels)
    fig, ax = plt.subplots(figsize=(12, max(5, n * 0.7)))
    ax.barh(labels, values)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.invert_yaxis()
    if xformatter is not None:
        ax.xaxis.set_major_formatter(xformatter)
    fig.tight_layout()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=120)
    plt.close(fig)


def main() -> None:
    try:
        df = load_data(INPUT_PATH)
    except FileNotFoundError as error:
        print(f"Error: {error}")
        return

    df = prepare_data(df)

    charts = [
        (
            "view_count",
            "View Count",
            "YouTube - Views by Video",
            OUTPUT_DIR / "youtube_views_bar.png",
            ticker.FuncFormatter(compact_count),
        ),
        (
            "like_count",
            "Like Count",
            "YouTube - Likes by Video",
            OUTPUT_DIR / "youtube_likes_bar.png",
            ticker.FuncFormatter(compact_count),
        ),
        (
            "engagement_rate",
            "Engagement Rate (%)",
            "YouTube - Engagement Rate by Video",
            OUTPUT_DIR / "youtube_engagement_rate_bar.png",
            ticker.PercentFormatter(xmax=1, decimals=1),
        ),
    ]

    for column, xlabel, title, output_path, xformatter in charts:
        chart_df = df.sort_values(column, ascending=False)
        save_bar_chart(
            labels=chart_df["chart_label"],
            values=chart_df[column],
            title=title,
            xlabel=xlabel,
            output_path=output_path,
            xformatter=xformatter,
        )

    print(f"Saved {len(charts)} charts to {OUTPUT_DIR}/")
    for _, _, title, output_path, _ in charts:
        print(f"  {output_path.name}")


if __name__ == "__main__":
    main()
