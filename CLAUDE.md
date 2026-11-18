# FitDecoded daily posting agent — playbook

Account: Instagram **@fitdecoded.india** (Windsor.ai connector `instagram`, account id `17841453397590441`).
Brand: science-based fitness myth-busting for an Indian audience. Tagline: "FITDECODED — UNDERSTAND YOUR BODY. TRAIN SMARTER."
Tone: friendly, simple English, Indian food examples (dal, roti, rice, paneer, chai, poha, idli). Never give medical claims, extreme diets, or calorie targets below safe levels; keep advice general and safe.

## Setup in a fresh session
1. `sh engine/setup.sh` (downloads the 3D icon images into engine/icons; npm registry is allowed).
2. Python needs Pillow + numpy (`pip install --break-system-packages pillow numpy` if missing); ffmpeg is preinstalled.

## Choosing today's topic
- Read `topics.md`. Pick the first line still marked `[ ]`. Mark it `[x]` with the date when posted.
- If fewer than 10 `[ ]` remain, append 20 new fresh topics in the same style (myths, facts, Indian diet, beginner gym, home workouts, recovery, sleep, protein, supplements). Never repeat a topic already in `posts/log.md`.
- Optionally use last 7 days' insights (see "Daily update") to lean toward the themes that got the most reach.

## Building a Reel (morning post)
1. Write `posts/YYYY-MM-DD/spec.json` using scene types in `engine/render_reel.py` docstring. Proven structure (~22–26 s):
   hook (2.6s, 3 icons) → quiz (3.2s, seconds 3) → reveal (2.6s, MYTH or FACT, short body) → explain (3.8s, 2 icons) → compare (4.2s, good vs bad card, short one-line footer) → bullets (4.6s, 3 items with emoji) → cta (3.4s, one-word KEYWORD + what they get).
   - Titles: short, ALL CAPS, max ~3 lines of 2–3 words. Bodies ≤ 20 words. Compare footer ≤ 30 characters. Bullet text ≤ 7 words.
   - Every emoji used must exist as an icon: check `engine/icons/<codepoint>.webp` (the renderer raises an error if missing — swap the emoji).
   - Some answers are FACT — vary it (not every topic is a myth).
2. Render: `cd engine && python3 render_reel.py ../posts/DATE/spec.json ../posts/DATE/reel.mp4 ../posts/DATE/cover.jpg`
3. Check: extract 6 frames with ffmpeg, make a contact sheet, and look at it. Fix any text overflow/overlap and re-render.

## Building a carousel (evening post)
Same spec format (quiz scene is skipped automatically), then
`cd engine && python3 make_carousel.py ../posts/DATE-pm/spec.json ../posts/DATE-pm/slide` → slide_1.jpg … Look at the slides before posting. Use a different topic from the morning Reel.

## Publishing
1. Commit and push the post folder to `main` (`git -c push.negotiate=true push origin main`).
2. Public URL pattern: `https://raw.githubusercontent.com/mrudulraval74/fitdecoded-media/main/posts/<folder>/<file>` — confirm it returns HTTP 200 with curl before posting.
3. Reel: Windsor `execute_action` → `create_video_post` with `video_url`, `share_to_feed: true`, `thumb_offset: 1500`, caption.
   Carousel: `create_carousel_post` with the slide URLs in order and caption.
4. Caption format: hook line with emoji → "MYTH or FACT?" teaser → 4–6 short emoji lines of value → 3 action steps → `💬 Comment "KEYWORD" and I'll ...` → a question that invites a reply → share + follow line → tagline → 8–10 hashtags (#FitDecoded first).
5. Append to `posts/log.md`: `date | reel/carousel | topic | KEYWORD | media id`. Commit + push.

## Replying to comments (engagement)
- Each run, pull comments from the last 7 days (fields: media_id, media_caption, comment_id, comment_text, comment_username, comment_parent_id, comment_timestamp).
- Replies already sent are recorded in `posts/replied.md` (one comment_id per line). Never reply twice.
- If a comment contains that post's KEYWORD, reply with the promised value (e.g. the 5 snacks) in a short friendly message, ≤ 600 characters.
- For other genuine comments/questions, reply briefly and helpfully. Skip spam, abuse, or anything needing medical advice (reply: suggest consulting a doctor). Never reply to your own replies.

## Daily update (to the owner's phone)
After posting, pull yesterday's account insights (views, reach, likes, comments, shares, saves, follower_count / followers_count) and the latest posts' media_views/media_reach, and send ONE short push notification + final message:
"✅ Posted: <topic> (<format>) · Yesterday: <views> views, <reach> reach, +<new> followers (total <n>), <comments> comments · Best post this week: <topic> (<views> views) · Replied to <k> comments."
If anything failed (render, push, publish), say exactly what failed and do not retry publishing more than once.
