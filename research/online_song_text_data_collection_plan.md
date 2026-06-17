# Online Song Text Data Collection Plan

## Goal

Define the data fields needed to support future NLP-based text extraction, building on the current manual tagging framework.

---

## Required Data Fields

| Field | Purpose |
|---|---|
| Song Title | Title analysis |
| Lyrics | Theme extraction and content classification |
| Language / Market | Market-level scope |
| Genre / Style | Control variable |
| Released / Online-Generated Status | Confirm analysis sample |
| Platform Link | Match with engagement data |
| Views / Streams | Performance metric |
| Likes | Engagement metric |
| Comments | Engagement metric |
| Release / Generated Date | Timing control |
| Data Source | Track data origin |

---

## NLP Extension

Once song titles and lyrics are available, the text can be processed through tokenization, embedding, and classification, then mapped to broader content categories such as romance, hometown/nostalgia, and local food/culture.

---

## Feasibility Questions

- Are lyrics available for released / online-generated Suno songs?
- Can each song be matched with engagement metrics?
- Is there enough online song data to support Turkish as the first market-level case study?
- If structured data access is unavailable, can a small online song sample be collected manually?