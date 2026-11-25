"""FitDecoded original exercise Reel (1080x1920): hook -> one scene per move (animated figure,
target-muscle chips, 2 form cues, reps) -> save/follow outro. Figures are our own drawn animations.

Usage: python3 make_exercise_reel.py spec.json out.mp4 cover.jpg

Spec:
{
 "hook_photo": "FitDecoded_02.jpg", "label": "NO GYM NEEDED", "hook": "6 MOVES FOR *STRONGER LEGS*", "hook_sub": "Ghar pe hi karo. Save it!",
 "moves": [{"name": "Bodyweight Squat", "anim": "squat", "targets": ["Quads", "Glutes"], "cues": ["...", "..."], "reps": "12 reps"}, ...],
 "outro": "Do *3 rounds*", "outro_sub": "Rest ~60 sec between rounds", "send": "Send this to your leg-day buddy"
}
anim: squat | lunge | bridge | calf | wallsit | donkey
"""
import json, math, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
import fd2 as F

W, H, FPS = 1080, 1920, 30
HOOK_T, MOVE_T, OUT_T = 2.6, 3.8, 3.4
BODY = (235, 238, 240)
BACK = (150, 158, 164)

# side-view poses in a 600x600 box, ground y=560, facing right
SQUAT_UP = {"toe": (355, 560), "ankle": (300, 560), "knee": (300, 430), "hip": (300, 300), "shoulder": (300, 150),
            "head": (300, 78), "elbow": (375, 150), "wrist": (450, 150)}
SQUAT_DN = {"toe": (355, 560), "ankle": (300, 560), "knee": (375, 450), "hip": (250, 440), "shoulder": (320, 305),
            "head": (355, 238), "elbow": (395, 305), "wrist": (470, 305)}
LUNGE_UP = {"toe": (430, 560), "ankle": (380, 560), "knee": (345, 445), "hip": (300, 330), "shoulder": (300, 180),
            "head": (300, 110), "elbow": (262, 255), "wrist": (292, 318),
            "ankle2": (160, 535), "toe2": (185, 560), "knee2": (225, 440)}
LUNGE_DN = {"toe": (430, 560), "ankle": (380, 560), "knee": (415, 438), "hip": (295, 420), "shoulder": (295, 270),
            "head": (295, 200), "elbow": (257, 345), "wrist": (287, 408),
            "ankle2": (160, 535), "toe2": (185, 560), "knee2": (262, 528)}
BRIDGE_DN = {"head": (112, 530), "shoulder": (180, 540), "hip": (312, 546), "knee": (400, 452), "ankle": (452, 560),
             "toe": (495, 560), "elbow": (250, 554), "wrist": (322, 556)}
BRIDGE_UP = {"head": (112, 530), "shoulder": (180, 540), "hip": (300, 490), "knee": (410, 446), "ankle": (452, 560),
             "toe": (495, 560), "elbow": (250, 554), "wrist": (322, 556)}
CALF_DN = {"toe": (355, 560), "ankle": (300, 560), "knee": (300, 432), "hip": (300, 302), "shoulder": (300, 152),
           "head": (300, 82), "elbow": (306, 228), "wrist": (312, 298)}
CALF_UP = {k: (v[0], v[1] - 40) for k, v in CALF_DN.items()}
CALF_UP["toe"] = (355, 560)
WALL = {"toe": (435, 560), "ankle": (382, 560), "knee": (380, 432), "hip": (252, 432), "shoulder": (246, 282),
        "head": (246, 212), "elbow": (300, 330), "wrist": (360, 410)}
WALL2 = dict(WALL, wrist=(360, 412))
DONKEY_DN = {"wrist": (430, 560), "elbow": (430, 500), "shoulder": (430, 432), "head": (505, 420), "hip": (262, 440),
             "knee2": (262, 560), "ankle2": (150, 560), "toe2": (130, 560),
             "knee": (270, 556), "ankle": (160, 548), "toe": (138, 545)}
DONKEY_UP = dict(DONKEY_DN, knee=(150, 425), ankle=(140, 305), toe=(118, 300))

ANIMS = {
    "squat": {"frames": [(SQUAT_UP, 0.25, 0.85, "DOWN SLOW"), (SQUAT_DN, 0.2, 0.6, "PUSH UP")],
              "hl": [("knee", "hip")], "glow": ["hip", "knee"]},
    "lunge": {"frames": [(LUNGE_UP, 0.25, 0.85, "DOWN SLOW"), (LUNGE_DN, 0.2, 0.6, "PUSH UP")],
              "hl": [("knee", "hip"), ("knee2", "hip")], "glow": ["hip"]},
    "bridge": {"frames": [(BRIDGE_DN, 0.25, 0.6, "LIFT HIPS"), (BRIDGE_UP, 0.45, 0.6, "SQUEEZE")],
               "hl": [("knee", "hip")], "glow": ["hip"]},
    "calf": {"frames": [(CALF_DN, 0.2, 0.5, "RISE UP"), (CALF_UP, 0.35, 0.6, "LOWER SLOW")],
             "hl": [("ankle", "knee")], "glow": ["ankle"]},
    "wallsit": {"frames": [(WALL, 0.9, 0.9, "HOLD"), (WALL2, 0.9, 0.9, "HOLD")],
                "hl": [("knee", "hip")], "glow": ["knee", "hip"], "wall": 222},
    "donkey": {"frames": [(DONKEY_DN, 0.2, 0.55, "KICK UP"), (DONKEY_UP, 0.35, 0.6, "LOWER")],
               "hl": [("knee", "hip")], "glow": ["hip"]},
}
BONES = [("ankle", "knee"), ("knee", "hip"), ("hip", "shoulder"), ("shoulder", "elbow"), ("elbow", "wrist"), ("ankle", "toe")]
BACK_BONES = [("ankle2", "knee2"), ("knee2", "hip"), ("ankle2", "toe2")]


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def pose_at(anim, t):
    fr = anim["frames"]
    t %= sum(h + m for _, h, m, _ in fr)
    for i, (p, hold, move, label) in enumerate(fr):
        nxt = fr[(i + 1) % len(fr)][0]
        if t < hold:
            return p, label
        t -= hold
        if t < move:
            k = ease(t / move)
            return {j: (p[j][0] + (nxt[j][0] - p[j][0]) * k, p[j][1] + (nxt[j][1] - p[j][1]) * k) for j in p}, label
        t -= move
    return fr[0][0], fr[0][3]


def figure(img, anim, pose, box, alpha=1.0):
    bx, by, bw, bh = box
    s = min(bw, bh) / 600.0
    ox, oy = bx + (bw - 600 * s) / 2, by + (bh - 600 * s) / 2
    P = {k: (ox + v[0] * s, oy + v[1] * s) for k, v in pose.items()}
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    if alpha == 1.0:
        g = ImageDraw.Draw(layer)
        for a, b in anim["hl"]:
            if a in P:
                g.line([P[a], P[b]], fill=F.LIME + (150,), width=int(70 * s))
        for j in anim.get("glow", []):
            r = 44 * s
            g.ellipse([P[j][0] - r, P[j][1] - r, P[j][0] + r, P[j][1] + r], fill=F.LIME + (90,))
        layer = layer.filter(ImageFilter.GaussianBlur(18 * s))
    d = ImageDraw.Draw(layer)
    hl = {tuple(x) for x in anim["hl"]}

    def seg(a, b, col, w):
        d.line([P[a], P[b]], fill=col + (255,), width=int(w))
        for j in (a, b):
            r = w / 2
            d.ellipse([P[j][0] - r, P[j][1] - r, P[j][0] + r, P[j][1] + r], fill=col + (255,))

    for a, b in BACK_BONES:
        if a in P:
            hot = (a, b) in hl
            seg(a, b, (150, 190, 40) if hot else BACK, 30 * s)
    seg("shoulder", "head", BODY, 18 * s)
    for a, b in BONES:
        hot = (a, b) in hl
        seg(a, b, F.LIME if hot else BODY, (40 if hot else 30) * s)
    r = 38 * s
    hx, hy = P["head"]
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=BODY + (255,))
    if alpha < 1.0:
        layer.putalpha(layer.getchannel("A").point(lambda v: int(v * alpha)))
    img.alpha_composite(layer)
    return s, ox, oy


def chips(img, items, x, y, size=40):
    d = ImageDraw.Draw(img)
    fc = F.font("xbold", size)
    F.fa_icon(img, "bullseye", x + 26, y + 33, 46)
    x += 72
    for m in items:
        tw = d.textlength(m.upper(), font=fc)
        d.rounded_rectangle([x, y, x + tw + 44, y + 66], radius=33, fill=F.LIME)
        d.text((x + 22, y + 10), m.upper(), font=fc, fill=F.INK)
        x += tw + 60


def move_static(m, i, n):
    img = F.dark_canvas(W, H, None).convert("RGBA")
    F.logo(img, 60, 70, 0.95)
    d = ImageDraw.Draw(img)
    f = F.font("black_i", 48)
    t = f"{i:02d}/{n:02d}"
    d.text((W - 70 - d.textlength(t, font=f), 92), t, font=f, fill=F.LIME)
    y = F.rich_text(img, m["name"].upper(), 64, 250, F.font("black_i", 96), W - 128)
    chips(img, m["targets"], 64, y + 24)
    top = y + 130
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, top, W - 60, top + 760], radius=34, fill=(20, 25, 28, 235), outline=(60, 72, 76, 255), width=3)
    gy = top + 760 - 70
    d.line([(110, gy), (W - 110, gy)], fill=(70, 80, 85, 255), width=5)
    cy = top + 800
    fs = F.font("xbold", 44)
    fn = F.font("black_i", 42)
    for k, cue in enumerate(m["cues"], 1):
        d.ellipse([64, cy + 2, 124, cy + 62], fill=F.LIME)
        d.text((94 - d.textlength(str(k), font=fn) / 2, cy + 6), str(k), font=fn, fill=F.INK)
        yy = cy + 4
        for ln in F.wrap(d, cue, fs, W - 260):
            d.text((150, yy), ln, font=fs, fill=F.WHITE); yy += 56
        cy = max(yy, cy + 66) + 22
    fr = F.font("black_i", 60)
    d.rounded_rectangle([60, H - 250, W - 60, H - 140], radius=22, fill=F.LIME)
    F.fa_icon(img, "dumbbell", 130, H - 195, 50, color=F.INK)
    d = ImageDraw.Draw(img)
    t = m["reps"].upper()
    d.text(((W - d.textlength(t, font=fr)) / 2, H - 236), t, font=fr, fill=F.INK)
    return img, (60, top + 10, W - 120, 740)


def move_frame(static, box, m, t):
    img = static.copy()
    anim = ANIMS[m["anim"]]
    for p, *_ in anim["frames"]:
        figure(img, anim, p, box, alpha=0.14)
    pose, label = pose_at(anim, t)
    s, ox, oy = figure(img, anim, pose, box)
    if "wall" in anim:
        d = ImageDraw.Draw(img)
        x = ox + anim["wall"] * s
        d.rectangle([x - 14, oy + 40 * s, x, oy + 566 * s], fill=(90, 100, 108, 255))
    d = ImageDraw.Draw(img)
    f = F.font("black_i", 50)
    tag = label
    if label == "HOLD":
        tag = f"HOLD {max(1, int(30 - t * 8))}s" if False else "HOLD 20-30 SEC"
    tw = d.textlength(tag, font=f)
    x1, y1 = W - 100 - tw - 44, box[1] + 26
    d.rounded_rectangle([x1, y1, W - 100, y1 + 78], radius=16, outline=F.LIME, width=5)
    d.text((x1 + 22, y1 + 10), tag, font=f, fill=F.LIME)
    return img.convert("RGB")


def hook_frame(spec, t):
    ph = F.clean_photo(spec["hook_photo"])
    ph = ph.crop((0, int(ph.height * 0.17), ph.width, ph.height))  # drop the photo's baked-in logo
    img = F.cover(ph, W, H, tuple(spec.get("focus", [0.5, 0.3])), zoom=1.0 + 0.04 * t / HOOK_T)
    img = F.shade(img, top=0.35, bottom=0.96, start=0.3).convert("RGBA")
    F.logo(img, 60, 70, 0.95)
    y = 1020
    _, y, _ = F.brush_label(img, spec["label"], 64, y, size=70, seed=3)
    y = F.rich_text(img, spec["hook"].upper(), 64, y + 30, F.font("black_i", 120), W - 128, gap=1.0)
    d = ImageDraw.Draw(img)
    fs = F.font("xbold_i", 52)
    d.text((66, y + 30), spec["hook_sub"], font=fs, fill=F.WHITE)
    return img.convert("RGB")


def outro_frame(spec, t):
    img = F.dark_canvas(W, H, F.clean_photo(spec.get("outro_photo", spec["hook_photo"])), "right").convert("RGBA")
    F.logo(img, 60, 70, 0.95)
    y = F.rich_text(img, spec["outro"].upper(), 64, 360, F.font("black_i", 130), W - 128)
    d = ImageDraw.Draw(img)
    d.text((66, y + 20), spec["outro_sub"], font=F.font("xbold", 50), fill=F.GREY)
    y += 160
    items = [("bookmark", "SAVE THIS", "for your next leg day"), ("paper-plane", "SHARE", spec["send"]),
             ("user-plus", "FOLLOW", "@fitdecoded.india for more")]
    pulse = 1.0 + 0.05 * math.sin(t * 6)
    for k, (ic, a, b) in enumerate(items):
        yy = y + k * 190
        r = int(64 * (pulse if k == 0 else 1))
        F.icon_circle(img, ic, 130, yy + 64, r=r)
        d = ImageDraw.Draw(img)
        d.text((230, yy + 4), a, font=F.font("black_i", 66), fill=F.LIME)
        for j, ln in enumerate(F.wrap(d, b, F.font("xbold", 42), W - 300)[:2]):
            d.text((232, yy + 84 + j * 50), ln, font=F.font("xbold", 42), fill=F.WHITE)
    return img.convert("RGB")


def main(spec_path, out, cover_out):
    spec = json.load(open(spec_path))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-shortest",
                          "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-c:a", "aac", "-b:a", "64k",
                          "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(HOOK_T * FPS)):
        fr = hook_frame(spec, i / FPS)
        if i == 0:
            fr.save(cover_out, quality=92)
        p.stdin.write(fr.tobytes())
    n = len(spec["moves"])
    for k, m in enumerate(spec["moves"], 1):
        static, box = move_static(m, k, n)
        for i in range(int(MOVE_T * FPS)):
            p.stdin.write(move_frame(static, box, m, i / FPS).tobytes())
    for i in range(int(OUT_T * FPS)):
        p.stdin.write(outro_frame(spec, i / FPS).tobytes())
    p.stdin.close(); p.wait()
    print("ok", HOOK_T + n * MOVE_T + OUT_T, "s")


if __name__ == "__main__":
    main(*sys.argv[1:4])
