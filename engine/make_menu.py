"""FitDecoded "nutrition menu" card: one saveable 1080x1350 image, like a restaurant menu
but with protein / calories per serving of everyday Indian foods.

Usage: python3 make_menu.py spec.json out.jpg

Spec:
{
 "label": "SAVE THIS MENU",
 "headline": "HIGH-PROTEIN *INDIAN* MENU",
 "sub": "Protein per serving · pick 1 in every meal",
 "photo": "FitDecoded_28.jpg",            # faint background photo from library/
 "value_label": "protein",                # word under the big lime number
 "columns": [
  {"name": "VEG", "icon": "leaf", "items": [
     ["1f9c0", "Paneer", "100 g", "~18g", "~265 kcal"],   # [emoji codepoint, name, serving, big value, small value]
     ...]},                                            # 4-6 items per column
  {"name": "NON-VEG", "icon": "drumstick-bite", "items": [...]}
 ],
 "addons_title": "EASY ADD-ONS",          # optional bottom strip, up to 3
 "addons": [["1f95b", "Milk 1 glass", "~8g"], ...],
 "tip": "Aim for ~20-30g protein in each main meal."
}
Emoji codepoints are Fluent 3D icons in engine/icons (run setup.sh). Headline: *word* = lime.
Every number must be a well-established approximate value (prefix "~").
"""
import json, os, sys
from PIL import Image, ImageDraw, ImageFilter
import fd2 as F

W, H = 1080, 1350
HERE = os.path.dirname(os.path.abspath(__file__))


def emoji(img, code, cx, cy, size):
    p = os.path.join(HERE, "icons", f"{code}.webp")
    if not os.path.exists(p):
        return
    e = Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)
    img.paste(e, (int(cx - size / 2), int(cy - size / 2)), e)


def rounded_panel(img, box, r=34):
    ov = Image.new("RGBA", img.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.rounded_rectangle(box, r, fill=(14, 18, 18, 215), outline=F.LIME + (255,), width=4)
    img.paste(ov, (0, 0), ov)


def fit_font(d, text, kind, size, maxw):
    while size > 18 and d.textlength(text, font=F.font(kind, size)) > maxw:
        size -= 2
    return F.font(kind, size)


def column(img, col, x, y, w, h, value_label):
    rounded_panel(img, [x, y, x + w, y + h])
    d = ImageDraw.Draw(img)
    # header
    fh = F.font("black_i", 46)
    tw = d.textlength(col["name"], font=fh)
    hx = x + (w - (tw + 80)) / 2
    F.icon_circle(img, col.get("icon", "leaf"), hx + 30, y + 52, 30)
    d.text((hx + 76, y + 22), col["name"], font=fh, fill=F.LIME)
    d.line([(x + 30, y + 100), (x + w - 30, y + 100)], fill=(70, 90, 40), width=2)
    items = col["items"]
    top, rh = y + 112, (h - 124) / len(items)
    for i, (code, name, serving, big, small) in enumerate(items):
        cy = top + rh * i + rh / 2
        r = min(52, rh * 0.38)
        d.ellipse([x + 22, cy - r, x + 22 + 2 * r, cy + r], fill=(8, 10, 10), outline=F.LIME, width=3)
        emoji(img, code, x + 22 + r, cy, int(r * 1.55))
        tx = x + 22 + 2 * r + 18
        vx = x + w - 22
        fb = F.font("black_i", 46)
        bw = d.textlength(big, font=fb)
        maxw = vx - bw - 12 - tx
        fn = fit_font(d, name, "xbold", 33, maxw)
        d.text((tx, cy - 40), name, font=fn, fill=F.WHITE)
        d.text((tx, cy + 2), serving, font=fit_font(d, serving, "pop_m", 24, maxw), fill=F.GREY)
        if small:
            d.text((tx, cy + 30), small, font=F.font("pop_m", 21), fill=(150, 160, 150))
        d.text((vx - bw, cy - 40), big, font=fb, fill=F.LIME)
        fl = F.font("pop_m", 20)
        d.text((vx - d.textlength(value_label, font=fl), cy + 12), value_label, font=fl, fill=F.GREY)
        if i < len(items) - 1:
            d.line([(tx, top + rh * (i + 1)), (x + w - 22, top + rh * (i + 1))], fill=(45, 55, 40), width=2)


def main(spec_path, out):
    s = json.load(open(spec_path))
    ph = F.clean_photo(s.get("photo", "FitDecoded_28.jpg"))
    ph = ph.crop((0, int(ph.height * 0.2), ph.width, ph.height))  # drop the baked-in logo
    img = F.cover(ph, W, H, (0.5, 0.3)).filter(ImageFilter.GaussianBlur(3))
    img = Image.blend(Image.new("RGB", (W, H), (10, 13, 14)), img, 0.22)
    d = ImageDraw.Draw(img)

    F.logo(img, 44, 30, scale=0.55, tagline=False)
    fh = F.font("pop_m", 26)
    d.text((W - 44 - d.textlength(F.HANDLE, font=fh), 58), F.HANDLE, font=fh, fill=F.GREY)

    _, y, _ = F.brush_label(img, s.get("label", "SAVE THIS MENU"), 0, 118, size=40, seed=4, center=True)
    y = F.rich_text(img, s["headline"].upper(), 0, y + 14, F.font("black_i", s.get("size", 76)), W - 80,
                    gap=1.0, center=True)
    d = ImageDraw.Draw(img)
    fs = F.font("pop_m", 30)
    d.text(((W - d.textlength(s["sub"], font=fs)) / 2, y + 6), s["sub"], font=fs, fill=F.WHITE)
    y += 60

    addons = s.get("addons") or []
    bottom = H - 70 - (150 if addons else 0) - (60 if s.get("tip") else 0)
    cols = s["columns"]
    gap = 22
    cw = (W - 2 * 36 - gap * (len(cols) - 1)) / len(cols)
    for i, col in enumerate(cols):
        column(img, col, 36 + i * (cw + gap), y, cw, bottom - y, s.get("value_label", "protein"))

    d = ImageDraw.Draw(img)
    y = bottom + 18
    if addons:
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
        ft = F.font("bold_i", 28)
        t = "TIP: " + s["tip"]
        d.text(((W - d.textlength(t, font=ft)) / 2, y + 4), t, font=ft, fill=F.WHITE)
    fb = F.font("xbold", 26)
    t = "SAVE  ·  SHARE  ·  FOLLOW FOR DAILY FOOD TIPS"
    d.text(((W - d.textlength(t, font=fb)) / 2, H - 52), t, font=fb, fill=F.LIME)
    img.save(out, quality=93)
    print("saved", out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
