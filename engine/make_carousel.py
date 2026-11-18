"""Build carousel slides (1080x1350 JPEG) from the same Reel spec.
Usage: python3 make_carousel.py spec.json outprefix  -> outprefix_1.jpg ...
"""
import json, sys
from PIL import ImageDraw
import render_reel as R

spec = json.load(open(sys.argv[1])); pre = sys.argv[2]
slides = [s for s in spec["scenes"] if s.get("type") != "quiz"]
n = len(slides)
for i, s in enumerate(slides, 1):
    img = R.frame(s, s["dur"] + 5, 0.01, 1)  # final state of the scene
    img = img.crop((0, 250, 1080, 1600))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 1080, 95], fill=R.BG1)
    f = R.font(R.F_BOLD, 34)
    d.text((60, 36), "FITDECODED", font=f, fill=R.ACCENT)
    pg = f"{i}/{n}"
    d.text((1020 - d.textlength(pg, font=f), 36), pg, font=f, fill=R.GREY)
    if i < n:
        sw = "SWIPE >"
        d.text((1020 - d.textlength(pg, font=f) - 40 - d.textlength(sw, font=f), 36), sw, font=f, fill=R.ACCENT)
    img.save(f"{pre}_{i}.jpg", "JPEG", quality=92)
print("ok", n, "slides")
