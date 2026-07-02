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

# Small title-level test sample from embedding_mini_test_plan.md
# Lyric excerpts can be added later to test whether lyrics improve theme classification
songs = [
    {
        "title": "Gül Rengi",
        "text": "Gül Rengi",
        "manual_tag": "Romance / heartbreak",
    },
    {
        "title": "Üsküdar'a Gider İken",
        "text": "Üsküdar'a Gider İken",
        "manual_tag": "Hometown / nostalgia or Local food / culture",
    },
    {
        "title": "İmkansızım",
        "text": "İmkansızım",
        "manual_tag": "Romance / heartbreak or Other / emerging theme",
    },
    {
        "title": "Gesi Bağları",
        "text": "Gesi Bağları",
        "manual_tag": "Hometown / nostalgia or Local food / culture",
    },
]

print("Loading embedding model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
print("Model loaded.")
label_embeddings = model.encode(theme_labels, convert_to_tensor=True)

print("Embedding Similarity Test Results")
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