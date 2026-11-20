"""Festival greeting post for FitDecoded (1080x1350 JPEG slides).

Usage: python3 make_festival.py spec.json outprefix   -> outprefix_1.jpg [, outprefix_2.jpg ...]

Spec:
{
  "festival": "Diwali",
  "greeting": "HAPPY DIWALI",
  "sub": "Light up your health this festive season",
  "colors": ["#2B0F3A", "#FF9F1C"],          # background dark + glow/accent colour
  "icons": ["🪔", "🎆", "✨"],                  # 3 festive icons (must exist in engine/icons)
  "tips_title": "STAY FIT THIS DIWALI",        # optional 2nd slide
  "tips": [["🍬", "Enjoy sweets, just share the box"], ["🚶", "Walk 15 min after big meals"], ["💧", "Drink water between snacks"]]
}
"""
import json, sys, math, random
from PIL import Image, ImageDraw
import render_reel as R

W, H = 1080, 1350


def hexrgb(h):
    h = h.lstrip("#"); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def base(dark, glow, seed=3):
    img = Image.new("RGB", (W, H), dark)
    d = ImageDraw.Draw(img)
    for r in range(900, 0, -20):
        a = (1 - r / 900) ** 2.2 * 0.55
        col = tuple(int(dark[i] + (glow[i] - dark[i]) * a) for i in range(3))
        d.ellipse([W // 2 - r, 520 - r, W // 2 + r, 520 + r], fill=col)
    rnd = random.Random(seed)
    for _ in range(70):  # sparkles / bokeh
        x, y, s = rnd.randint(0, W), rnd.randint(0, H), rnd.randint(2, 7)
        c = tuple(min(255, int(glow[i] * 0.6 + 255 * 0.4)) for i in range(3))
        d.ellipse([x - s, y - s, x + s, y + s], fill=c)
    return img, d


def brand(d, glow, page=None):
    f = R.font(R.F_BOLD, 34)
    d.text((60, 40), "FITDECODED", font=f, fill=glow)
    if page:
        d.text((1020 - d.textlength(page, font=f), 40), page, font=f, fill=(230, 230, 230))
    fh = R.font(R.F_BOLD, 38)
    t = R.HANDLE
    d.text(((W - d.textlength(t, font=fh)) / 2, H - 90), t, font=fh, fill=glow)


def centered(d, text, fnt, y, color, maxw=W - 140, gap=1.1):
    for ln in R.wrap(d, text, fnt, maxw):
        d.text(((W - d.textlength(ln, font=fnt)) / 2, y), ln, font=fnt, fill=color)
        y += int(fnt.size * gap)
    return y


def main():
    s = json.load(open(sys.argv[1])); pre = sys.argv[2]
    dark, glow = hexrgb(s["colors"][0]), hexrgb(s["colors"][1])
    n = 2 if s.get("tips") else 1
    # slide 1: greeting
    img, d = base(dark, glow)
    brand(d, glow, f"1/{n}" if n > 1 else None)
    ic = s["icons"]
    R.paste_icon(img, ic[0], 380, W / 2, 400)
    if len(ic) > 1: R.paste_icon(img, ic[1], 220, 190, 250, rot=-10)
    if len(ic) > 2: R.paste_icon(img, ic[2], 200, W - 190, 290, rot=10)
    y = centered(d, s["greeting"], R.font(R.F_TITLE, s.get("greeting_size", 150)), s.get("greeting_y", 650), (255, 255, 255))
    y = centered(d, s.get("sub", ""), R.font(R.F_MED, 52), y + 20, (235, 235, 235), gap=1.3)
    if max(y + 40, 1130) + 50 < H - 100:
        centered(d, "From all of us at FitDecoded", R.font(R.F_BOLD, 40), max(y + 40, 1130), glow)
    img.save(f"{pre}_1.jpg", "JPEG", quality=92)
    if n == 1:
        print("ok 1 slide"); return
    # slide 2: festive fitness tips
    img, d = base(dark, glow, seed=7)
    brand(d, glow, "2/2")
    R.paste_icon(img, ic[0], 200, W / 2, 230)
    y = centered(d, s.get("tips_title", "STAY FIT THIS FESTIVAL"), R.font(R.F_TITLE, 100), 360, (255, 255, 255)) + 30
    fb = R.font(R.F_BOLD, 52)
    for e, txt in s["tips"]:
        lines = R.wrap(d, txt, fb, W - 380)
        hgt = max(170, len(lines) * 68 + 60)
        d.rounded_rectangle([70, y, W - 70, y + hgt], radius=34, fill=tuple(int(c * 0.6) for c in dark))
        R.paste_icon(img, e, 120, 165, y + hgt / 2)
        yy = y + (hgt - len(lines) * 68) / 2 - 4
        for ln in lines:
            d.text((260, yy), ln, font=fb, fill=(255, 255, 255)); yy += 68
        y += hgt + 30
    img.save(f"{pre}_2.jpg", "JPEG", quality=92)
    print("ok 2 slides")


if __name__ == "__main__":
    main()
