from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModel, AutoTokenizer


DEFAULT_INPUT = Path(
    "data/processed/turkish_transcript_analysis_ready.csv"
)

DEFAULT_OUTPUT = Path(
    "data/processed/turkish_lyric_embedding_results_8.csv"
)

DEFAULT_MODEL = (
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

USABLE_QUALITIES = {
    "good",
    "usable_with_noise",
}

THEME_DESCRIPTIONS = {
    "Romance / heartbreak": (
        "Lyrics about romantic love, longing, separation, heartbreak, "
        "missing someone, emotional pain, or relationships."
    ),
    "Hometown / nostalgia": (
        "Lyrics about one's hometown, homeland, memories, distance, "
        "belonging, returning home, or nostalgia for the past."
    ),
    "Local food / culture": (
        "Lyrics about Turkish local traditions, folk culture, places, "
        "food, customs, regional identity, or cultural heritage."
    ),
    "Party / dance": (
        "Lyrics about dancing, celebration, nightlife, energy, parties, "
        "having fun, rhythm, or excitement."
    ),
    "Healing / relaxing": (
        "Lyrics about calmness, peace, comfort, healing, reflection, "
        "relaxation, hope, or emotional recovery."
    ),
    "Other / emerging theme": (
        "Lyrics whose main meaning does not clearly match romance, "
        "nostalgia, local culture, party, dance, healing, or relaxation."
    ),
}

OUTPUT_COLUMNS = [
    "video_id",
    "artist_name",
    "song_title",
    "candidate_title",
    "youtube_url",
    "ai_suno_related",
    "channel_type",
    "genre_style",
    "transcript_quality",
    "lyric_language_verified",
    "transcript_language",
    "predicted_theme",
    "similarity_score",
    "second_best_theme",
    "second_best_score",
    "score_margin",
    "romance_heartbreak_score",
    "hometown_nostalgia_score",
    "local_food_culture_score",
    "party_dance_score",
    "healing_relaxing_score",
    "other_emerging_theme_score",
    "view_count",
    "like_count",
    "comment_count",
    "like_rate",
    "comment_rate",
    "transcript_clean",
    "embedding_model",
]


def normalize_text(value: Any) -> str:
    """Convert a value to a stripped string."""
    return str(value or "").strip()


def normalize_label(value: Any) -> str:
    """Normalize categorical values for reliable comparison."""
    return normalize_text(value).lower()


def parse_number(value: Any) -> float | None:
    """Parse numeric CSV values safely."""
    text = normalize_text(value).replace(",", "")

    if not text:
        return None

    try:
        return float(text)
    except ValueError:
        return None


def safe_rate(
    numerator: Any,
    denominator: Any,
) -> str:
    """Calculate a rate while safely handling missing or invalid values."""
    numerator_value = parse_number(numerator)
    denominator_value = parse_number(denominator)

    if (
        numerator_value is None
        or denominator_value is None
        or denominator_value <= 0
    ):
        return ""

    return f"{numerator_value / denominator_value:.8f}"


def read_csv(
    path: Path,
) -> tuple[list[dict[str, str]], list[str]]:
    """Read and validate the analysis-ready input CSV."""
    if not path.exists():
        raise FileNotFoundError(
            f"Input file not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)
        rows = list(reader)
        headers = reader.fieldnames or []

    if not rows:
        raise ValueError(
            f"Input CSV is empty: {path}"
        )

    required_columns = {
        "video_id",
        "seed_song_title",
        "transcript_clean",
        "transcript_quality",
        "lyric_language_verified",
    }

    missing_columns = sorted(
        required_columns - set(headers)
    )

    if missing_columns:
        raise ValueError(
            "Input CSV is missing required columns: "
            + ", ".join(missing_columns)
        )

    return rows, headers


def is_usable_row(
    row: dict[str, str],
) -> bool:
    """Return True when a transcript is ready for embedding analysis."""
    quality = normalize_label(
        row.get("transcript_quality")
    )

    language_verified = normalize_label(
        row.get("lyric_language_verified")
    )

    transcript = normalize_text(
        row.get("transcript_clean")
    )

    return (
        quality in USABLE_QUALITIES
        and language_verified == "yes"
        and bool(transcript)
    )


def select_rows(
    rows: list[dict[str, str]],
    ai_only: bool,
    limit: int,
) -> list[dict[str, str]]:
    """Filter rows according to transcript quality and optional AI status."""
    selected: list[dict[str, str]] = []

    for row in rows:
        if not is_usable_row(row):
            continue

        if ai_only:
            ai_related = normalize_label(
                row.get("ai_suno_related")
            )

            if ai_related != "yes":
                continue

        selected.append(row)

    if limit > 0:
        selected = selected[:limit]

    return selected


def get_device() -> torch.device:
    """Use Apple Silicon MPS when available, otherwise CPU."""
    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def mean_pooling(
    last_hidden_state: torch.Tensor,
    attention_mask: torch.Tensor,
) -> torch.Tensor:
    """Average token embeddings while ignoring padding tokens."""
    expanded_mask = (
        attention_mask
        .unsqueeze(-1)
        .expand(last_hidden_state.size())
        .float()
    )

    summed_embeddings = torch.sum(
        last_hidden_state * expanded_mask,
        dim=1,
    )

    token_counts = torch.clamp(
        expanded_mask.sum(dim=1),
        min=1e-9,
    )

    return summed_embeddings / token_counts


def calculate_embeddings(
    tokenizer: AutoTokenizer,
    model: AutoModel,
    texts: list[str],
    device: torch.device,
    batch_size: int = 4,
    max_length: int = 512,
) -> np.ndarray:
    """
    Encode text using AutoTokenizer and AutoModel.

    Longer text is truncated to max_length tokens.
    """
    all_embeddings: list[np.ndarray] = []

    model.eval()

    for start in range(
        0,
        len(texts),
        batch_size,
    ):
        batch_texts = texts[
            start : start + batch_size
        ]

        encoded = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=max_length,
            return_tensors="pt",
        )

        encoded = {
            key: value.to(device)
            for key, value in encoded.items()
        }

        with torch.no_grad():
            model_output = model(**encoded)

        pooled_embeddings = mean_pooling(
            last_hidden_state=(
                model_output.last_hidden_state
            ),
            attention_mask=encoded[
                "attention_mask"
            ],
        )

        normalized_embeddings = F.normalize(
            pooled_embeddings,
            p=2,
            dim=1,
        )

        all_embeddings.append(
            normalized_embeddings
            .cpu()
            .numpy()
            .astype(np.float32)
        )

    return np.vstack(all_embeddings)


def get_song_title(
    row: dict[str, str],
) -> str:
    """Return the best available song title field."""
    return (
        normalize_text(
            row.get("seed_song_title")
        )
        or normalize_text(
            row.get("candidate_title")
        )
        or normalize_text(
            row.get("song_title")
        )
        or "(untitled)"
    )


def build_result(
    row: dict[str, str],
    similarities: np.ndarray,
    theme_names: list[str],
    model_name: str,
) -> dict[str, str]:
    """Build one output row from theme similarity scores."""
    ranked_indices = np.argsort(
        similarities
    )[::-1]

    best_index = int(
        ranked_indices[0]
    )

    second_index = int(
        ranked_indices[1]
    )

    best_theme = theme_names[
        best_index
    ]

    second_theme = theme_names[
        second_index
    ]

    best_score = float(
        similarities[best_index]
    )

    second_score = float(
        similarities[second_index]
    )

    score_map = {
        theme_names[index]: float(
            similarities[index]
        )
        for index in range(
            len(theme_names)
        )
    }

    views = row.get(
        "view_count",
        "",
    )

    likes = row.get(
        "like_count",
        "",
    )

    comments = row.get(
        "comment_count",
        "",
    )

    return {
        "video_id": normalize_text(
            row.get("video_id")
        ),
        "artist_name": normalize_text(
            row.get("artist_name")
        ),
        "song_title": get_song_title(
            row
        ),
        "candidate_title": normalize_text(
            row.get("candidate_title")
        ),
        "youtube_url": normalize_text(
            row.get("youtube_url")
        ),
        "ai_suno_related": normalize_text(
            row.get("ai_suno_related")
        ),
        "channel_type": normalize_text(
            row.get("channel_type")
        ),
        "genre_style": normalize_text(
            row.get("genre_style")
        ),
        "transcript_quality": normalize_text(
            row.get("transcript_quality")
        ),
        "lyric_language_verified": normalize_text(
            row.get(
                "lyric_language_verified"
            )
        ),
        "transcript_language": normalize_text(
            row.get("transcript_language")
        ),
        "predicted_theme": best_theme,
        "similarity_score": (
            f"{best_score:.4f}"
        ),
        "second_best_theme": second_theme,
        "second_best_score": (
            f"{second_score:.4f}"
        ),
        "score_margin": (
            f"{best_score - second_score:.4f}"
        ),
        "romance_heartbreak_score": (
            f"{score_map['Romance / heartbreak']:.4f}"
        ),
        "hometown_nostalgia_score": (
            f"{score_map['Hometown / nostalgia']:.4f}"
        ),
        "local_food_culture_score": (
            f"{score_map['Local food / culture']:.4f}"
        ),
        "party_dance_score": (
            f"{score_map['Party / dance']:.4f}"
        ),
        "healing_relaxing_score": (
            f"{score_map['Healing / relaxing']:.4f}"
        ),
        "other_emerging_theme_score": (
            f"{score_map['Other / emerging theme']:.4f}"
        ),
        "view_count": normalize_text(
            views
        ),
        "like_count": normalize_text(
            likes
        ),
        "comment_count": normalize_text(
            comments
        ),
        "like_rate": safe_rate(
            likes,
            views,
        ),
        "comment_rate": safe_rate(
            comments,
            views,
        ),
        "transcript_clean": normalize_text(
            row.get("transcript_clean")
        ),
        "embedding_model": model_name,
    }


def write_results(
    path: Path,
    results: list[dict[str, str]],
) -> None:
    """Write embedding results to a UTF-8 CSV."""
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS,
            extrasaction="ignore",
        )

        writer.writeheader()
        writer.writerows(results)


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Run lyric-level theme embedding for "
            "reviewed Turkish YouTube transcripts."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help=(
            f"Input analysis-ready CSV. "
            f"Default: {DEFAULT_INPUT}"
        ),
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=(
            f"Output results CSV. "
            f"Default: {DEFAULT_OUTPUT}"
        ),
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=(
            f"Hugging Face model. "
            f"Default: {DEFAULT_MODEL}"
        ),
    )

    parser.add_argument(
        "--ai-only",
        action="store_true",
        help=(
            "Only analyze rows where "
            "ai_suno_related=yes."
        ),
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help=(
            "Maximum rows to analyze. "
            "Use 0 for all eligible rows."
        ),
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=4,
        help=(
            "Embedding batch size. "
            "Default: 4"
        ),
    )

    parser.add_argument(
        "--max-length",
        type=int,
        default=512,
        help=(
            "Maximum number of tokens per text. "
            "Longer text is truncated. "
            "Default: 512"
        ),
    )

    return parser.parse_args()


def validate_args(
    args: argparse.Namespace,
) -> None:
    """Validate numeric command-line arguments."""
    if args.limit < 0:
        raise ValueError(
            "--limit cannot be negative."
        )

    if args.batch_size <= 0:
        raise ValueError(
            "--batch-size must be greater than 0."
        )

    if args.max_length <= 0:
        raise ValueError(
            "--max-length must be greater than 0."
        )


def main() -> int:
    args = parse_args()

    try:
        validate_args(args)

        rows, _ = read_csv(
            args.input
        )

    except (
        FileNotFoundError,
        ValueError,
    ) as error:
        print(
            f"Error: {error}",
            file=sys.stderr,
            flush=True,
        )
        return 1

    selected_rows = select_rows(
        rows=rows,
        ai_only=args.ai_only,
        limit=args.limit,
    )

    print(
        f"Total input rows: {len(rows)}",
        flush=True,
    )

    print(
        "Usable lyric rows selected: "
        f"{len(selected_rows)}",
        flush=True,
    )

    if not selected_rows:
        print(
            "No eligible rows found. Check "
            "transcript_quality and "
            "lyric_language_verified values.",
            flush=True,
        )
        return 0

    device = get_device()

    print(
        f"Using device: {device}",
        flush=True,
    )

    print(
        f"Loading tokenizer: {args.model}",
        flush=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(
        args.model
    )

    print(
        f"Loading model: {args.model}",
        flush=True,
    )

    model = AutoModel.from_pretrained(
        args.model
    )

    model.to(device)

    theme_names = list(
        THEME_DESCRIPTIONS.keys()
    )

    theme_texts = list(
        THEME_DESCRIPTIONS.values()
    )

    print(
        "Encoding theme descriptions...",
        flush=True,
    )

    theme_embeddings = calculate_embeddings(
        tokenizer=tokenizer,
        model=model,
        texts=theme_texts,
        device=device,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )

    lyric_texts = [
        normalize_text(
            row.get("transcript_clean")
        )
        for row in selected_rows
    ]

    print(
        "Encoding lyrics...",
        flush=True,
    )

    lyric_embeddings = calculate_embeddings(
        tokenizer=tokenizer,
        model=model,
        texts=lyric_texts,
        device=device,
        batch_size=args.batch_size,
        max_length=args.max_length,
    )

    # Embeddings are normalized, so matrix multiplication
    # is equivalent to cosine similarity.
    similarity_matrix = (
        lyric_embeddings
        @ theme_embeddings.T
    )

    results: list[dict[str, str]] = []

    for row, similarities in zip(
        selected_rows,
        similarity_matrix,
        strict=True,
    ):
        result = build_result(
            row=row,
            similarities=similarities,
            theme_names=theme_names,
            model_name=args.model,
        )

        results.append(result)

        print(
            f"- {result['song_title']}\n"
            f"  predicted="
            f"{result['predicted_theme']}, "
            f"score="
            f"{result['similarity_score']}, "
            f"margin="
            f"{result['score_margin']}",
            flush=True,
        )

    write_results(
        path=args.output,
        results=results,
    )

    print(
        "\nLyric-level embedding complete.",
        flush=True,
    )

    print(
        f"Rows written: {len(results)}",
        flush=True,
    )

    print(
        f"Output: {args.output}",
        flush=True,
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(
        main()
    )