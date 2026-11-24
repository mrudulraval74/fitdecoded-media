"""FitDecoded exercise demo slide: animated figure + target muscles + steps (PROTOTYPE).

Usage: python3 make_exercise.py spec.json outprefix  -> outprefix.mp4 (looping demo) + outprefix.jpg (still)

Spec:
{
 "index": "1/3", "name": "BODYWEIGHT *SQUAT*", "targets": ["Quads", "Glutes", "Core"],
 "dose": "3 sets x 12 reps", "steps": ["Feet shoulder-width, toes slightly out", "...", "..."],
 "anim": "squat"            # key in POSES below
}
"""
import json, os, subprocess, sys, math, shutil, tempfile
from PIL import Image, ImageDraw, ImageFilter
import fd2 as F

W, H = 1080, 1350
FPS = 30
PANEL_H = 520
BONES = [("ankle", "knee"), ("knee", "hip"), ("hip", "shoulder"), ("shoulder", "elbow"), ("elbow", "wrist"),
         ("ankle", "toe")]

# Side-view poses in a 600x600 box (ground at y=560). Each anim: list of (pose, hold_seconds, move_seconds_to_next)
POSES = {
 "squat": {
  "frames": [
   ({"toe": (355, 560), "ankle": (300, 560), "knee": (300, 430), "hip": (300, 300), "shoulder": (300, 150),
     "head": (300, 78), "elbow": (375, 150), "wrist": (450, 150)}, 0.35, 1.0, "DOWN"),
   ({"toe": (355, 560), "ankle": (300, 560), "knee": (375, 450), "hip": (250, 440), "shoulder": (320, 305),
     "head": (355, 238), "elbow": (395, 305), "wrist": (470, 305)}, 0.25, 0.7, "UP"),
  ],
  "hl": [("knee", "hip"), ("hip", "shoulder")],   # bones drawn lime (target muscles)
  "glow": ["hip", "knee"],
 },
}


def lerp(a, b, t):
    return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)


def ease(t):
    return 0.5 - 0.5 * math.cos(math.pi * t)


def pose_at(anim, t):
    fr = anim["frames"]
    total = sum(h + m for _, h, m, _ in fr)
    t = t % total
    for i, (p, hold, move, label) in enumerate(fr):
        nxt = fr[(i + 1) % len(fr)][0]
        if t < hold:
            return p, label, 0.0
        t -= hold
        if t < move:
            k = ease(t / move)
            return {j: lerp(p[j], nxt[j], k) for j in p}, label, t / move
        t -= move
    return fr[0][0], fr[0][3], 0.0


def draw_figure(img, anim, pose, box, ghost=False):
    bx, by, bw, bh = box
    s = min(bw, bh) / 600.0
    ox, oy = bx + (bw - 600 * s) / 2, by + (bh - 600 * s) / 2
    P = {k: (ox + v[0] * s, oy + v[1] * s) for k, v in pose.items()}
    if not ghost:
        _glow(img, anim, P, s)
    _body(img, anim, P, s, ox, oy, bx, bw, ghost)


def _glow(img, anim, P, s):
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    for a, b in anim["hl"]:
        g.line([P[a], P[b]], fill=F.LIME + (150,), width=int(70 * s))
    for j in anim.get("glow", []):
        r = 40 * s
        g.ellipse([P[j][0] - r, P[j][1] - r, P[j][0] + r, P[j][1] + r], fill=F.LIME + (90,))
    glow = glow.filter(ImageFilter.GaussianBlur(18 * s))
    img.alpha_composite(glow)


def _body(img, anim, P, s, ox, oy, bx, bw, ghost):
    d = ImageDraw.Draw(img)
    gy = oy + 566 * s
    if not ghost:
        d.line([(bx + 40, gy), (bx + bw - 40, gy)], fill=(70, 80, 85, 255), width=4)
    d.line([P["shoulder"], P["head"]], fill=(235, 238, 240, 255), width=int(18 * s))
    hl = {tuple(x) for x in anim["hl"]}
    for a, b in BONES:
        col = F.LIME if (a, b) in hl else (235, 238, 240)
        w = int((40 if (a, b) in hl else 30) * s)
        d.line([P[a], P[b]], fill=col + (255,), width=w)
        for j in (a, b):
            r = w / 2
            d.ellipse([P[j][0] - r, P[j][1] - r, P[j][0] + r, P[j][1] + r], fill=col + (255,))
    r = 38 * s
    hx, hy = P["head"]
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=(235, 238, 240, 255))


def base(spec):
    img = F.dark_canvas(W, H, None, "right").convert("RGBA")
    F.logo(img, 56, 46, 0.8)
    d = ImageDraw.Draw(img)
    f = F.font("xbold", 30)
    t = "EXERCISE " + spec.get("index", "")
    d.text((W - 60 - d.textlength(t, font=f), 70), t, font=f, fill=F.GREY)
    y = F.rich_text(img, spec["name"].upper(), 60, 170, F.font("black_i", 84), W - 120)
    # target chips
    d = ImageDraw.Draw(img)
    fc = F.font("xbold", 34)
    x = 60
    y += 18
    F.fa_icon(img, "bullseye", x + 22, y + 27, 40)
    x += 62
    for m in spec["targets"]:
        tw = d.textlength(m.upper(), font=fc)
        d.rounded_rectangle([x, y, x + tw + 40, y + 56], radius=28, fill=F.LIME)
        d.text((x + 20, y + 9), m.upper(), font=fc, fill=F.INK)
        x += tw + 56
    return img, y + 80


def frame(spec, anim, static, top, t):
    img = static.copy()
    box = (60, top, W - 120, PANEL_H)
    pose, label, _ = pose_at(anim, t)
    ghost = Image.new("RGBA", img.size, (0, 0, 0, 0))
    for p, *_ in anim["frames"]:
        draw_figure(ghost, anim, p, box, ghost=True)
    ghost.putalpha(ghost.getchannel("A").point(lambda a: a * 0.16))
    img.alpha_composite(ghost)
    draw_figure(img, anim, pose, box)
    d = ImageDraw.Draw(img)
    f = F.font("black_i", 44)
    tag = label + (" (slow)" if label == "DOWN" else "")
    tw = d.textlength(tag, font=f)
    d.rounded_rectangle([W - 90 - tw - 40, top + 20, W - 90, top + 84], radius=14, outline=F.LIME, width=4)
    d.text((W - 90 - tw - 20, top + 26), tag, font=f, fill=F.LIME)
    return img.convert("RGB")


def static_layer(spec):
    img, top = base(spec)
    d = ImageDraw.Draw(img)
    # figure panel
    d.rounded_rectangle([60, top, W - 60, top + PANEL_H], radius=28, fill=(20, 25, 28, 235), outline=(60, 70, 74, 255), width=2)
    y = top + PANEL_H + 26
    fs = F.font("xbold", 33)
    fn = F.font("black_i", 36)
    for i, st in enumerate(spec["steps"], 1):
        cx, cy = 92, y + 22
        d.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill=F.LIME)
        n = str(i)
        d.text((cx - d.textlength(n, font=fn) / 2, cy - 23), n, font=fn, fill=F.INK)
        lines = F.wrap(d, st, fs, W - 260)
        yy = y
        for ln in lines:
            d.text((140, yy), ln, font=fs, fill=F.WHITE); yy += 42
        y = max(yy, y + 50) + 12
    # dose bar
    fd = F.font("black_i", 46)
    d.rounded_rectangle([60, H - 120, W - 60, H - 40], radius=18, fill=F.LIME)
    t = spec["dose"].upper()
    F.fa_icon(img, "dumbbell", 120, H - 80, 42, color=F.INK)
    d = ImageDraw.Draw(img)
    d.text(((W - d.textlength(t, font=fd)) / 2, H - 108), t, font=fd, fill=F.INK)
    return img, top + 0


def main(spec_path, out):
    spec = json.load(open(spec_path))
    anim = POSES[spec["anim"]]
    static, top = static_layer(spec)
    total = sum(h + m for _, h, m, _ in anim["frames"])
    reps = spec.get("loops", 2)
    n = int(round(total * reps * FPS))
    tmp = tempfile.mkdtemp()
    for i in range(n):
        frame(spec, anim, static, top, i / FPS).save(os.path.join(tmp, f"f{i:04d}.png"))
    frame(spec, anim, static, top, anim["frames"][0][1] + anim["frames"][0][2]).save(out + ".jpg", quality=92)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out + ".mp4"], check=True)
    shutil.rmtree(tmp)
    print("ok", n, "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
