import argparse

from youtube_transcript_api import YouTubeTranscriptApi


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("video_id")
    args = parser.parse_args()

    api = YouTubeTranscriptApi()
    transcript = api.fetch(
        args.video_id,
        languages=["tr", "en"],
    )

    print("Language:", transcript.language)
    print("Language code:", transcript.language_code)
    print("Generated:", transcript.is_generated)

    rows = transcript.to_raw_data()
    for row in rows[:5]:
        print(row)


if __name__ == "__main__":
    main()