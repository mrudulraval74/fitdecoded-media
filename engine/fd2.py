"""FitDecoded brand-style drawing kit (v2): lime brush labels, italic heavy type,
icon circles, HUD cards, logo, photo backgrounds from library/."""
import json, math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
LIB = os.path.join(HERE, "..", "library")
LIME = (197, 245, 54)
LIME_D = (126, 211, 33)
INK = (12, 14, 16)
WHITE = (250, 250, 250)
GREY = (200, 205, 210)
PANEL = (16, 20, 22)
GF = "/usr/share/fonts/truetype/google-fonts/"
MONT_I = GF + "ofl/montserrat/Montserrat-Italic[wght].ttf"
MONT = GF + "ofl/montserrat/Montserrat[wght].ttf"
POP_B = GF + "Poppins-Bold.ttf"
POP_M = GF + "Poppins-Medium.ttf"
FA = os.path.join(HERE, "assets", "fa-solid-900.ttf")
FA_MAP = json.load(open(os.path.join(HERE, "assets", "fa_solid_map.json")))
HANDLE = "@fitdecoded.india"
_fc = {}


def font(kind, size):
    """kind: 'black_i','xbold_i','bold_i','xbold','bold','pop_b','pop_m','fa'"""
    k = (kind, size)
    if k in _fc:
        return _fc[k]
    if kind == "fa":
        f = ImageFont.truetype(FA, size)
    elif kind.startswith("pop"):
        f = ImageFont.truetype(POP_B if kind == "pop_b" else POP_M, size)
    else:
        f = ImageFont.truetype(MONT_I if kind.endswith("_i") else MONT, size)
        name = {"black_i": b"Black Italic", "xbold_i": b"ExtraBold Italic", "bold_i": b"Bold Italic",
                "xbold": b"ExtraBold", "bold": b"Bold", "black": b"Black"}[kind]
        f.set_variation_by_name(name)
    _fc[k] = f
    return f


# ---------------- backgrounds ----------------
def lib_index():
    return json.load(open(os.path.join(LIB, "index.json")))


def clean_photo(name):
    """Library images have a stray strip/white line at the top and thin side borders: crop them off."""
    import numpy as np
    im = Image.open(os.path.join(LIB, name)).convert("RGB")
    a = np.asarray(im.convert("L")).astype(float)
    rows = a[:420, 100:980].mean(1)
    wl = [y for y in range(420) if rows[y] > 200]
    top = (wl[-1] + 8) if wl else 0
    return im.crop((54, top, 1028, 1340))


def cover(im, w, h, focus=(0.5, 0.5), zoom=1.0):
    s = max(w / im.width, h / im.height) * zoom
    nw, nh = int(im.width * s + 0.5), int(im.height * s + 0.5)
    r = im.resize((nw, nh), Image.LANCZOS)
    x = int((nw - w) * focus[0]); y = int((nh - h) * focus[1])
    return r.crop((x, y, x + w, y + h))


def shade(img, top=0.0, bottom=0.85, left=0.0, start=0.35):
    """Darken: vertical gradient (from `start` of height down to bottom alpha) and optional left fade."""
    w, h = img.size
    ov = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(ov)
    for y in range(h):
        t = y / h
        a = top * max(0, 1 - t / 0.25)
        if t > start:
            a = max(a, bottom * ((t - start) / (1 - start)) ** 1.2)
        d.line([(0, y), (w, y)], fill=int(255 * min(1, a)))
    if left:
        lov = Image.new("L", (w, h), 0)
        ld = ImageDraw.Draw(lov)
        for x in range(w):
            t = x / w
            ld.line([(x, 0), (x, h)], fill=int(255 * left * max(0, 1 - t / 0.7) ** 1.3))
        ov = Image.fromarray(__import__("numpy").maximum(__import__("numpy").asarray(ov), __import__("numpy").asarray(lov)))
    black = Image.new("RGB", (w, h), INK)
    return Image.composite(black, img, ov)


def dark_canvas(w, h, photo=None, side="right"):
    """Dark panel background with a faint lime glow and optional faded photo on one side."""
    img = Image.new("RGB", (w, h), (13, 16, 18))
    if photo is not None:
        photo = photo.crop((0, int(photo.height * 0.17), photo.width, photo.height))  # drop baked-in logo
        p = cover(photo, int(w * 0.62), h, (0.5, 0.4))
        p = Image.blend(Image.new("RGB", p.size, (13, 16, 18)), p, 0.55)
        mask = Image.new("L", p.size, 0)
        md = ImageDraw.Draw(mask)
        for x in range(p.width):
            t = x / p.width if side == "right" else 1 - x / p.width
            md.line([(x, 0), (x, h)], fill=int(255 * min(1, t * 1.6) ** 1.5))
        img.paste(p, (w - p.width, 0) if side == "right" else (0, 0), mask)
    glow = Image.new("RGB", (w, h), (0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([-w * 0.3, h * 0.55, w * 0.7, h * 1.4], fill=(40, 70, 10))
    glow = glow.filter(ImageFilter.GaussianBlur(160))
    return Image.fromarray(__import__("numpy").clip(__import__("numpy").asarray(img).astype(int) + __import__("numpy").asarray(glow).astype(int), 0, 255).astype("uint8"))


# ---------------- brand pieces ----------------
def logo(img, x, y, scale=1.0, tagline=True):
    d = ImageDraw.Draw(img)
    fF = font("black_i", int(110 * scale))
    # F mark with a darker shadow layer
    d.text((x + 6 * scale, y + 4 * scale), "F", font=fF, fill=(40, 90, 40))
    d.text((x, y), "F", font=fF, fill=LIME)
    tx = x + int(88 * scale)
    ft = font("xbold", int(62 * scale))
    d.text((tx, y + int(22 * scale)), "Fit", font=ft, fill=WHITE)
    d.text((tx + d.textlength("Fit", font=ft) + 2, y + int(22 * scale)), "Decoded", font=ft, fill=LIME)
    if tagline:
        fs = font("xbold", int(25 * scale))
        d.text((x + int(14 * scale), y + int(112 * scale)), "UNDERSTAND YOUR BODY. TRAIN SMARTER.", font=fs, fill=WHITE)


def brush(img, x, y, w, h, color=LIME, seed=1, angle=-2.0):
    """Rough paint-stroke rectangle."""
    rnd = random.Random(seed)
    pad = 40
    layer = Image.new("RGBA", (int(w) + pad * 2, int(h) + pad * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    pts = []
    n = 28
    for i in range(n + 1):
        pts.append((pad + w * i / n, pad + rnd.uniform(-7, 7)))
    for i in range(6):
        pts.append((pad + w + rnd.uniform(-4, 22), pad + h * i / 5 + rnd.uniform(-4, 4)))
    for i in range(n, -1, -1):
        pts.append((pad + w * i / n, pad + h + rnd.uniform(-7, 7)))
    for i in range(5, -1, -1):
        pts.append((pad + rnd.uniform(-22, 4), pad + h * i / 5 + rnd.uniform(-4, 4)))
    d.polygon(pts, fill=color + (255,))
    for _ in range(9):  # dry-brush streaks
        yy = pad + rnd.uniform(0.05, 0.95) * h
        x0 = pad + w + rnd.uniform(0, 10)
        d.line([(x0, yy), (x0 + rnd.uniform(20, 70), yy + rnd.uniform(-3, 3))], fill=color + (255,), width=rnd.randint(2, 6))
        yy = pad + rnd.uniform(0.05, 0.95) * h
        x0 = pad - rnd.uniform(0, 10)
        d.line([(x0, yy), (x0 - rnd.uniform(20, 60), yy)], fill=color + (255,), width=rnd.randint(2, 5))
    layer = layer.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.paste(layer, (int(x - pad), int(y - pad)), layer)


def brush_label(img, text, x, y, size=96, color=LIME, ink=INK, seed=1, center=False):
    d = ImageDraw.Draw(img)
    f = font("black_i", size)
    tw = d.textlength(text, font=f)
    bw, bh = tw + size * 0.7, size * 1.25
    if center:
        x = (img.width - bw) / 2
    brush(img, x, y, bw, bh, color, seed)
    d = ImageDraw.Draw(img)
    d.text((x + size * 0.32, y + size * 0.05), text, font=f, fill=ink)
    return x, y + bh, bw


def rich_lines(d, text, f, maxw):
    """Split into lines; words wrapped in *...* are highlighted (lime). Returns list of [(word, hl)]."""
    words, hl = [], False
    for raw in text.replace("\n", " \n ").split(" "):
        if raw == "\n":
            words.append(("\n", False)); continue
        if not raw:
            continue
        s = raw
        core = s.rstrip(".,!?:;)")
        start = s.startswith("*"); end = core.endswith("*") and len(core) > 1
        s = s.replace("*", "")
        if start:
            hl = True
        words.append((s, hl))
        if end:
            hl = False
    lines, cur = [], []
    for wd, h in words:
        if wd == "\n":
            lines.append(cur); cur = []; continue
        test = " ".join(x for x, _ in cur + [(wd, h)])
        if cur and d.textlength(test, font=f) > maxw:
            lines.append(cur); cur = []
        cur.append((wd, h))
    if cur:
        lines.append(cur)
    return lines


def rich_text(img, text, x, y, f, maxw, color=WHITE, hl=LIME, gap=1.08, center=False, shadow=True):
    d = ImageDraw.Draw(img)
    for ln in rich_lines(d, text, f, maxw):
        full = " ".join(w for w, _ in ln)
        xx = (img.width - d.textlength(full, font=f)) / 2 if center else x
        for i, (w, h) in enumerate(ln):
            s = w + (" " if i < len(ln) - 1 else "")
            if shadow:
                d.text((xx + 4, y + 5), s, font=f, fill=(0, 0, 0))
            d.text((xx, y), s, font=f, fill=hl if h else color)
            xx += d.textlength(s, font=f)
        y += int(f.size * gap)
    return y


def wrap(d, text, f, maxw):
    return [" ".join(w for w, _ in ln) for ln in rich_lines(d, text.replace("*", ""), f, maxw)]


def fa_icon(img, name, cx, cy, size, color=LIME):
    d = ImageDraw.Draw(img)
    ch = chr(int(FA_MAP.get(name, FA_MAP["bolt"]), 16))
    f = font("fa", size)
    bb = d.textbbox((0, 0), ch, font=f)
    d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), ch, font=f, fill=color)


def icon_circle(img, name, cx, cy, r=62):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 12, 12), outline=LIME, width=5)
    fa_icon(img, name, cx, cy, int(r * 0.95))


def item_rows(img, items, x, y, w, title_size=50, desc_size=36, r=58, gap=26):
    """items: [[fa_icon, title, desc], ...] rows with icon circles + divider lines."""
    d = ImageDraw.Draw(img)
    ft, fd = font("xbold", title_size), font("pop_m", desc_size)
    for i, (ic, t, ds) in enumerate(items):
        tx = x + r * 2 + 34
        dl = wrap(d, ds, fd, w - (tx - x)) if ds else []
        hgt = max(r * 2, title_size * 1.15 + len(dl) * desc_size * 1.18)
        icon_circle(img, ic, x + r, y + hgt / 2, r)
        yy = y + (hgt - (title_size * 1.15 + len(dl) * desc_size * 1.18)) / 2
        d.text((tx, yy), t, font=ft, fill=LIME)
        yy += title_size * 1.15
        for ln in dl:
            d.text((tx, yy), ln, font=fd, fill=WHITE); yy += desc_size * 1.18
        y += hgt + gap
        if i < len(items) - 1:
            d.line([(tx, y - gap / 2), (x + w, y - gap / 2)], fill=(60, 70, 40), width=2)
    return y


def hud_card(img, x, y, w, h, value, unit="", label="", icon="fire"):
    """Glassy HUD stat card like the Reels (lime outline)."""
    layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle([x, y, x + w, y + h], radius=24, fill=(10, 14, 12, 190), outline=LIME + (255,), width=4)
    img.paste(layer, (0, 0), layer)
    d = ImageDraw.Draw(img)
    fa_icon(img, icon, x + 62, y + h / 2, int(h * 0.38))
    fl = font("xbold", int(h * 0.17))
    d.text((x + 120, y + h * 0.16), label.upper(), font=fl, fill=GREY)
    fv = font("black_i", int(h * 0.42))
    d.text((x + 120, y + h * 0.36), value, font=fv, fill=WHITE)
    if unit:
        fu = font("xbold", int(h * 0.2))
        d.text((x + 128 + d.textlength(value, font=fv), y + h * 0.55), unit, font=fu, fill=LIME)


def torn_box(img, x, y, w, h, seed=5):
    brush(img, x, y, w, h, LIME, seed, angle=0)


def footer_actions(img, y):
    d = ImageDraw.Draw(img)
    W = img.width
    d.line([(50, y - 20), (W - 50, y - 20)], fill=(55, 60, 55), width=2)
    items = [("heart", "LIKE", "if this helped"), ("paper-plane", "SHARE", "with a friend"), ("bookmark", "SAVE", "for later")]
    cw = (W - 100) / 3
    for i, (ic, t, s) in enumerate(items):
        cx = 50 + cw * i
        fa_icon(img, ic, cx + 50, y + 45, 56)
        d.text((cx + 105, y + 8), t, font=font("xbold", 40), fill=WHITE)
        d.text((cx + 105, y + 56), s, font=font("pop_m", 27), fill=GREY)
        if i:
            d.line([(cx - 10, y), (cx - 10, y + 95)], fill=(55, 60, 55), width=2)
