print("Script started")
import csv
from pathlib import Path

from sentence_transformers import SentenceTransformer, util

# Candidate theme labels from content_category_schema.csv
theme_labels = [
    "Romance / heartbreak",
    "Hometown / nostalgia",
    "Local food / culture",
    "Party / dance",
    "Healing / relaxing",
    "Other / emerging theme",
]

# Lyric excerpt-level input sample
input_path = Path("data/processed/lyric_excerpt_sample.csv")

songs = []

with input_path.open("r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        songs.append(
            {
                "title": row["Song Title"],
                "text": row["Lyric Excerpt"],
                "manual_tag": row["Manual Tag"],
            }
        )

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
print("Model loaded.")

label_embeddings = model.encode(theme_labels, convert_to_tensor=True)

print("Lyric Excerpt-Level Embedding Similarity Test Results")
print("-" * 80)

for song in songs:
    song_embedding = model.encode(song["text"], convert_to_tensor=True)
    similarities = util.cos_sim(song_embedding, label_embeddings)[0]

    best_idx = similarities.argmax().item()
    best_label = theme_labels[best_idx]
    best_score = similarities[best_idx].item()

    print(f"Song: {song['title']}")
    print(f"Manual tag: {song['manual_tag']}")
    print(f"Top embedding match: {best_label}")
    print(f"Similarity score: {best_score:.4f}")
    print("-" * 80)