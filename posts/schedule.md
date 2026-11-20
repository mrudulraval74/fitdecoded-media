# Auto posting-time schedule (maintained by the daily runs)

Slot A trigger: trig_0143j67DfjLFzx5qt1q9BBCK ("FitDecoded midday image post")
Slot B trigger: trig_01RCAzmrKUwuJ4ggixMekoKu ("FitDecoded evening image / festival post")

Candidate times (IST):
- Slot A: 09:22, 12:52, 15:22
- Slot B: 18:22 (unchanged). 2026-11-20 run chose 20:22 for 2026-11-21 (explore: all Slot B candidates have 0 counted posts, next after 18:22), but the update_trigger call was blocked because a scheduled run needs owner approval for it. Owner must apply manually.

Phase: EXPLORE (started 2026-11-20)

## Rule
- EXPLORE: each run sets its own slot's time for TOMORROW to the candidate with the fewest posts so far (ties: next in list after today's). Ends when every candidate in that slot has >= 4 posts.
- EXPLOIT: use the candidate with the highest average 24-hour reach. Every 7th day, test the runner-up once.
- Re-check weekly: if another candidate beats the current best by >= 1.3x over the last 14 days, switch.
- Slot B festival posts are not counted (they always get low reach).
- Always keep Slot B at least 3 hours after Slot A.

## History
| Date | Slot | Time (IST) | Topic | 24h reach |
|---|---|---|---|---|
| 2026-11-19 | A | 07:22 | Veg diet muscle | 6 |
| 2026-11-20 | A | 07:24 (actual IG time) | Women lifting bulky | (pending; 2 at ~6 h) |
| 2026-11-20 | B | 13:26 (manual test run) | Dev Uthani Ekadashi greeting (festival) | not counted (manual test + festival) |

## Current settings
- Slot A: 12:52 (set 2026-11-20, first explore test)
- Slot B: 18:22 (unchanged). 2026-11-20 run chose 20:22 for 2026-11-21 (explore: all Slot B candidates have 0 counted posts, next after 18:22), but the update_trigger call was blocked because a scheduled run needs owner approval for it. Owner must apply manually.
