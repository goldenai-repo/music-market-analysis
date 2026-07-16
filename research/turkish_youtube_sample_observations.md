# Turkish YouTube Sample Observations

## 1. Sample Overview
This exploratory sample includes 14 Turkish YouTube music videos across Suno-assisted, mainstream pop, dance-pop, rap, folk/traditional, and fusion styles.

## 2. Preliminary Observations

### Observation 1: Suno-assisted samples are useful for testing the tagging framework.
These samples have much lower view counts than mainstream songs, but they are useful for testing whether lyrics and title keywords can be tagged consistently.

### Observation 2: Mainstream pop/love ballads have high view counts.
Their engagement may also reflect artist popularity, channel/distribution effects, and video age, not only lyrics/title content. This suggests that channel type should be considered when interpreting engagement.

### Observation 3: Title keywords alone are not enough.
Several titles contain metaphors, place names, broad emotional phrases, or cultural references, so lyric context is needed for content classification.

### Observation 4: Comment-based engagement needs caution.
Some videos have limited or unusual comment data (e.g.TARKAN - Şımarık), so comment rate should be interpreted carefully.

## 3. Transcript Collection Update

- Integrated `youtube-transcript-api` and retrieved transcripts for 5 manually validated music videos.
- Four transcripts were in Turkish and one was in English.
- Three Turkish transcripts were usable with minor ASR noise; one was too short for reliable lyric-level analysis.
- English-language covers will be excluded from the Turkish lyric-analysis subset.

### Next Step

Expand transcript collection and continue manual quality review before lyric-level embedding analysis.