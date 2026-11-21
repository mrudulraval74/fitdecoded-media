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
| 2026-11-20 | A | 07:24 (actual IG time) | Women lifting bulky | 3 |
| 2026-11-20 | B | 13:26 (manual test run) | Dev Uthani Ekadashi greeting (festival) | not counted (manual test + festival; 2) |
| 2026-11-21 | A | 12:54 (actual IG time) | Rice vs roti | (pending; 1 at ~5.5 h, cached) |
| 2026-11-21 | B | 18:25 (actual IG time) | Tulsi Vivah greeting (festival) | not counted (festival) |

## Current settings
- Slot A: 12:52 (set 2026-11-20). 2026-11-21 run chose 15:22 for 2026-11-22 (explore: 09:22 and 15:22 have 0 posts, tie goes to next after 12:52; 15:22 is exactly 3 h before Slot B 18:22). update_trigger was blocked again (scheduled runs need owner approval), so the owner must apply it manually: CRON_TZ=Asia/Kolkata 22 15 * * *
- Slot B: 18:22 (trigger still unchanged). 2026-11-21 run chose 20:22 for 2026-11-22 (explore: Slot B candidates 18:22 / 20:22 both have 0 counted posts; tie goes to next after 18:22). 20:22 is >= 3 h after Slot A (12:52 now, or 15:22 if the owner applies it). update_trigger was blocked again (scheduled runs need owner approval), so the owner must apply it manually: CRON_TZ=Asia/Kolkata 22 20 * * *
