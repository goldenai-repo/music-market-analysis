# A/B Test Hypothesis Candidates

## Purpose

This note summarizes exploratory A/B test hypotheses derived from the current
14-song Turkish lyric embedding sample.

These observations are intended to guide experimental design rather than serve
as causal evidence.

## Preliminary Observation

In the current sample, songs with smaller top-two embedding score margins tend
to show relatively higher normalized engagement.

One possible interpretation is that lyrics containing two semantically related
themes produce more balanced embedding scores than lyrics dominated by a single
theme. This observation requires further validation.

---

## Candidate 1: Single-theme Lyrics vs. Related Dual-theme Lyrics

**Hypothesis**

Songs combining two semantically related lyrical themes may receive higher
normalized engagement than songs maintaining one dominant lyrical theme.

**A/B Design**

- **Group A:** One dominant lyrical theme (e.g., Romance / heartbreak)
- **Group B:** Two related lyrical themes (e.g., Romance / heartbreak + Healing / relaxing)

**Validation**

Use lyric-level embedding to verify that:

- Group A has a larger top-two embedding score margin.
- Group B has a smaller top-two embedding score margin.

**Priority:** Primary candidate.

---

## Candidate 2: Title–Lyric Alignment

**Hypothesis**

Songs whose titles and lyrics express the same dominant theme may exhibit
different engagement from songs whose lyrics introduce an additional related
theme.

**A/B Design**

- **Group A:** Title and lyrics express the same dominant theme.
- **Group B:** Title expresses one theme while the lyrics introduce an additional related theme.

**Validation**

Compare title-level and lyric-level embedding results.

**Priority:** Secondary candidate.

---

## Shared Controls

Keep the following approximately consistent across each A/B pair:

- Musical style
- Vocal type
- Tempo
- Song duration
- Production quality
- Release timing
- Cover artwork
- Title format

## Evaluation Metrics

Primary:
- Like rate
- Comment rate

Secondary:
- Views / streams

## Current Recommendation

Prioritize **Candidate 1 (Single-theme Lyrics vs. Related Dual-theme Lyrics)**,
as it is directly motivated by the current lyric-level embedding results and
fits the lyric-focused scope of this project.