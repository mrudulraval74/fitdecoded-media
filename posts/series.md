# Animated workout series (weekly, owner-approved 2026-11-24)

Format: 1 carousel = item 1 animated grid MP4 (engine/make_workout_grid.py, 6 moves, muscle maps, sets x reps)
+ 4 still slides (engine/make_post2.py with "page_offset": 1): HOW TO DO IT moves 1-3, HOW TO DO IT moves 4-6, truth, follow.
Example: posts/2026-11-24-workout/ (grid.json + spec.json). Owner OK'd video inside a carousel for this series only (still no Reels).

## Rotation (take the first [ ])
- [x] 2026-11-24 #1 Arms: 6 dumbbell moves (biceps, triceps, forearms) — ARMS
- [ ] Legs: squat, lunge, glute bridge, step-up, calf raise, wall sit — LEGS
- [ ] Chest: push-up, incline push-up, dumbbell floor press, dumbbell fly, knee push-up, chest squeeze press — CHEST
- [ ] Back: dumbbell row, superman, reverse fly, band pull-apart, bird dog, good morning (bodyweight) — BACK
- [ ] Shoulders: overhead press, lateral raise, front raise, pike push-up, arm circles, shrug — SHOULDERS
- [ ] Core: plank, dead bug, side plank, mountain climber, glute bridge march, leg raise — CORE
- [ ] Home full body, no equipment: squat, push-up, lunge, plank, glute bridge, jumping jacks — HOME
- (then repeat the cycle with 6 different moves per body part)

## Real exercise clips
If `library/videos.json` lists clips (imported from the owner's Google Drive) for this week's moves, prefer them over the drawn figures: put each clip in its card of the grid (extend make_workout_grid.py to composite video frames), keeping the muscle maps, names and cues.
