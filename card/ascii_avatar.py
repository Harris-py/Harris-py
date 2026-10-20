# Flat avatar -> ASCII art for the neofetch card: head outline and features drawn, background blank.
# Usage: ascii_avatar.py avatar.png cols [--light]
import sys
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
im = Image.open(sys.argv[1]).convert('RGB').crop((150, 150, 1000, 1080))
cols = int(sys.argv[2]); rows = int(cols * im.height / im.width * 0.5)
a = np.asarray(im).astype(int); r, g, b = a[..., 0], a[..., 1], a[..., 2]
white = (r > 200) & (g > 200) & (b > 200); green = (g > 120) & (g > r + 30); dark = ~white & ~green
m = Image.fromarray((dark * 255).astype('uint8')).copy(); ImageDraw.floodfill(m, (2, 2), 128)
bg = np.asarray(m) == 128
cls = np.where(bg, 0, np.where(green, 1, np.where(white, 2, 3)))   # 0 bg, 1 head, 2 rims, 3 lenses/lines
edge = np.asarray(Image.fromarray((cls * 60).astype('uint8')).filter(ImageFilter.FIND_EDGES)) > 0
def cell(y0, y1, x0, x1):
    c = cls[y0:y1, x0:x1]; e = edge[y0:y1, x0:x1].mean()
    f = [(c == k).mean() for k in range(4)]
    if f[0] > .85: return ' '
    if f[3] > .5: return '@'                     # lenses, nose and mouth
    if f[2] > .45: return '='                    # white rims
    if f[3] > .2 or f[2] > .2: return '+'
    if f[0] > .04: return '#' if f[1] > .35 else '+'          # where the head meets the background
    k = (y0 * 7 + x0 * 3) // 37 % 9                          # sparse dotted fill, like the reference
    return '.' if k == 0 else '-' if k == 4 else ' '
H, W = cls.shape; out = []
for i in range(rows):
    y0, y1 = i * H // rows, (i + 1) * H // rows
    out.append(''.join(cell(y0, y1, j * W // cols, (j + 1) * W // cols) for j in range(cols)).rstrip())
print('\n'.join(out))
