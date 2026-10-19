# Progress

## Checklist
- [x] Phase 0 setup
- [x] Phase 1 models/config
- [x] Phase 2 net/normalize
- [x] Phase 3 sources
- [x] Phase 4 db
- [x] Phase 5 filters
- [x] Phase 6 digest
- [x] Phase 7 notifiers
- [x] Phase 8 pipeline/cli
- [x] Phase 9 smoke test
- [ ] Phase 10 scheduling
- [ ] Phase 11 LLM (optional)
- [ ] Phase 12 README/final

## Latest command output
```
$ python -m oppwatch run --dry-run
2026-10-19 21:13:21,082 INFO RSS source 'reddit_internships': fetched 25 items
2026-10-19 21:13:22,495 ERROR source reddit_hackathons failed: 429 Client Error: Too Many Requests for url: https://www.reddit.com/r/hackathons/new/.rss
Weekly Opportunities (2026-10-19)
New this week: 9

INTERNSHIPS (9)
1. Final-year Data Science Student from a Tier-3 College | Seeking Remote ML/AI Internship | deadline: n/a
   https://www.reddit.com/r/internships/comments/1x9of85/finalyear_data_science_student_from_a_tier3/
2. Am I wrong for thinking my company is expecting way too much from an intern? | deadline: n/a
   https://www.reddit.com/r/internships/comments/1x9q91n/am_i_wrong_for_thinking_my_company_is_expecting/
3. Cap one Business Analyst Summer 2027 vs JPMC Data and AI Summer 2027 | deadline: n/a
   https://www.reddit.com/r/internships/comments/1x982xh/cap_one_business_analyst_summer_2027_vs_jpmc_data/
...
2026-10-19 21:13:22,505 INFO Dry run complete
2026-10-19 21:13:22,505 INFO Run completed: {'sources_ok': 1, 'sources_failed': 1, 'fetched': 25, 'kept': 9, 'new': 9, 'sent': False}

$ python -m oppwatch run
2026-10-19 21:13:46,088 INFO nothing new
```

## QUESTIONS FOR USER
- Please open each url in config/sources.yaml in a browser and set enabled: true only for sources that work.

## BLOCKED
(none)
