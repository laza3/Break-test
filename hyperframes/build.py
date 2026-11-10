#!/usr/bin/env python3
"""Inline fonts + images into the HyperFrames composition (single self-contained HTML)."""
import base64, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
FONTS = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "fonts")

def b64(path):
    with open(path, "rb") as fh:
        return base64.b64encode(fh.read()).decode("ascii")

subs = {
    "__F_ANTON__": b64(os.path.join(FONTS, "Anton-400.woff2")),
    "__F_BC600__": b64(os.path.join(FONTS, "BarlowCondensed-600.woff2")),
    "__F_BC800__": b64(os.path.join(FONTS, "BarlowCondensed-800.woff2")),
    "__F_SM400__": b64(os.path.join(FONTS, "SpaceMono-400.woff2")),
    "__F_SM700__": b64(os.path.join(FONTS, "SpaceMono-700.woff2")),
    "__IMG_A__":   b64(os.path.join(REPO, "assets", "01-pool-hall-wide.jpg")),
    "__IMG_B__":   b64(os.path.join(REPO, "assets", "02-billard-lounge.jpg")),
    "__IMG_C__":   b64(os.path.join(REPO, "assets", "03-bar-coffee.jpg")),
    "__IMG_D__":   b64(os.path.join(REPO, "assets", "04-logo-restaurant.jpg")),
}

with open(os.path.join(HERE, "template.html"), encoding="utf-8") as fh:
    html = fh.read()

for key, val in subs.items():
    if key not in html:
        raise SystemExit("placeholder missing: " + key)
    html = html.replace(key, val)

out = os.path.join(HERE, "index.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(html)
print("wrote %s (%.2f MB)" % (out, os.path.getsize(out) / 1e6))
