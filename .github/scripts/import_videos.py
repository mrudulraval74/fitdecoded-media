"""Compress downloaded exercise clips and publish them as GitHub Release assets.

Usage: python3 import_videos.py RAW_DIR OUT_DIR

- RAW_DIR: the Drive folder as downloaded by gdown (subfolders like men/, girl/).
- Each .mp4 is re-encoded (max 720 px wide, H.264 CRF 26, no audio, faststart)
  and named <category>__<slug>.mp4 so names are unique and URL-safe.
- Assets go into releases named videos-<category>-<n> (max 900 per release,
  GitHub's limit is 1000), so the git repo itself stays small.
- Writes library/videos.json: one entry per clip with category, exercise name,
  public download URL and size.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = os.environ.get("GITHUB_REPOSITORY", "mrudulraval74/fitdecoded-media")
PER_RELEASE = 900


def slug(text):
    text = re.sub(r"\(\d+\)", "", text)
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or "clip"


def run(cmd):
    print("+", " ".join(cmd[:6]), "..." if len(cmd) > 6 else "", flush=True)
    subprocess.run(cmd, check=True)


def main(raw_dir, out_dir):
    raw, out = Path(raw_dir), Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    clips, used = [], set()
    for src in sorted(raw.rglob("*")):
        if src.suffix.lower() not in (".mp4", ".mov", ".m4v") or not src.is_file():
            continue
        rel = src.relative_to(raw).parts
        # category = the men / girl folder wherever it sits in the path
        dirs = [slug(p) for p in rel[:-1]]
        category = next((d for d in dirs if d in ("men", "girl")),
                        dirs[-1] if dirs else "misc")
        name = f"{category}__{slug(src.stem)}"
        base, n = name, 2
        while name in used:
            name = f"{base}-{n}"
            n += 1
        used.add(name)
        dst = out / f"{name}.mp4"
        try:
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-i", str(src),
                 "-vf", "scale='min(720,iw)':-2", "-c:v", "libx264",
                 "-preset", "veryfast", "-crf", "26", "-pix_fmt", "yuv420p",
                 "-an", "-movflags", "+faststart", str(dst)],
                check=True, timeout=300)
        except Exception as e:  # keep going; report at the end
            print(f"FAILED {src}: {e}", flush=True)
            continue
        if dst.stat().st_size > src.stat().st_size:  # keep the smaller one
            dst.write_bytes(src.read_bytes())
        clips.append({
            "file": dst.name,
            "category": category,
            "exercise": re.sub(r"\s*\(\d+\)\s*", "", src.stem).strip(),
            "source": "/".join(rel),
            "bytes": dst.stat().st_size,
        })

    by_cat = {}
    for c in clips:
        by_cat.setdefault(c["category"], []).append(c)
    for cat, items in by_cat.items():
        for i in range(0, len(items), PER_RELEASE):
            tag = f"videos-{cat}-{i // PER_RELEASE + 1}"
            exists = subprocess.run(["gh", "release", "view", tag, "-R", REPO],
                                    capture_output=True).returncode == 0
            if not exists:
                run(["gh", "release", "create", tag, "-R", REPO, "--title", tag,
                     "--notes", f"Exercise clips ({cat}). Index: library/videos.json"])
            chunk = items[i:i + PER_RELEASE]
            for j in range(0, len(chunk), 50):
                run(["gh", "release", "upload", tag, "-R", REPO, "--clobber"]
                    + [str(out / c["file"]) for c in chunk[j:j + 50]])
            for c in chunk:
                c["release"] = tag
                c["url"] = f"https://github.com/{REPO}/releases/download/{tag}/{c['file']}"

    Path("library").mkdir(exist_ok=True)
    Path("library/videos.json").write_text(json.dumps(clips, indent=1))
    total = sum(c["bytes"] for c in clips)
    print(f"DONE: {len(clips)} clips, {total / 1e9:.2f} GB, "
          + ", ".join(f"{k}={len(v)}" for k, v in by_cat.items()))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
