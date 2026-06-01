import json
import time
from http.client import IncompleteRead
from urllib.request import Request, urlopen


URL = "https://rss.applemarketingtools.com/api/v2/us/music/most-played/100/songs.json"
OUTPUT_FILE = "itunes_us_top100.md"


def get_label(obj, key, default=""):
    value = obj.get(key, {})
    if isinstance(value, dict):
        return value.get("label", default)
    return default


def get_attr(obj, key, attr, default=""):
    value = obj.get(key, {})
    if isinstance(value, dict):
        return value.get("attributes", {}).get(attr, default)
    return default


def clean_md(text):
    return str(text or "").replace("|", "\\|").replace("\n", " ").strip()


def get_links(entry):
    preview_url = ""
    itunes_url = ""

    links = entry.get("link", [])
    if isinstance(links, dict):
        links = [links]

    for link in links:
        attrs = link.get("attributes", {})
        href = attrs.get("href", "")
        link_type = attrs.get("type", "")

        if "audio" in link_type:
            preview_url = href
        elif "itunes.apple.com" in href:
            itunes_url = href

    return preview_url, itunes_url


def build_rows(entries):
    rows = []

    for rank, entry in enumerate(entries, start=1):
        images = entry.get("im:image", [])
        artwork_url = images[-1].get("label", "") if images else ""
        preview_url, itunes_url = get_links(entry)

        rows.append(
            {
                "rank": rank,
                "song": get_label(entry, "im:name"),
                "artist": get_label(entry, "im:artist"),
                "album": get_label(entry.get("im:collection", {}), "im:name"),
                "genre": get_attr(entry, "category", "label"),
                "release_date": get_label(entry, "im:releaseDate"),
                "itunes_id": get_attr(entry, "id", "im:id"),
                "price": get_attr(entry, "im:price", "amount"),
                "currency": get_attr(entry, "im:price", "currency"),
                "artwork": artwork_url,
                "preview": preview_url,
                "itunes_link": itunes_url,
            }
        )

    return rows


def build_rows_from_results(results):
    rows = []

    for rank, item in enumerate(results, start=1):
        genres = item.get("genres", [])
        genre = ", ".join(genre.get("name", "") for genre in genres if genre.get("name"))

        rows.append(
            {
                "rank": rank,
                "song": item.get("name", ""),
                "artist": item.get("artistName", ""),
                "album": "",
                "genre": genre,
                "release_date": item.get("releaseDate", ""),
                "itunes_id": item.get("id", ""),
                "price": "",
                "currency": "",
                "artwork": item.get("artworkUrl100", ""),
                "preview": "",
                "itunes_link": item.get("url", ""),
            }
        )

    return rows


def write_markdown(rows):
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# iTunes US Top 100 Songs\n\n")
        f.write("Data source: Apple RSS / Marketing Tools, United States\n\n")
        f.write(
            "| Rank | Song | Artist | Genre | Release Date | Apple ID | Artwork | Apple Link |\n"
        )
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")

        for row in rows:
            artwork = f"[Cover]({row['artwork']})" if row["artwork"] else ""
            preview = f"[Preview]({row['preview']})" if row["preview"] else ""
            itunes_link = f"[iTunes]({row['itunes_link']})" if row["itunes_link"] else ""

            f.write(
                f"| {row['rank']} "
                f"| {clean_md(row['song'])} "
                f"| {clean_md(row['artist'])} "
                f"| {clean_md(row['genre'])} "
                f"| {clean_md(row['release_date'])} "
                f"| {clean_md(row['itunes_id'])} "
                f"| {artwork} "
                f"| {itunes_link} |\n"
            )


def main():
    data = None
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Encoding": "identity",
        "Connection": "close",
    }

    for attempt in range(1, 4):
        request = Request(URL, headers=headers)
        with urlopen(request, timeout=30) as response:
            try:
                raw_data = response.read()
            except IncompleteRead as exc:
                raw_data = exc.partial

        try:
            data = json.loads(raw_data.decode("utf-8"))
            break
        except json.JSONDecodeError:
            if attempt == 3:
                raise
            time.sleep(2)

    feed = data.get("feed", {})
    if "results" in feed:
        rows = build_rows_from_results(feed.get("results", []))
    else:
        rows = build_rows(feed.get("entry", []))

    if not rows:
        raise RuntimeError("No songs found in the iTunes response.")

    write_markdown(rows)
    print(f"Saved {len(rows)} songs to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
