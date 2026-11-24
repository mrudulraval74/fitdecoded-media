"""FitDecoded animated workout grid (PROTOTYPE): 6 moves for one body part, each card shows an
animated figure doing the move + a mini muscle map with the worked muscles in lime.

Usage: python3 make_workout_grid.py spec.json outprefix -> outprefix.mp4 (6 s loop) + outprefix.jpg (still)

Spec:
{
 "title": "6 DUMBBELL *MOVES*", "sub": "FOR ARMS: BICEPS + TRICEPS + FOREARMS",
 "moves": [ {"name": "Regular Curl", "grip": "Palms up", "anim": "curl", "map": "front", "muscles": ["biceps"]}, ... ],  # 6
 "dose": "3 SETS x 10-12 REPS EACH", "note": "Start light. Slow, controlled reps."
}
anim: curl | hammer | reverse | overhead | kickback | wrist     map: front | back
muscles: biceps, triceps, forearms
"""
import json, math, os, shutil, subprocess, sys, tempfile
from PIL import Image, ImageDraw, ImageFilter
import fd2 as F

W, H, FPS, LOOP, LOOPS = 1080, 1350, 30, 2.0, 3
BODY = (232, 236, 240)
DIM = (70, 80, 88)


def ease_loop(t):
    """0 -> 1 -> 0 over one loop with short holds."""
    p = (t % LOOP) / LOOP
    if p < 0.1: return 0.0
    if p < 0.45: return 0.5 - 0.5 * math.cos(math.pi * (p - 0.1) / 0.35)
    if p < 0.55: return 1.0
    if p < 0.95: return 0.5 + 0.5 * math.cos(math.pi * (p - 0.55) / 0.4)
    return 0.0


def L(a, b, k):
    return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k)


def seg(d, a, b, w, col):
    d.line([a, b], fill=col, width=int(w))
    for p in (a, b):
        d.ellipse([p[0] - w / 2, p[1] - w / 2, p[0] + w / 2, p[1] + w / 2], fill=col)


def dumbbell(d, c, ang, s):
    dx, dy = math.cos(ang) * 15 * s, math.sin(ang) * 15 * s
    a, b = (c[0] - dx, c[1] - dy), (c[0] + dx, c[1] + dy)
    d.line([a, b], fill=(150, 160, 168), width=int(5 * s))
    for p in (a, b):
        r = 8 * s
        d.ellipse([p[0] - r, p[1] - r, p[0] + r, p[1] + r], fill=(40, 46, 50), outline=(170, 180, 186), width=max(2, int(2 * s)))


def front_figure(img, cx, gy, s, arms, hl, bell_ang, two_hand=False):
    """arms: dict side(-1/1) -> (elbow, wrist) offsets in figure units (y up negative)."""
    P = lambda x, y: (cx + x * s, gy + y * s)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    d = ImageDraw.Draw(img)
    # legs + torso
    for sd in (-1, 1):
        seg(d, P(sd * 16, -100), P(sd * 22, -4), 14 * s, BODY)
    d.polygon([P(-30, -178), P(30, -178), P(19, -100), P(-19, -100)], fill=BODY)
    d.rounded_rectangle([*P(-20, -112), *P(20, -94)], radius=int(6 * s), fill=(40, 46, 50))  # shorts band
    for sd in (-1, 1):
        sh = P(sd * 30, -172)
        el = P(*arms[sd][0]); wr = P(*arms[sd][1])
        if "upper" in hl:
            g.line([sh, el], fill=F.LIME + (170,), width=int(26 * s))
        if "fore" in hl:
            g.line([el, wr], fill=F.LIME + (170,), width=int(24 * s))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7 * s)))
    d = ImageDraw.Draw(img)
    for sd in (-1, 1):
        sh = P(sd * 30, -172)
        el = P(*arms[sd][0]); wr = P(*arms[sd][1])
        seg(d, sh, el, 12 * s, F.LIME if "upper" in hl else BODY)
        seg(d, el, wr, 11 * s, F.LIME if "fore" in hl else BODY)
    if two_hand:
        w = P(*arms[1][1])
        dumbbell(d, w, bell_ang, s)
    else:
        for sd in (-1, 1):
            dumbbell(d, P(*arms[sd][1]), bell_ang if sd > 0 else math.pi - bell_ang, s)
    seg(d, P(0, -180), P(0, -192), 9 * s, BODY)
    r = 15 * s
    hx, hy = P(0, -207)
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=BODY)


def side_kickback(img, cx, gy, s, k):
    P = lambda x, y: (cx + x * s, gy + y * s)
    glow = Image.new("RGBA", img.size, (0, 0, 0, 0))
    g = ImageDraw.Draw(glow)
    hip, knee, ank, toe = P(-26, -112), P(-8, -58), P(-16, -4), P(6, -4)
    sh = P(44, -150)                       # torso hinged forward (facing right)
    el = P(0, -124)                        # upper arm pinned back, parallel to torso
    wr = L(P(2, -80), P(-44, -112), k)     # forearm: hangs down -> straight back
    g.line([sh, el], fill=F.LIME + (170,), width=int(26 * s))
    img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(7 * s)))
    d = ImageDraw.Draw(img)
    seg(d, hip, knee, 14 * s, BODY); seg(d, knee, ank, 13 * s, BODY); seg(d, ank, toe, 8 * s, BODY)
    seg(d, hip, sh, 30 * s, BODY)
    seg(d, sh, el, 12 * s, F.LIME); seg(d, el, wr, 11 * s, BODY)
    dumbbell(d, wr, 0.0, s)
    seg(d, sh, P(60, -158), 9 * s, BODY)
    r = 15 * s
    hx, hy = P(76, -166)
    d.ellipse([hx - r, hy - r, hx + r, hy + r], fill=BODY)


def draw_move(img, anim, cx, gy, s, t):
    k = ease_loop(t)
    if anim in ("curl", "hammer", "reverse"):
        arms = {sd: ((sd * 34, -128), L((sd * 36, -84), (sd * 30, -168), k)) for sd in (-1, 1)}
        ang = {"curl": 0.0, "reverse": 0.0, "hammer": math.pi / 2}[anim]
        hl = ("upper", "fore") if anim != "curl" else ("upper",)
        front_figure(img, cx, gy, s, arms, hl, ang)
    elif anim == "overhead":
        wr = L((2, -300), (2, -222), k)
        arms = {sd: ((sd * 18, -262), (sd * 2 + 0, wr[1])) for sd in (-1, 1)}
        arms = {sd: (arms[sd][0], (wr[0] * sd, wr[1])) for sd in (-1, 1)}
        front_figure(img, cx, gy, s, arms, ("upper",), math.pi / 2, two_hand=True)
    elif anim == "kickback":
        side_kickback(img, cx, gy, s, k)
    elif anim == "wrist":
        arms = {sd: ((sd * 36, -128), (sd * 46, -150)) for sd in (-1, 1)}
        ang = math.pi / 2 + (k - 0.5) * 2.2
        front_figure(img, cx, gy, s, arms, ("fore",), ang)


def muscle_map(img, cx, top, s, view, muscles):
    d = ImageDraw.Draw(img)
    P = lambda x, y: (cx + x * s, top + y * s)
    col = lambda m: F.LIME if m in muscles else DIM
    r = 9 * s
    d.ellipse([*P(-9, 0), *P(9, 18)], fill=DIM)
    d.polygon([P(-26, 22), P(26, 22), P(16, 76), P(-16, 76)], fill=DIM)
    for sd in (-1, 1):
        up = "biceps" if view == "front" else "triceps"
        d.polygon([P(sd * 27, 22), P(sd * 36, 26), P(sd * 38, 52), P(sd * 30, 52)], fill=col(up))
        d.polygon([P(sd * 30, 55), P(sd * 38, 55), P(sd * 42, 84), P(sd * 35, 84)], fill=col("forearms"))
    f = F.font("xbold", int(13 * s))
    t = view.upper()
    d.text((cx - d.textlength(t, font=f) / 2, top + 88 * s), t, font=f, fill=(140, 150, 156))


def static_layer(spec):
    img = F.dark_canvas(W, H, None, "right").convert("RGBA")
    F.logo(img, 56, 46, 0.8)
    y = F.rich_text(img, spec["title"].upper(), 60, 150, F.font("black_i", 70), W - 120)
    d = ImageDraw.Draw(img)
    fs = F.font("xbold_i", 34)
    d.text((62, y + 6), spec["sub"].upper(), font=fs, fill=F.GREY)
    cards = []
    gx, gy0, cw, ch, gap = 48, y + 64, 312, 400, 18
    fn, fnum, fg = F.font("black_i", 30), F.font("black_i", 40), F.font("xbold", 22)
    for i, m in enumerate(spec["moves"]):
        x = gx + (i % 3) * (cw + gap); yy = gy0 + (i // 3) * (ch + gap)
        d.rounded_rectangle([x, yy, x + cw, yy + ch], radius=24, fill=(18, 23, 26, 240), outline=(70, 90, 60, 255), width=2)
        d.text((x + 18, yy + 12), f"{i + 1:02d}", font=fnum, fill=F.LIME)
        lines = F.wrap(d, m["name"], fn, cw - 100)
        ty = yy + 14
        for ln in lines[:2]:
            d.text((x + 82, ty), ln, font=fn, fill=F.WHITE); ty += 34
        if m.get("grip"):
            d.text((x + 82, ty + 2), m["grip"], font=fg, fill=F.LIME)
        muscle_map(img, x + cw - 44, yy + ch - 118, 1.0, m["map"], m["muscles"])
        cards.append((x, yy, cw, ch, m))
    fy = gy0 + 2 * ch + gap + 22
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([60, fy, W - 60, fy + 76], radius=18, fill=F.LIME)
    F.fa_icon(img, "dumbbell", 112, fy + 38, 40, color=F.INK)
    d = ImageDraw.Draw(img)
    fd = F.font("black_i", 40)
    t = spec["dose"].upper()
    d.text(((W - d.textlength(t, font=fd)) / 2, fy + 14), t, font=fd, fill=F.INK)
    fnote = F.font("xbold", 30)
    t = spec.get("note", "")
    d.text(((W - d.textlength(t, font=fnote)) / 2, fy + 94), t, font=fnote, fill=F.GREY)
    return img, cards


def frame(static, cards, t):
    img = static.copy()
    for i, (x, y, cw, ch, m) in enumerate(cards):
        draw_move(img, m["anim"], x + cw * 0.36, y + ch - 24, 1.12 if m["anim"] != "overhead" else 0.98, t)
    return img.convert("RGB")


def main(spec_path, out):
    spec = json.load(open(spec_path))
    static, cards = static_layer(spec)
    tmp = tempfile.mkdtemp()
    n = int(LOOP * LOOPS * FPS)
    for i in range(n):
        frame(static, cards, i / FPS).save(os.path.join(tmp, f"f{i:04d}.png"))
    frame(static, cards, LOOP * 0.5).save(out + ".jpg", quality=92)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%04d.png"),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", "-movflags", "+faststart", out + ".mp4"], check=True)
    shutil.rmtree(tmp)
    print("ok", n, "frames")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
