"""FitDecoded interactive Reel renderer (1080x1920, 30fps MP4 with music).

Usage: python3 render_reel.py spec.json out.mp4 [cover.jpg]

Scene types (key "type"):
  hook     : tag, title, icons[]          big question with floating 3D icons
  quiz     : question, seconds            MYTH vs FACT buttons + countdown ring ("guess now!")
  reveal   : answer ("MYTH"/"FACT"), body, icon
  explain  : tag, title, body, icons[]
  compare  : tag, left{icon,label,sub,good}, right{...}
  bullets  : tag, items[[emoji, text], ...]
  cta      : keyword, body
"""
import json, subprocess, sys, math, os, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BG1, BG2 = (10, 13, 18), (16, 40, 32)
ACCENT = (57, 255, 136)
RED = (255, 77, 77)
WHITE = (245, 247, 250)
GREY = (175, 185, 195)
HERE = os.path.dirname(os.path.abspath(__file__))
FD = "/usr/share/fonts/truetype/google-fonts/"
F_TITLE = FD + "ofl/anton/Anton-Regular.ttf"
F_BOLD = FD + "Poppins-Bold.ttf"
F_MED = FD + "Poppins-Medium.ttf"
HANDLE = "@fitdecoded.india"
_icon_cache, _font_cache = {}, {}


def font(path, size):
    k = (path, size)
    if k not in _font_cache:
        _font_cache[k] = ImageFont.truetype(path, size)
    return _font_cache[k]


def icon(emoji, size):
    k = (emoji, size)
    if k in _icon_cache:
        return _icon_cache[k]
    cps = [f"{ord(c):x}" for c in emoji]
    names = ["-".join(cps), "-".join(c for c in cps if c != "fe0f"), "-".join(c for c in cps if c != "fe0f") + "-fe0f"]
    for n in names:
        p = os.path.join(HERE, "icons", n + ".webp")
        if os.path.exists(p):
            im = Image.open(p).convert("RGBA").resize((size, size), Image.LANCZOS)
            _icon_cache[k] = im
            return im
    raise FileNotFoundError(f"no icon for {emoji!r} ({names})")


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def pop(t):
    """overshoot scale 0->1.15->1"""
    t = max(0.0, min(1.0, t))
    return 1 + 2.70158 * (t - 1) ** 3 + 1.70158 * (t - 1) ** 2


def mix(c, a):
    return tuple(int(BG1[i] + (c[i] - BG1[i]) * max(0, min(1, a))) for i in range(3))


_bg_base = None


def background(t):
    global _bg_base
    if _bg_base is None:
        g = Image.new("RGB", (W, H * 2), BG1)
        d = ImageDraw.Draw(g)
        for r in range(1000, 0, -25):
            a = (1 - r / 1000) ** 2
            d.ellipse([W // 2 - r, H - r, W // 2 + r, H + r], fill=tuple(int(BG1[i] + (BG2[i] - BG1[i]) * a) for i in range(3)))
        _bg_base = g
    off = int(H * 0.5 + H * 0.12 * math.sin(t * 0.5))
    return _bg_base.crop((0, off, W, off + H)).copy()


def paste_icon(img, emoji, size, cx, cy, scale=1.0, rot=0.0):
    s = max(4, int(size * scale))
    im = icon(emoji, size)
    if s != size:
        im = im.resize((s, s), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    # soft shadow
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    sh.putalpha(im.split()[3].point(lambda a: int(a * 0.45)))
    sh = sh.filter(ImageFilter.GaussianBlur(14))
    img.paste((0, 0, 0), (int(cx - im.width / 2 + 10), int(cy - im.height / 2 + 24)), sh)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


def wrap(d, text, fnt, maxw):
    out = []
    for para in text.split("\n"):
        line = ""
        for w in para.split():
            test = (line + " " + w).strip()
            if d.textlength(test, font=fnt) <= maxw:
                line = test
            else:
                if line:
                    out.append(line)
                line = w
        out.append(line)
    return out


def text_block(d, text, fnt, y, color, a, gap=1.12, maxw=W - 160):
    off = int((1 - ease(a)) * 50)
    for ln in wrap(d, text, fnt, maxw):
        d.text(((W - d.textlength(ln, font=fnt)) / 2, y + off), ln, font=fnt, fill=mix(color, ease(a)))
        y += int(fnt.size * gap)
    return y


def tag(d, text, y, a, color=ACCENT):
    f = font(F_BOLD, 44)
    tw = d.textlength(text, font=f)
    d.rounded_rectangle([(W - tw) / 2 - 34, y, (W + tw) / 2 + 34, y + 78], radius=39, fill=mix(color, ease(a)))
    d.text(((W - tw) / 2, y + 10), text, font=f, fill=BG1)
    return y + 130


def chrome(img, d, gt, total):
    d.rectangle([0, 0, int(W * gt / total), 12], fill=ACCENT)
    f = font(F_BOLD, 34)
    d.text(((W - d.textlength("FITDECODED", font=f)) / 2, 70), "FITDECODED", font=f, fill=ACCENT)


def button(d, cx, cy, label, color, scale=1.0, filled=False, dim=False):
    f = font(F_TITLE, int(110 * scale))
    tw = d.textlength(label, font=f)
    w2, h2 = tw / 2 + 60 * scale, 95 * scale
    col = mix(color, 0.3 if dim else 1)
    if filled:
        d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], radius=int(40 * scale), fill=col)
        d.text((cx - tw / 2, cy - f.size * 0.62), label, font=f, fill=BG1)
    else:
        d.rounded_rectangle([cx - w2, cy - h2, cx + w2, cy + h2], radius=int(40 * scale), outline=col, width=10)
        d.text((cx - tw / 2, cy - f.size * 0.62), label, font=f, fill=col)


def frame(s, t, gt, total):
    img = background(gt)
    d = ImageDraw.Draw(img)
    chrome(img, d, gt, total)
    ty = s.get("type", "explain")
    dur = s["dur"]

    if ty == "hook":
        y = tag(d, s.get("tag", "MYTH OR FACT?"), 360, t / 0.3)
        y = text_block(d, s["title"], font(F_TITLE, s.get("title_size", 150)), y, WHITE, (t - 0.1) / 0.4)
        icons = s.get("icons", [])
        n = len(icons)
        for i, e in enumerate(icons):
            cx = W / 2 + (i - (n - 1) / 2) * 330
            cy = y + 260 + 25 * math.sin(gt * 3 + i)
            paste_icon(img, e, 300, cx, cy, pop((t - 0.35 - i * 0.15) / 0.45), rot=8 * math.sin(gt * 2 + i))

    elif ty == "quiz":
        secs = s.get("seconds", 3)
        f = font(F_TITLE, 110)
        y = text_block(d, s.get("question", "MYTH OR FACT?"), f, 400, WHITE, t / 0.3)
        text_block(d, "Guess before the timer ends!", font(F_MED, 50), y + 10, GREY, (t - 0.2) / 0.3)
        k = pop((t - 0.25) / 0.4)
        button(d, W * 0.29, 1050, "MYTH", RED, max(0.01, k))
        button(d, W * 0.71, 1050, "FACT", ACCENT, max(0.01, k))
        # countdown ring
        cx, cy, r = W / 2, 1420, 140
        rem = max(0.0, secs - t)
        frac = rem / secs
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(40, 50, 55), width=18)
        d.arc([cx - r, cy - r, cx + r, cy + r], -90, -90 + 360 * frac, fill=ACCENT, width=18)
        num = str(int(math.ceil(rem))) if rem > 0 else "0"
        sub = t % 1.0
        fn = font(F_TITLE, int(150 * (1.25 - 0.25 * ease(sub / 0.3))))
        d.text((cx - d.textlength(num, font=fn) / 2, cy - fn.size * 0.62), num, font=fn, fill=WHITE)
        paste_icon(img, "🤔", 170, W - 170, 1420 + 15 * math.sin(gt * 4), pop((t - 0.5) / 0.4))

    elif ty == "reveal":
        ans = s["answer"].upper()
        good = ans == "FACT"
        col = ACCENT if good else RED
        # flash
        if t < 0.15:
            d.rectangle([0, 0, W, H], fill=mix(col, 0.25))
            chrome(img, d, gt, total)
        k = pop(t / 0.4)
        shake = int(18 * math.sin(t * 60) * max(0, 1 - t / 0.4))
        button(d, W * 0.29 + (shake if not good else 0), 560, "MYTH", RED, 1.0 if not good else 0.8, filled=not good, dim=good)
        button(d, W * 0.71 + (shake if good else 0), 560, "FACT", ACCENT, 1.0 if good else 0.8, filled=good, dim=not good)
        paste_icon(img, "✅" if good else "❌", 340, W / 2, 960, k)
        if s.get("body"):
            text_block(d, s["body"], font(F_BOLD, 64), 1230, WHITE, (t - 0.45) / 0.4)
        f = font(F_MED, 46)
        msg = "Guessed right? Comment below"
        text_block(d, msg, f, 1500, ACCENT, (t - 0.9) / 0.4)

    elif ty == "explain":
        y = tag(d, s.get("tag", "THE SCIENCE"), 360, t / 0.3)
        y = text_block(d, s["title"], font(F_TITLE, s.get("title_size", 120)), y, WHITE, (t - 0.1) / 0.4) + 30
        y = text_block(d, s.get("body", ""), font(F_MED, 52), y, GREY, (t - 0.45) / 0.4, gap=1.35) + 40
        icons = s.get("icons", [])
        n = len(icons)
        for i, e in enumerate(icons):
            cx = W / 2 + (i - (n - 1) / 2) * 300
            paste_icon(img, e, 260, cx, max(y + 170, 1250) + 18 * math.sin(gt * 3 + i), pop((t - 0.7 - i * 0.2) / 0.45))

    elif ty == "compare":
        y = tag(d, s.get("tag", "WHICH IS WORSE?"), 360, t / 0.3)
        for j, side in enumerate([s["left"], s["right"]]):
            a = (t - 0.3 - j * 0.6) / 0.45
            if a <= 0:
                continue
            cx = W * (0.27 if j == 0 else 0.73)
            x0, x1 = cx - 230, cx + 230
            yo = int((1 - ease(a)) * 100)
            col = ACCENT if side.get("good") else RED
            d.rounded_rectangle([x0, 560 + yo, x1, 1420 + yo], radius=44, fill=(22, 28, 34), outline=mix(col, ease(a)), width=8)
            paste_icon(img, side["icon"], 250, cx, 760 + yo + 12 * math.sin(gt * 3 + j), pop(a))
            fl = font(F_TITLE, 78)
            yy = 960 + yo
            for ln in wrap(d, side["label"], fl, 420):
                d.text((cx - d.textlength(ln, font=fl) / 2, yy), ln, font=fl, fill=WHITE)
                yy += 88
            fs = font(F_MED, 42)
            for ln in wrap(d, side.get("sub", ""), fs, 410):
                d.text((cx - d.textlength(ln, font=fs) / 2, yy + 10), ln, font=fs, fill=GREY)
                yy += 54
            mark = "✅" if side.get("good") else "❌"
            paste_icon(img, mark, 130, cx, 1420 + yo, pop((t - 1.6 - j * 0.3) / 0.35))
        if s.get("footer"):
            text_block(d, s["footer"], font(F_BOLD, 56), 1490, WHITE, (t - 2.2) / 0.4)

    elif ty == "bullets":
        y = tag(d, s.get("tag", "WHAT TO DO"), 360, t / 0.3) + 40
        items = s["items"]
        step = max(0.55, (dur - 1.4) / len(items))
        fb = font(F_BOLD, 58)
        for i, (e, txt) in enumerate(items):
            a = (t - 0.35 - i * step) / 0.4
            lines = wrap(d, txt, fb, W - 380)
            hgt = max(190, len(lines) * 76 + 70)
            if a > 0:
                off = int((1 - ease(a)) * 120)
                d.rounded_rectangle([70 + off, y, W - 70 + off, y + hgt], radius=36, fill=(22, 30, 34))
                paste_icon(img, e, 140, 170 + off, y + hgt / 2, pop(a))
                yy = y + (hgt - len(lines) * 76) / 2 - 6
                for ln in lines:
                    d.text((270 + off, yy), ln, font=fb, fill=WHITE)
                    yy += 76
            y += hgt + 36

    elif ty == "cta":
        paste_icon(img, "💬", 300, W / 2, 560 + 20 * math.sin(gt * 3), pop(t / 0.45))
        y = text_block(d, "COMMENT", font(F_TITLE, 120), 790, WHITE, (t - 0.2) / 0.4)
        kw = f'"{s["keyword"]}"'
        fk = font(F_TITLE, 170)
        k = pop((t - 0.4) / 0.45)
        tw = d.textlength(kw, font=fk)
        if k > 0.05:
            d.rounded_rectangle([(W - tw) / 2 - 40, y, (W + tw) / 2 + 40, y + 230], radius=40, fill=ACCENT)
            d.text(((W - tw) / 2, y + 10), kw, font=fk, fill=BG1)
        y = text_block(d, s.get("body", ""), font(F_MED, 54), y + 280, WHITE, (t - 0.7) / 0.4, gap=1.3)
        text_block(d, "FOLLOW " + HANDLE, font(F_BOLD, 58), 1480, ACCENT, (t - 1.1) / 0.4)
    return img


# ---------------- audio: simple upbeat loop + pops on scene changes ----------------
def make_audio(path, total, cut_times, bpm=112, sr=44100):
    n = int(total * sr)
    out = np.zeros(n)
    beat = 60 / bpm
    tt = np.arange(int(0.25 * sr)) / sr
    kick = np.sin(2 * np.pi * (55 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 9)
    hat = np.random.RandomState(1).randn(int(0.05 * sr)) * np.exp(-np.arange(int(0.05 * sr)) / sr * 80) * 0.25
    chords = [[220.0, 261.6, 329.6], [174.6, 220.0, 261.6], [196.0, 246.9, 293.7], [164.8, 196.0, 246.9]]
    b = 0
    while b * beat < total:
        i = int(b * beat * sr)
        seg = kick[: max(0, min(len(kick), n - i))]
        out[i:i + len(seg)] += seg * 0.55
        j = int((b + 0.5) * beat * sr)
        if j < n:
            sg = hat[: n - j]
            out[j:j + len(sg)] += sg
        if b % 4 == 0:
            ch = chords[(b // 4) % 4]
            L = int(4 * beat * sr)
            tl = np.arange(min(L, n - i)) / sr
            env = np.minimum(1, tl * 4) * np.exp(-tl * 0.5)
            pad = sum(np.sin(2 * np.pi * f * tl) + 0.3 * np.sin(4 * np.pi * f * tl) for f in ch) * env * 0.05
            out[i:i + len(pad)] += pad
        b += 1
    tp = np.arange(int(0.12 * sr)) / sr
    popsnd = np.sin(2 * np.pi * (500 + 900 * tp / 0.12) * tp) * np.exp(-tp * 35) * 0.35
    for c in cut_times:
        i = int(c * sr)
        sg = popsnd[: max(0, n - i)]
        out[i:i + len(sg)] += sg
    fade = int(0.8 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / max(1e-9, np.abs(out).max()) * 0.6
    data = (out * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(data.tobytes())


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
        ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
         "-r", str(FPS), "-i", "-", "-i", wav, "-shortest", "-c:v", "libx264", "-preset", "veryfast",
         "-crf", "20", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        stdin=subprocess.PIPE)
    gt = 0.0
    for s in scenes:
        for i in range(int(round(s["dur"] * FPS))):
            t = i / FPS
            proc.stdin.write(frame(s, t, gt + t, total).tobytes())
        gt += s["dur"]
    proc.stdin.close(); proc.wait()
    os.remove(wav)
    if cover:
        frame(scenes[0], 3, 0.01, total).save(cover, "JPEG", quality=92)
    print("ok", out, f"{total:.1f}s")


if __name__ == "__main__":
    main()
