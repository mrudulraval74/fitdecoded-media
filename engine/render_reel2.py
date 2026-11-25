"""FitDecoded v2 Reel (1080x1920, 30fps, music) in brand style on library photos.

Usage: python3 render_reel2.py spec.json out.mp4 [cover.jpg]

Spec: {"topic": "...", "keyword": "VEG", "scenes": [ ... ]}
Scene types (all except cta take "photo": library file name, optional "focus": [x, y], optional "sub": subtitle line):
  hook    : label, headline (use *word* for lime), hud: [icon, value, unit, label] (optional)
  quiz    : question, seconds (3)
  reveal  : verdict ("MYTH"/"FACT"), headline
  explain : label, headline, stats: [[icon, value, unit, label], ...] (0-2)
  list    : label, items: [[fa_icon, title, desc], ...] (3-4)
  cta     : keyword, body  (or head + tag for a question CTA, e.g. head "COMMENT YOUR PICK", tag "RICE or ROTI?")
Durations ("dur") ~2.5-5 s each; total 22-30 s.
"""
import json, math, os, subprocess, sys
from PIL import Image, ImageDraw, ImageFilter
import fd2 as F
from render_reel import make_audio

W, H, FPS = 1080, 1920, 30
RED = (255, 82, 82)
_photo_cache = {}


def ease(t):
    t = max(0.0, min(1.0, t)); return 1 - (1 - t) ** 3


def pop(t):
    t = max(0.0, min(1.0, t)); return 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2


def bg(s, t, dur, dark=0.0):
    key = (s["photo"], tuple(s.get("focus", [0.5, 0.3])))
    if key not in _photo_cache:
        ph = F.clean_photo(s["photo"])
        ph = ph.crop((0, int(ph.height * 0.16), ph.width, ph.height))  # drop the baked-in logo
        base = F.cover(ph, int(W * 1.12), int(H * 1.12), key[1])
        _photo_cache[key] = base
    base = _photo_cache[key]
    z = 1.0 + 0.10 * (t / max(dur, 0.1))          # slow Ken Burns zoom
    cw, ch = int(base.width / z / 1.0), int(base.height / z / 1.0)
    cw, ch = min(base.width, int(W * 1.12 / z)), min(base.height, int(H * 1.12 / z))
    x = (base.width - cw) // 2; y = (base.height - ch) // 2
    img = base.crop((x, y, x + cw, y + ch)).resize((W, H), Image.BILINEAR)
    img = F.shade(img, top=0.75, bottom=0.92, start=0.30)
    if dark:
        img = Image.blend(img, Image.new("RGB", (W, H), F.INK), dark)
    return img


def anim_paste(img, layer, t0, t, dx=-120):
    """Slide+fade an RGBA layer in starting at t0."""
    a = ease((t - t0) / 0.35)
    if a <= 0:
        return
    off = int(dx * (1 - a))
    if a < 1:
        alpha = layer.split()[3].point(lambda v: int(v * a))
        layer = layer.copy(); layer.putalpha(alpha)
    img.paste(layer, (off, 0), layer)


def layer():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def subtitle(img, text, t):
    if not text:
        return
    a = ease((t - 0.2) / 0.3)
    if a <= 0:
        return
    d = ImageDraw.Draw(img)
    f = F.font("pop_m", 42)
    lines = F.wrap(d, text, f, W - 220)
    y = H - 230 - len(lines) * 60
    for ln in lines:
        tw = d.textlength(ln, font=f)
        d.rounded_rectangle([(W - tw) / 2 - 18, y - 6, (W + tw) / 2 + 18, y + 52], radius=10, fill=(0, 0, 0))
        d.text(((W - tw) / 2, y), ln, font=f, fill=F.WHITE)
        y += 60


_layer_cache = {}


def static_layer(key, fn):
    if key not in _layer_cache:
        L = layer(); fn(L); _layer_cache[key] = L
    return _layer_cache[key]


def frame(s, si, t, gt, total):
    ty = s["type"]; dur = s["dur"]
    if ty == "cta":
        img = F.dark_canvas(W, H)
    else:
        img = bg(s, t, dur, dark=0.35 if ty in ("quiz", "list") else 0.0)
    if ty != "cta":
        F.logo(img, 60, 70, 0.75, tagline=False)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, int(W * gt / total), 10], fill=F.LIME)

    if ty == "hook":
        L1 = static_layer((si, 1), lambda L: F.brush_label(L, s.get("label", "MYTH OR FACT?"), 70, 860, size=70, seed=3))
        L2 = static_layer((si, 2), lambda L: F.rich_text(L, s["headline"].upper(), 74, 980, F.font("black_i", s.get("size", 116)), W - 140, gap=1.0))
        anim_paste(img, L1, 0.0, t); anim_paste(img, L2, 0.25, t, dx=0)
        if s.get("hud"):
            k = pop((t - 0.8) / 0.4)
            if k > 0.05:
                L3 = static_layer((si, 3), lambda L: F.hud_card(L, 560, 300, 460, 150, *s["hud"][1:], icon=s["hud"][0]))
                anim_paste(img, L3, 0.8, t, dx=200)

    elif ty == "quiz":
        secs = s.get("seconds", 3)
        L1 = static_layer((si, 1), lambda L: F.rich_text(L, s.get("question", "WHAT DO YOU THINK?"), 0, 520, F.font("black_i", 104), W - 120, center=True))
        anim_paste(img, L1, 0, t, dx=0)
        d.text(((W - d.textlength("Guess before the timer ends!", font=F.font("pop_m", 46))) / 2, 790), "Guess before the timer ends!", font=F.font("pop_m", 46), fill=F.GREY)
        k = pop((t - 0.25) / 0.4)
        if k > 0.05:
            Lb = static_layer((si, 2), lambda L: (F.brush_label(L, "MYTH", 110, 960, size=110, color=RED, ink=(255, 255, 255), seed=7),
                                                  F.brush_label(L, "FACT", 600, 960, size=110, seed=8)))
            anim_paste(img, Lb, 0.25, t, dx=0)
        cx, cy, r = W / 2, 1360, 140
        rem = max(0.0, secs - t)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(10, 12, 12), outline=(50, 60, 40), width=16)
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * rem / secs, fill=F.LIME, width=16)
        num = str(int(math.ceil(rem))) if rem > 0 else "0"
        fn = F.font("black_i", int(150 * (1.25 - 0.25 * ease((t % 1.0) / 0.3))))
        bb = d.textbbox((0, 0), num, font=fn)
        d.text((cx - (bb[0] + bb[2]) / 2, cy - (bb[1] + bb[3]) / 2), num, font=fn, fill=F.WHITE)

    elif ty == "reveal":
        v = s["verdict"].upper(); good = v == "FACT"
        if t < 0.12:
            img.paste(Image.new("RGB", (W, H), F.LIME if good else RED), (0, 0), Image.new("L", (W, H), 70))
        k = pop(t / 0.35)
        Lv = static_layer((si, 1), lambda L: F.brush_label(L, v, 0, 900, size=190, color=F.LIME if good else RED,
                                                            ink=F.INK if good else (255, 255, 255), seed=4, center=True))
        if k > 0.02:
            sc = max(0.05, k)
            if abs(sc - 1) > 0.01:
                Lz = Lv.resize((int(W * sc), int(H * sc)), Image.BILINEAR)
                img.paste(Lz, (int((W - Lz.width) / 2), int((H - Lz.height) / 2 + (1 - sc) * 0)), Lz)
            else:
                img.paste(Lv, (0, 0), Lv)
        L2 = static_layer((si, 2), lambda L: F.rich_text(L, s["headline"], 0, 1220, F.font("black_i", 76), W - 140, center=True, gap=1.1))
        anim_paste(img, L2, 0.45, t, dx=0)

    elif ty == "explain":
        L1 = static_layer((si, 1), lambda L: F.brush_label(L, s.get("label", "SCIENCE"), 70, 860, size=80, seed=6))
        L2 = static_layer((si, 2), lambda L: F.rich_text(L, s["headline"], 74, 1000, F.font("black_i", 82), W - 150, gap=1.08))
        anim_paste(img, L1, 0, t); anim_paste(img, L2, 0.3, t, dx=0)
        for i, st in enumerate(s.get("stats", [])[:2]):
            Ls = static_layer((si, 10 + i), lambda L, st=st, i=i: F.hud_card(L, 560 - i * 0, 260 + i * 190, 470, 160, st[1], st[2], st[3], st[0]))
            anim_paste(img, Ls, 0.8 + i * 0.35, t, dx=220)

    elif ty == "list":
        L1 = static_layer((si, 1), lambda L: F.brush_label(L, s.get("label", "WHAT TO DO"), 70, 420, size=84, seed=5))
        anim_paste(img, L1, 0, t)
        items = s["items"][:4]
        step = max(0.45, (dur - 1.2) / len(items))
        y0 = 620
        for i, it in enumerate(items):
            Li = static_layer((si, 20 + i), lambda L, it=it, i=i: F.item_rows(L, [it], 80, y0 + i * 230, W - 160, title_size=56, desc_size=40, r=70))
            anim_paste(img, Li, 0.3 + i * step, t)

    elif ty == "cta":
        F.logo(img, 120, 330, 1.25)
        d = ImageDraw.Draw(img)
        k = pop((t - 0.2) / 0.4)
        head = s.get("head", "COMMENT")
        tag = s.get("tag", f'"{s.get("keyword", "")}"')
        hf = F.font("black_i", 120 if len(head) <= 9 else 84)
        d.text(((W - d.textlength(head, font=hf)) / 2, 680), head, font=hf, fill=F.WHITE)
        if k > 0.05:
            Lk = static_layer((si, 1), lambda L: F.brush_label(L, tag, 0, 840, size=150 if len(tag) <= 10 else 100, seed=12, center=True))
            anim_paste(img, Lk, 0.2, t, dx=0)
        L2 = static_layer((si, 2), lambda L: F.rich_text(L, s.get("body", ""), 0, 1080, F.font("bold_i", 56), W - 180, center=True, gap=1.2, shadow=False))
        anim_paste(img, L2, 0.6, t, dx=0)
        icons = [("heart", "LIKE"), ("paper-plane", "SHARE"), ("user-plus", "FOLLOW")]
        for i, (ic, lab) in enumerate(icons):
            a = (t - 1.0 - i * 0.2) / 0.3
            if a <= 0:
                continue
            cx = 230 + i * 310
            F.icon_circle(img, ic, cx, 1430, int(80 * min(1, pop(a))))
            f = F.font("xbold", 40)
            d.text((cx - d.textlength(lab, font=f) / 2, 1540), lab, font=f, fill=F.WHITE)
        f = F.font("xbold", 46)
        d.text(((W - d.textlength(F.HANDLE, font=f)) / 2, 1660), F.HANDLE, font=f, fill=F.LIME)

    if ty != "cta":
        subtitle(img, s.get("sub", ""), t)
    return img


def main():
    spec = json.load(open(sys.argv[1]))
    out, cover = sys.argv[2], (sys.argv[3] if len(sys.argv) > 3 else None)
    scenes = spec["scenes"]
    total = sum(s["dur"] for s in scenes)
    cuts, acc = [], 0
    for s in scenes:
        cuts.append(acc); acc += s["dur"]
    wav = out + ".wav"
    make_audio(wav, total, cuts)
    proc = subprocess.Popen(
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
         "-i", "-", "-i", wav, "-shortest", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out], stdin=subprocess.PIPE)
    gt = 0.0
    for si, s in enumerate(scenes):
        for i in range(int(round(s["dur"] * FPS))):
            t = i / FPS
            proc.stdin.write(frame(s, si, t, gt + t, total).convert("RGB").tobytes())
        gt += s["dur"]
    proc.stdin.close(); proc.wait(); os.remove(wav)
    if cover:
        frame(scenes[0], 0, scenes[0]["dur"] - 0.05, 0.01, total).convert("RGB").save(cover, "JPEG", quality=92)
    print("ok", out, f"{total:.1f}s")


if __name__ == "__main__":
    main()
