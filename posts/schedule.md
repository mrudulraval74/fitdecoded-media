# Auto posting-time schedule (maintained by the daily runs)

Slot A trigger: trig_0143j67DfjLFzx5qt1q9BBCK ("FitDecoded midday image post")
Slot B trigger: trig_01RCAzmrKUwuJ4ggixMekoKu ("FitDecoded evening image / festival post")

Candidate times (IST):
- Slot A: 09:22, 12:52, 15:22
- Slot B: 18:22 (trigger unchanged). Counted Slot B posts so far: 0 (every Slot B post has been a festival greeting). 2026-11-23 run again chose 20:22 for 2026-11-24 (explore: no counted posts at any time, next after 18:22). update_trigger blocked again (scheduled runs need owner approval); owner can apply manually: CRON_TZ=Asia/Kolkata 22 20 * * *. Must stay >= 3 h after Slot A (12:52 now, 15:22 if applied).
