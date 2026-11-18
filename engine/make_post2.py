"""FitDecoded v2 image carousel (1080x1350 JPEG), brand style on library photos.

Usage: python3 make_post2.py spec.json outprefix   -> outprefix_1.jpg ...

Spec:
{
 "topic": "...", "keyword": "RICE",
 "slides": [
  {"type": "cover", "photo": "FitDecoded_28.jpg", "focus": [0.5, 0.0], "label": "MYTH OR FACT?",
   "headline": "IS RICE WORSE THAN *ROTI?*", "question": "Swipe to decode the truth >"},
  {"type": "verdict", "photo": "FitDecoded_39.jpg", "verdict": "MYTH",
   "headline": "Rice doesn't make you fat. *Portions do.*", "stats": [["fire","~130","kcal","100g cooked rice"], ["fire","~120","kcal","1 medium roti"]]},
  {"type": "list", "photo": "FitDecoded_04.jpg", "label": "SCIENCE", "headline": "What actually *matters:*",
   "items": [["scale-balanced", "Total Calories", "Your daily total decides fat gain or loss."], ...]},   # 3-5 items
  {"type": "truth", "truth": "Both rice and roti fit in fat loss.", "focus": ["Watch the portion", "Add dal + sabzi", "Stay consistent"],
   "cta": "Comment RICE for my portion guide"}
 ]
}
Headline: wrap a word in *stars* to make it lime. Icons are Font Awesome solid names (see assets/fa_solid_map.json).
"""
import json, sys
from PIL import Image, ImageDraw
import fd2 as F

W, H = 1080, 1350


def slide_cover(s):
    ph = F.clean_photo(s["photo"])
    img = F.cover(ph, W, H, tuple(s.get("focus", [0.5, 0.0])))
    img = F.shade(img, top=0.0, bottom=0.95, start=0.38)
    y = 760
    _, y, _ = F.brush_label(img, s.get("label", "MYTH OR FACT?"), 60, y, size=62, seed=3)
    y = F.rich_text(img, s["headline"].upper(), 64, y + 24, F.font("black_i", s.get("size", 112)), W - 120, gap=1.02)
    if s.get("question"):
        d = ImageDraw.Draw(img)
        f = F.font("black_i", 46)
        lines = F.wrap(d, s["question"], f, W - 260)
        bh = len(lines) * 56 + 50
        by = max(y + 30, H - bh - 70)
        F.torn_box(img, 90, by, W - 180, bh, seed=9)
        d = ImageDraw.Draw(img)
        yy = by + 24
        for ln in lines:
            d.text(((W - d.textlength(ln, font=f)) / 2, yy), ln, font=f, fill=F.INK); yy += 56
    return img


def base_panel(s, page):
    ph = F.clean_photo(s["photo"]) if s.get("photo") else None
    img = F.dark_canvas(W, H, ph, "right")
    F.logo(img, 56, 46, 0.8)
    d = ImageDraw.Draw(img)
    f = F.font("xbold", 30)
    d.text((W - 60 - d.textlength(page, font=f), 70), page, font=f, fill=F.GREY)
    return img


def slide_verdict(s, page):
    img = base_panel(s, page)
    v = s.get("verdict", "MYTH").upper()
    col = F.LIME if v == "FACT" else (255, 82, 82)
    _, y, _ = F.brush_label(img, v, 60, 250, size=130, color=col, ink=F.INK if v == "FACT" else (255, 255, 255), seed=4)
    y = F.rich_text(img, s["headline"], 66, y + 40, F.font("black_i", 78), W - 140, gap=1.1)
    for i, st in enumerate(s.get("stats", [])[:3]):
        ic, val, unit, lab = st
        F.hud_card(img, 66, y + 50 + i * 190, 620, 160, val, unit, lab, ic)
    return img


def slide_list(s, page):
    img = base_panel(s, page)
    _, y, _ = F.brush_label(img, s.get("label", "SCIENCE"), 60, 240, size=84, seed=6)
    y = F.rich_text(img, s["headline"], 66, y + 30, F.font("black_i", 66), W - 140, gap=1.1)
    F.item_rows(img, s["items"][:5], 66, y + 40, W - 150)
    return img


def slide_truth(s, page, keyword):
    img = base_panel(s, page)
    d = ImageDraw.Draw(img)
    F.torn_box(img, 50, 250, W - 100, 330, seed=11)
    d = ImageDraw.Draw(img)
    F.fa_icon(img, "lightbulb", 125, 330, 70, F.INK)
    d.text((185, 290), "THE TRUTH:", font=F.font("black_i", 72), fill=F.INK)
    yy = 395
    for ln in F.wrap(d, s["truth"], F.font("bold_i", 48), W - 220):
        d.text((110, yy), ln, font=F.font("bold_i", 48), fill=F.INK); yy += 58
    y = 650
    F.fa_icon(img, "bullseye", 100, y + 40, 62)
    d.text((160, y), "FOCUS ON:", font=F.font("black_i", 66), fill=F.WHITE)
    y += 110
    for it in s.get("focus", [])[:4]:
        F.fa_icon(img, "check", 110, y + 26, 40)
        d.text((160, y), it, font=F.font("bold_i", 46), fill=F.WHITE); y += 72
    if s.get("cta") or keyword:
        cta = s.get("cta") or f'Comment "{keyword}"'
        f = F.font("black_i", 44)
        y += 20
        F.fa_icon(img, "comment", 100, y + 28, 52)
        for ln in F.wrap(d, cta, f, W - 220):
            d.text((160, y), ln, font=f, fill=F.LIME); y += 54
    F.footer_actions(img, H - 150)
    return img


def main():
    spec = json.load(open(sys.argv[1])); pre = sys.argv[2]
    slides = spec["slides"]; n = len(slides)
    for i, s in enumerate(slides, 1):
        page = f"{i}/{n}"
        t = s["type"]
        img = (slide_cover(s) if t == "cover" else slide_verdict(s, page) if t == "verdict"
               else slide_list(s, page) if t == "list" else slide_truth(s, page, spec.get("keyword")))
        img.convert("RGB").save(f"{pre}_{i}.jpg", "JPEG", quality=92)
    print("ok", n, "slides")


if __name__ == "__main__":
    main()
