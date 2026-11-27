"""FitDecoded nutrition / healthy-food tip card: colourful 3D food icons in lime panels.
Renders a still image (1080x1350) and, with --reel, a short Reel (1080x1920) where the
rows pop in one by one (~10-12 s, our own generated beat).

Usage:
  python3 make_tips.py spec.json out.jpg                      # image
  python3 make_tips.py spec.json out.mp4 cover.jpg --reel     # Reel + cover

Spec:
{
 "label": "SAVE THIS",                       # brush label above the headline
 "headline": "HIGH-PROTEIN *INDIAN* FOODS",  # *word* = lime; <= 6 words works best
 "sub": "Protein per serving · pick 1 in every meal",
 "photo": "FitDecoded_28.jpg",               # faint background photo from library/
 "value_label": "protein",                   # small word under each big value ("" for none)
 "columns": [                                # 1 or 2 columns, 3-6 rows each
  {"name": "VEG", "icon": "leaf", "items": [
     ["1f9c0", "Paneer", "100 g", "~18g", "~265 kcal"],   # [emoji code, title, line 1, big value, line 2]
     ...]},                                  # big value / line 2 may be "" (tips without numbers)
  {"name": "NON-VEG", "icon": "drumstick-bite", "items": [...]}
 ],
 "addons_title": "EASY ADD-ONS",             # optional strip of up to 3 [emoji, text, value]
 "addons": [["1f95b", "Milk, 1 glass", "~8g"], ...],
 "tip": "Aim for ~20-30g protein in each main meal."
}
Emoji codes are Fluent 3D icons in engine/icons/<code>.webp (run setup.sh); e.g. 1f9c0 cheese,
1f95a egg, 1f357 chicken leg, 1f41f fish, 1f963 bowl, 1f95b milk, 1f95c peanuts, 1fad8 beans,
1f372 dal pot, 1f35b curry, 1fadb pea pod (soya), 1f34c banana, 1f34e apple, 1f955 carrot,
1f966 broccoli, 1f952 cucumber, 1f965 coconut, 1f375 tea, 2615 hot drink, 1f4a7 droplet.
Every number must be a well-established approximate value (prefix "~"); if unsure, leave it out.
"""
import json, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
import fd2 as F

HERE = os.path.dirname(os.path.abspath(__file__))
FPS = 30


def emoji(img, code, cx, cy, size):
    p = os.path.join(HERE, "icons", f"{code}.webp")
    if not os.path.exists(p):
        print("missing icon", code)
        return
    e = Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)
    img.paste(e, (int(cx - size / 2), int(cy - size / 2)), e)


def rounded_panel(img, box, r=34):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(ov).rounded_rectangle(box, r, fill=(14, 18, 18, 215), outline=F.LIME + (255,), width=4)
    img.paste(ov, (0, 0), ov)


def fit_font(d, text, kind, size, maxw):
    while size > 18 and d.textlength(text, font=F.font(kind, size)) > maxw:
        size -= 2
    return F.font(kind, size)


def row(img, item, x, w, cy, rh, value_label, wide):
    code, name, l1, big, l2 = (list(item) + ["", "", ""])[:5]
    d = ImageDraw.Draw(img)
    sc = max(1.0, min(1.3, rh / 170))           # taller rows (Reel 9:16) get bigger type
    if wide:
        sc *= 1.12
    r = min(52 * sc, rh * 0.38)
    d.ellipse([x + 22, cy - r, x + 22 + 2 * r, cy + r], fill=(8, 10, 10), outline=F.LIME, width=3)
    emoji(img, code, x + 22 + r, cy, int(r * 1.55))
    tx, vx = x + 22 + 2 * r + 20, x + w - 24
    fb = F.font("black_i", int(46 * sc))
    bw = d.textlength(big, font=fb) if big else 0
    maxw = vx - bw - (14 if big else 0) - tx
    lines = [l for l in (l1, l2) if l]
    ts, l1s, l2s = int(33 * sc), int(24 * sc), int(21 * sc)
    ft = fit_font(d, name, "xbold", ts, maxw)
    th = ts * 1.2 + len(lines) * l1s * 1.13
    yy = cy - th / 2
    d.text((tx, yy), name, font=ft, fill=F.WHITE)
    yy += ts * 1.22
    for k, ln in enumerate(lines):
        f = fit_font(d, ln, "pop_m", l1s if k == 0 else l2s, maxw)
        d.text((tx, yy), ln, font=f, fill=F.GREY if k == 0 else (150, 160, 150))
        yy += l1s * 1.13
    if big:
        d.text((vx - bw, cy - 40 * sc), big, font=fb, fill=F.LIME)
        if value_label:
            fl = F.font("pop_m", int(20 * sc))
            d.text((vx - d.textlength(value_label, font=fl), cy + 14 * sc), value_label, font=fl, fill=F.GREY)


def column(img, col, x, y, w, h, value_label, shown, wide):
    rounded_panel(img, [x, y, x + w, y + h])
    d = ImageDraw.Draw(img)
    top = y + 24
    if col.get("name"):
        fh = F.font("black_i", 46)
        tw = d.textlength(col["name"], font=fh)
        hx = x + (w - (tw + 80)) / 2
        F.icon_circle(img, col.get("icon", "leaf"), hx + 30, y + 52, 30)
        d.text((hx + 76, y + 22), col["name"], font=fh, fill=F.LIME)
        d.line([(x + 30, y + 100), (x + w - 30, y + 100)], fill=(70, 90, 40), width=2)
        top = y + 112
    items = col["items"]
    rh = (y + h - 12 - top) / len(items)
    for i, it in enumerate(items[:shown]):
        row(img, it, x, w, top + rh * i + rh / 2, rh, value_label, wide)
        if i < len(items) - 1:
            d.line([(x + 30, top + rh * (i + 1)), (x + w - 24, top + rh * (i + 1))], fill=(45, 55, 40), width=2)


def steps(s):
    """Reveal order: rows interleaved across columns, then add-ons, then the tip."""
    cols = s["columns"]
    return max(len(c["items"]) for c in cols) + (1 if s.get("addons") else 0) + (1 if s.get("tip") else 0)


def render(s, W=1080, H=1350, reveal=None, yoff=0):
    """reveal = how many reveal steps to show (None = everything)."""
    n_rows = max(len(c["items"]) for c in s["columns"])
    reveal = 10 ** 6 if reveal is None else reveal
    ph = F.clean_photo(s.get("photo", "FitDecoded_28.jpg"))
    ph = ph.crop((0, int(ph.height * 0.2), ph.width, ph.height))  # drop the baked-in logo
    img = F.cover(ph, W, H, (0.5, 0.3)).filter(ImageFilter.GaussianBlur(3))
    img = Image.blend(Image.new("RGB", (W, H), (10, 13, 14)), img, 0.22)
    d = ImageDraw.Draw(img)
    F.logo(img, 44, 30 + yoff, scale=0.55, tagline=False)
    fh = F.font("pop_m", 26)
    d.text((W - 44 - d.textlength(F.HANDLE, font=fh), 58 + yoff), F.HANDLE, font=fh, fill=F.GREY)
    _, y, _ = F.brush_label(img, s.get("label", "SAVE THIS"), 0, 118 + yoff, size=40, seed=4, center=True)
    y = F.rich_text(img, s["headline"].upper(), 0, y + 14, F.font("black_i", s.get("size", 76)), W - 80,
                    gap=1.0, center=True)
    d = ImageDraw.Draw(img)
    if s.get("sub"):
        fs = fit_font(d, s["sub"], "pop_m", 30, W - 80)
        d.text(((W - d.textlength(s["sub"], font=fs)) / 2, y + 6), s["sub"], font=fs, fill=F.WHITE)
    y += 60
    addons = s.get("addons") or []
    bottom = H - 70 - yoff - (150 if addons else 0) - (60 if s.get("tip") else 0)
    cols = s["columns"]
    gap = 22
    cw = (W - 72 - gap * (len(cols) - 1)) / len(cols)
    for i, col in enumerate(cols):
        column(img, col, 36 + i * (cw + gap), y, cw, bottom - y, s.get("value_label", ""),
               min(reveal, n_rows), len(cols) == 1)
    d = ImageDraw.Draw(img)
    y = bottom + 18
    step = n_rows
    if addons:
        step += 1
        if reveal >= step:
            rounded_panel(img, [36, y, W - 36, y + 132], r=28)
            d = ImageDraw.Draw(img)
            ft = F.font("black_i", 30)
            t = s.get("addons_title", "EASY ADD-ONS")
            tw = d.textlength(t, font=ft)
            d.rectangle([(W - tw) / 2 - 16, y - 18, (W + tw) / 2 + 16, y + 18], fill=(14, 18, 18))
            d.text(((W - tw) / 2, y - 18), t, font=ft, fill=F.LIME)
            aw = (W - 72) / len(addons)
            for i, (code, name, val) in enumerate(addons):
                ax = 36 + aw * i
                emoji(img, code, ax + 62, y + 72, 62)
                d.text((ax + 106, y + 34), name, font=fit_font(d, name, "xbold", 26, aw - 120), fill=F.WHITE)
                d.text((ax + 106, y + 70), val, font=F.font("black_i", 34), fill=F.LIME)
                if i:
                    d.line([(ax, y + 28), (ax, y + 110)], fill=(70, 90, 40), width=2)
        y += 150
    if s.get("tip"):
        step += 1
        if reveal >= step:
            t = "TIP: " + s["tip"]
            ft = fit_font(d, t, "bold_i", 28, W - 80)
            d.text(((W - d.textlength(t, font=ft)) / 2, y + 4), t, font=ft, fill=F.WHITE)
    fb = F.font("xbold", 26)
    t = s.get("footer", "SAVE  ·  SHARE  ·  FOLLOW FOR DAILY FOOD TIPS")
    d.text(((W - d.textlength(t, font=fb)) / 2, H - 52 - yoff), t, font=fb, fill=F.LIME)
    return img


def reel(s, out, cover_out, hook_t=1.6, step_t=0.75, hold_t=3.0, fade=0.25):
    W, H = 1080, 1920
    n = steps(s)
    states = [render(s, W, H, k, yoff=120) for k in range(n + 1)]
    states[-1].save(cover_out, quality=92)      # cover = the full card
    total = hook_t + n * step_t + hold_t
    wav = out + ".wav"
    from render_reel import make_audio
    make_audio(wav, total, [0.0, hook_t] + [hook_t + k * step_t for k in range(1, n + 1)])
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav, "-shortest",
                          "-c:v", "libx264", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-crf", "20",
                          "-c:a", "aac", "-b:a", "64k", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    for i in range(int(total * FPS)):
        t = i / FPS
        if t < hook_t:
            fr = states[0]
        else:
            k = min(n, int((t - hook_t) / step_t) + 1)
            a = min(1.0, ((t - hook_t) - (k - 1) * step_t) / fade) if k <= n else 1.0
            fr = states[k] if a >= 1 else Image.blend(states[k - 1], states[k], a)
        p.stdin.write(fr.tobytes())
    p.stdin.close(); p.wait()
    os.remove(wav)
    print("ok", round(total, 1), "s ->", out)


if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    if "--reel" in sys.argv:
        reel(spec, sys.argv[2], sys.argv[3])
    else:
        render(spec).save(sys.argv[2], quality=93)
        print("saved", sys.argv[2])
