import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 640
BG = (13, 17, 23)
PANEL = (22, 27, 34)
BORDER = (48, 54, 61)
TEXT = (230, 237, 243)
DIM = (139, 148, 158)
BLUE = (88, 166, 255)
GREEN = (63, 185, 80)
RED = (248, 81, 73)

img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)


def font(size, bold=False):
    names = [
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for n in names:
        if os.path.exists(n):
            return ImageFont.truetype(n, size)
    return ImageFont.load_default()


# ---- background calibration grid -------------------------------------------------
step = 40
for x in range(0, W, step):
    d.line([(x, 0), (x, H)], fill=(19, 24, 31), width=1)
for y in range(0, H, step):
    d.line([(0, y), (W, y)], fill=(19, 24, 31), width=1)

# ---- left: reticle + drift ------------------------------------------------------
cx, cy, r = 330, H // 2, 150
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(33, 38, 45), width=2)
d.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2],
          outline=(63, 185, 80, 90), width=2)

for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
    a = (cx + dx * (r + 14), cy + dy * (r + 14))
    b = (cx + dx * (r - 26), cy + dy * (r - 26))
    d.line([a, b], fill=GREEN, width=4)

# drift trail wandering toward the lower-right
pts = [(cx - 70, cy + 10), (cx - 20, cy - 40), (cx + 30, cy + 25), (cx + 82, cy - 34)]
for i in range(len(pts) - 1):
    shade = tuple(int(RED[j] * (0.35 + 0.65 * (i + 1) / len(pts))) for j in range(3))
    d.line([pts[i], pts[i + 1]], fill=shade, width=6)
d.ellipse([pts[-1][0] - 11, pts[-1][1] - 11, pts[-1][0] + 11, pts[-1][1] + 11], fill=RED)
d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=BLUE)

# ---- right: wordmark ------------------------------------------------------------
tx = 580
y = 150
d.text((tx, y), "DUALSENSE", font=font(74, bold=True), fill=TEXT)
y += 82
d.text((tx, y), "DRIFT LAB", font=font(74, bold=True), fill=BLUE)

y += 116
d.text((tx, y), "Measure it.  Back it up.  Recentre it.", font=font(30), fill=DIM)
y += 54
d.text((tx, y), "In-browser stick-drift diagnostics for the PS5 DualSense.", font=font(26), fill=DIM)

# ---- chips ----------------------------------------------------------------------
chip_y = y + 56
chips = [("WebHID", BLUE), ("USB", DIM), ("Volatile by default", GREEN), ("MIT", DIM)]
cx0 = tx
for label, col in chips:
    f = font(23, bold=True)
    tw = d.textlength(label, font=f)
    box = [cx0, chip_y, cx0 + tw + 34, chip_y + 46]
    d.rounded_rectangle(box, radius=23, outline=col, width=2)
    d.text((cx0 + 17, chip_y + 10), label, font=f, fill=col)
    cx0 += tw + 52

# ---- bottom rule ----------------------------------------------------------------
d.line([(0, H - 6), (W, H - 6)], fill=BLUE, width=6)

img.save("assets/social-preview.png", "PNG")
print("wrote assets/social-preview.png", img.size, os.path.getsize("assets/social-preview.png"), "bytes")
