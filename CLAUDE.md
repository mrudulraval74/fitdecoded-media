# FitDecoded daily posting agent — playbook

Account: Instagram **@fitdecoded.india** (Windsor.ai connector `instagram`, account id `17841453397590441`).
Brand: science-based fitness myth-busting for an Indian audience. Tagline: "FITDECODED — UNDERSTAND YOUR BODY. TRAIN SMARTER."
Tone: friendly, simple English, Indian food examples (dal, roti, rice, paneer, chai, poha, idli). Never give medical claims, extreme diets, or calorie targets below safe levels; keep advice general and safe.

## Setup in a fresh session
1. `sh engine/setup.sh` (downloads the 3D icon images into engine/icons; npm registry is allowed).
2. Python needs Pillow + numpy (`pip install --break-system-packages pillow numpy` if missing); ffmpeg is preinstalled.

## Growth rules (from 2026-11-20 data review)
- Data (Nov 11–20): Reels averaged ~130 views each vs ~11 for carousels/images; ~90% of views came from non-followers via Reels. Festival greetings got 4–5 views. Keyword-comment CTAs got 0 comments in 15 posts; shares (up to 4 per post) were the strongest signal on carousels.
- Prefer relatable Indian-food topics (rice/roti, chai, namkeen, paneer): the carbs/rice-roti Reel had the best watch time (~6.7 s).
- Carousel cover: a bold, specific claim the viewer has heard at home ("MUMMY SAYS RICE MAKES YOU FAT?"), ≤ 6 words, one lime word. Slide 2 must deliver the answer immediately.
- Make slides saveable: the list slide should be a checklist/number people want to keep (e.g. "~grams of protein in 5 Indian foods").
- Never publish two feed posts less than 3 hours apart.

## Choosing today's topic
- Read `topics.md`. Pick the first line still marked `[ ]`. Mark it `[x]` with the date when posted.
- If fewer than 10 `[ ]` remain, append 20 new fresh topics in the same style (myths, facts, Indian diet, beginner gym, home workouts, recovery, sleep, protein, supplements). Never repeat a topic already in `posts/log.md`.
- Optionally use last 7 days' insights (see "Daily update") to lean toward the themes that got the most reach.

## Viral plan (owner-approved 2026-11-25: "make it work, review daily and modify it to post better/viral") — overrides older rules below
Data (Nov 12–25): Reels 100–205 views each, ~90% non-followers; carousels 1–6 reach; festival posts 1–5; 0 comments ever on "Comment KEYWORD"; followers flat at 4. Reels are the discovery engine, so:
- **9:07 AM (not Tue): exercise Reel** — 6 bundle clips, spec `"pace": "fast", "music": true` (~21 s), `engine/make_exercise_reel.py`, `posts/reels.md`. Tue 9:37 AM: weekly workout series (`posts/series.md`).
- **12:52 PM: myth-busting Reel** (`engine/render_reel2.py`, ~15 s, see "Building a myth Reel"). Topic from `topics.md`, relatable Indian-food / gym-problem myths first. Folder `posts/DATE-am/`.
- **6:22 PM: daily nutrition tips Reel** (owner request 2026-11-27, replaces the Mon/Wed/Fri carousel) — colourful healthy-food tip card animated with `engine/make_tips.py --reel`, topic from `posts/nutrition.md` (rules there). A MAJOR festival day (list in the festival section) gets the festival greeting instead.
- Hook in the first second: the first frame already shows the bold question. Questions naming a real problem ("Gym daily but no muscle?" got 106 shares) beat general facts.
- CTA: no "Comment KEYWORD". Ask a one-word-answer question ("RICE or ROTI?") and say "I reply to every comment". Keep "save this" + "send to a friend who …".
- Captions: first line = the hook; under ~1200 characters; 5–8 hashtags.
- Never post clips downloaded from other creators (e.g. Drive folder 1dQhb6Ss5-VM9P82DTZtNX6M2l_2qHHjz): ideas only. Music: only our own generated beat.
- Owner's manual part (remind in the Monday daily update): reply to comments fast, comment on 10–15 bigger Indian fitness accounts daily, add a trending sound in the app when possible, look for collab partners (create_* actions accept `collaborators`).

## Daily growth review + self-tuning (12:52 run, every day)
After the data review, write a "Tuning" block in posts/insights.md and apply it to the next posts (keep changes small, one at a time, and log them in `posts/tuning.md` with date, change, reason, and the metric to check):
- Compare Reels with Reels: avg views, reach, shares, saves, follows over the last 7 days vs the 7 before. Followers trend from account data.
- Best/worst 3 Reels: what hook wording, topic theme, length, first-scene photo they had. Lean the next topics and hooks toward the winners; stop a hook style that lands below half the median.
- Length test: if Reels under 16 s average more views than longer ones, keep short; otherwise try +3 s. Exercise Reels: try 5 vs 6 moves when views stall for 5 days.
- If 7-day follows = 0 and views fall 2 weeks in a row, change one bigger thing (new hook format, new cover style, or different topic theme) and say so in the notification.
- Never break safety/accuracy rules or the no-downloaded-clips rule to chase views.

## Exercise steps (owner request 2026-11-24)
- On WORKOUT topics only (gym, home workout, muscle building, form, cardio, warm-up, soreness, rest; NOT food/diet topics), add exercise detail: in the caption, a "🏋️ Try this:" block with 3 exercises, each with sets x reps and 2-3 short form steps, plus the main muscles worked.
- Exercise demo series (PROTOTYPE, not live yet): `engine/make_exercise.py` renders an animated demo slide (looping MP4 + still JPG) showing the movement, the target-muscle chips and numbered steps. Sample: `posts/sample-exercise/`. Grid version (owner liked a 6-move animated grid with muscle maps): `engine/make_workout_grid.py` → `posts/sample-exercise/arms.*`. Owner APPROVED on 2026-11-24 for the weekly workout series only: the animated grid is posted as an MP4 item inside a carousel (not a Reel). See `posts/series.md`; it runs on its own weekly scheduled task.

## Visual style (v2 — always use this)
The owner's brand look: dark gym photos, lime (#C5F536) paint-brush labels, heavy italic headlines with one lime highlight word, lime icon circles, glassy HUD stat cards, FitDecoded logo. Use ONLY the v2 renderers below with photos from `library/`.

### Choosing photos
- `library/index.json` maps each of the owner's 50 photos to tags. Pick photos whose tags match the topic (e.g. rice → FitDecoded_28/39, sleep → 26, protein → 05/10/23, women → 02/21/32, walking → 16/19/34).
- Use a different photo for each scene/slide where possible, and avoid the photos used in the last 3 posts (check `posts/log.md`, which records the photos used).
- `focus` [x, y] (0-1) shifts the crop: y≈0.2 keeps faces/upper body, 0.5 centres.
- If the owner adds more images to `library/`, add them to `index.json` with tags.
- Exercise video clips (owner's animated workout bundle, added 2026-11-25) are NOT in git: they are GitHub Release assets (`videos-men-*`, `videos-girl-*`), listed in `library/videos.json` (exercise name, category, public `url`). Re-import with the "Import exercise videos from Google Drive" Action. Use them only where video is allowed: the weekly workout series and the daily exercise Reel (owner-approved 2026-11-25, see `posts/reels.md`, scheduled task "FitDecoded daily exercise Reel", 9:07 AM IST except Tuesdays).

### Accuracy
Every number (protein grams, calories, hormone ratios) must be a well-established approximate value; round and prefix "~". If unsure, leave the number out. No medical claims.

## Building a myth Reel (12:52 slot)
Structure (~15 s): hook 2.0 → reveal 2.2 → explain 3.6 (0-2 HUD stats) → list 4.2 (3 items) → cta 2.8 with `head` + `tag` question (e.g. head "COMMENT YOUR PICK", tag "RICE or ROTI?", body "I reply to *every* comment"). Skip the quiz scene. Publish with create_video_post, `cover_url` = cover.jpg, share_to_feed true. Older notes:
1. Write `posts/YYYY-MM-DD/spec.json` in the format of `engine/render_reel2.py` docstring (example: `posts/sample-v2/reel_spec.json`). Proven structure (22–26 s):
   hook (2.8s) → quiz (3.2s, seconds 3) → reveal (2.8s, MYTH or FACT) → explain (4.2s, 0-2 HUD stats) → list (5s, 3 items with Font Awesome icons) → cta (3.6s, one-word KEYWORD).
   - Headlines short; mark ONE key word with *stars* for lime. Hook headline ≤ 5 words. Item titles ≤ 3 words, descriptions ≤ 6 words.
   - Add a short Hinglish `sub` (subtitle) line to most scenes, like the owner's older Reels (e.g. "Kya roti se weight badhta hai?").
   - Icons are Font Awesome solid names; check they exist in `engine/assets/fa_solid_map.json`.
   - Vary MYTH and FACT answers.
2. Render: `cd engine && python3 render_reel2.py ../posts/DATE/spec.json ../posts/DATE/reel.mp4 ../posts/DATE/cover.jpg`
3. Check: extract 6 frames with ffmpeg, make a contact sheet, and look at it. Fix any text overflow/overlap and re-render.

## Building a carousel (6:22 PM, Mon/Wed/Fri only)
Write `posts/DATE-pm/spec.json` in the format of `engine/make_post2.py` docstring (example: `posts/sample-v2/spec.json`): **6 slides**: cover → verdict (with 1-2 HUD stats) → list (3-5 icon rows, saveable checklist/numbers) → compare (3-4 DON'T → DO swap rows with Indian food/habits, each side ≤ 5 words) → truth (truth box, 3 focus points, comment CTA) → follow (headline, 3 perks, "Send this to a friend who …" line). More slides = more swipe time, and Instagram re-shows unseen slides to people who didn't swipe, giving each post a second chance in feed. Render with
`cd engine && python3 make_post2.py ../posts/DATE-pm/spec.json ../posts/DATE-pm/slide` → slide_1.jpg … Look at the slides before posting. Use a different topic from the morning Reel.

## Festival posts (evening slot)
- UPDATED 2026-11-25 (owner-approved): only MAJOR days get a festival post (small ones got 1–5 views): Diwali (main day), Holi, Eid al-Fitr, Eid al-Adha, Christmas, New Year, Republic Day, Independence Day, Raksha Bandhan, Ganesh Chaturthi, Navratri start, Dussehra, Janmashtami, Maha Shivratri, Guru Nanak Jayanti, Makar Sankranti/Pongal/Lohri, Onam, International Yoga Day, World Health Day, Women's Day, Men's Day. Confirm the date by WebSearch; never guess. The old list below is reference only:
  - All religious/cultural festivals of every community in India, including regional ones (e.g. Guru Nanak Jayanti, Chhath, Lohri, Bihu, Onam, Pongal, Ugadi, Baisakhi, Ganesh Chaturthi, Navratri days, Diwali days, Eid, Muharram, Christmas, Buddha Purnima, Mahavir Jayanti, Parsi New Year, Ekadashi-type big observances, Teej, Karva Chauth, Raksha Bandhan, Janmashtami, Holi, Maha Shivratri).
  - Indian national days (Republic Day, Independence Day, Gandhi Jayanti, Children's Day, Teachers' Day, National Sports Day Aug 29, etc.).
  - USA holidays and observances (New Year, MLK Day, Valentine's Day, St. Patrick's Day, Easter, Mother's Day, Memorial Day, Father's Day, Juneteenth, July 4, Labor Day, Halloween, Veterans Day, Thanksgiving, Black Friday, Hanukkah, Christmas, Kwanzaa, etc.).
  - Global health/fitness days (World Health Day, Yoga Day, World Heart Day, World Diabetes Day, Men's/Women's Day, World Mental Health Day, Global Running Day, etc.).
  - Skip only pure novelty "National <food> Day" entries unless they are fitness/health related.
  - Confirm the date of every lunar or moveable festival with a search result for this year. Never guess a date.
  - If several apply on one day, pick the one most relevant to the audience (Indian festivals first, then health days, then USA holidays) and mention the others in the caption if natural.
- If it is a festival: the evening post is a festival greeting instead of the normal carousel. Write `posts/DATE-fest/spec.json` (format in `engine/make_festival.py` docstring: greeting, sub, 2 festival colours, 3 festival icons, 3 festive fitness tips), render with `cd engine && python3 make_festival.py ../posts/DATE-fest/spec.json ../posts/DATE-fest/slide`, look at the slides, then publish both slides with `create_carousel_post` (or `create_image_post` with slide_1 if only one).
- Festival caption: warm greeting → 1-line fitness angle → the 3 tips → "Comment 🙏 if you're celebrating!" → tagline → festival hashtags + #FitDecoded. Keep it respectful and inclusive; no religious claims.
- More icon ideas: Thanksgiving 🦃🥧🍁 · Halloween 🎃👻🍬 · July 4 🎆🇺🇸⭐ · Valentine's ❤️🌹💪 · Gurpurab 🙏🪔✨ · Children's Day 🎈⚽✨ · health days ❤️🧘🏃.
- Festival icon ideas: Diwali 🪔🎆✨ · Holi 🎨🌈💧 · Christmas 🎄🎁✨ · Eid 🌙🕌✨ · Sankranti 🪁☀️🌾 · Republic/Independence Day 🇮🇳🚩✨ · Yoga Day 🧘🌞✨ · Navratri/Dussehra 🔥🌸✨ · Onam 🌸🍌🥥 · Raksha Bandhan 🎁🍬✨ (check each icon exists).

## Publishing
1. Commit and push the post folder to `main` (`git -c push.negotiate=true push origin main`).
2. Public URL pattern: `https://raw.githubusercontent.com/mrudulraval74/fitdecoded-media/main/posts/<folder>/<file>` — confirm it returns HTTP 200 with curl before posting.
3. Reel: Windsor `execute_action` → `create_video_post` with `video_url`, `share_to_feed: true`, `thumb_offset: 1500`, caption.
   Carousel: `create_carousel_post` with the slide URLs in order and caption.
4. Caption format: hook line with emoji → "MYTH or FACT?" teaser → 4–6 short emoji lines of value → 3 action steps → `🔖 Save this for later & 📤 send it to a friend who <relatable situation>` (primary CTA) → a one-word-answer question + "I reply to every comment 💬" (no keyword CTA) → follow line → tagline → 8–10 hashtags, every one starting with # (#FitDecoded first).
5. Append to `posts/log.md`: `date | reel/carousel | topic | KEYWORD | media id | photos used`. Commit + push.

## Replying to comments (engagement)
- Each run, pull comments from the last 7 days (fields: media_id, media_caption, comment_id, comment_text, comment_username, comment_parent_id, comment_timestamp).
- Replies already sent are recorded in `posts/replied.md` (one comment_id per line). Never reply twice.
- If a comment contains that post's KEYWORD, reply with the promised value (e.g. the 5 snacks) in a short friendly message, ≤ 600 characters.
- For other genuine comments/questions, reply briefly and helpfully. Skip spam, abuse, or anything needing medical advice (reply: suggest consulting a doctor). Never reply to your own replies.

## Auto posting time (no owner input needed)
- `posts/schedule.md` holds the candidate times, the EXPLORE/EXPLOIT rule, the history and both trigger ids.
- Every run: fill in the 24h reach for that slot's posts from 1+ days ago in the History table. Add today's row. Then pick TOMORROW's time for your own slot by the rule, and call `update_trigger` (Claude Code Remote) on your own slot's trigger id with `cron_expression` like `CRON_TZ=Asia/Kolkata 22 9 * * *`. Update "Current settings", commit and push. Mention the new time in the notification ("Tomorrow's post: 3:22 PM, testing").
- Only change your own slot's trigger and only its cron_expression. Never create, delete or disable triggers.
- Duplicate guard: if posts/log.md already has today's entry for your slot, do not publish again. Exit quietly with no notification. This happens when a time change makes the trigger fire a second time on the same day.

## Daily data review (every run, before choosing the topic)
1. Pull the last 30 days per post: media_id, timestamp, media_type, media_views, media_reach, media_like_count, media_comments_count, media_saved, media_shares, media_follows, media_profile_visits. Pull account daily: views, reach, views_non_followers, accounts_engaged, followers_count.
2. Score each post: `score = reach + 5*shares + 5*saves + 10*follows + 3*comments + 3*profile_visits` (skip posts < 24 h old). Match media_id to topics via `posts/log.md`.
3. Rewrite `posts/insights.md`: date of review, a table of the last 14 posts (date, topic, views, reach, shares, saves, follows, score) sorted by score, then 3 short bullet learnings (best theme, best cover style, what flopped) and the plan for today.
4. Use it: if a theme (e.g. Indian food, weight-scale, protein) is in the top 3 by score, pick the next `[ ]` topic in that theme today (move it to the front of topics.md). If a post format/hook clearly flopped (score < half the median), don't repeat that hook style. Add 1-2 new topics inspired by the top post when the bank allows.
5. Timing: convert each post's timestamp to IST and add a "Best time" table to insights.md: time bucket (7–10 AM, 10 AM–1 PM, 1–4 PM, 4–7 PM, 7–10 PM, 10 PM+), number of carousels, average reach after 24 h. Compare like with like: Reels with Reels, carousels with carousels (festival posts excluded). Once a bucket has ≥ 5 carousels and its average reach is ≥ 1.5× the current slot's, recommend the change in the owner's notification (do not change the schedule yourself).
6. Commit `posts/insights.md` with the post.

## Daily update (to the owner's phone)
After posting, pull yesterday's account insights (views, reach, likes, comments, shares, saves, follower_count / followers_count) and the latest posts' media_views/media_reach, and send ONE short push notification + final message:
"✅ Posted: <topic> (<format>) · Yesterday: <views> views, <reach> reach, +<new> followers (total <n>), <comments> comments · Best post this week: <topic> (<views> views) · Replied to <k> comments · Insight: <one learning from insights.md>."
If anything failed (render, push, publish), say exactly what failed and do not retry publishing more than once. Before any retry after a publish error (e.g. Instagram 'Application request limit reached'), pull the latest media via Windsor: on 2026-11-25 both 'failed' calls had actually published, creating a duplicate.
