# Flat avatar -> CRT tone grid: black background -> panel green (-1), green head -> light, white rims -> white, black lines/lenses -> dark.
import json, sys
from PIL import Image, ImageDraw
import numpy as np
im = Image.open(sys.argv[1]).convert('RGB')
a = np.asarray(im).astype(int)
r, g, b = a[..., 0], a[..., 1], a[..., 2]
white = (r > 200) & (g > 200) & (b > 200)
green = (g > 120) & (g > r + 30)
dark = ~white & ~green
# background = the black region touching the border; lenses and lines stay inside the head
bgmask = Image.fromarray((dark * 255).astype('uint8')).copy()   # copy: floodfill needs a writable image
ImageDraw.floodfill(bgmask, (2, 2), 128)
bg = np.asarray(bgmask) == 128
level = np.where(bg, -1.0, np.where(white, 1.0, np.where(green, 0.8, 0.0)))
box = (150, 130, 1000, 1080)                      # keeps the panel's 428x480 shape
W, H = 107, 120
crop = level[box[1]:box[3], box[0]:box[2]]
# area-average each 4px cell; mostly-background cells stay background, edges keep a dithered mix
img_bg = Image.fromarray(((crop < -.5) * 255).astype('uint8')).resize((W, H), Image.BOX)
img_v = Image.fromarray((np.clip(crop, 0, 1) * 255).astype('uint8')).resize((W, H), Image.BOX)
isbg = np.asarray(img_bg) / 255 > .5
v = np.asarray(img_v) / 255 / np.maximum(1e-3, 1 - np.asarray(img_bg) / 255)
out = np.where(isbg, -1, np.round(np.clip(v, 0, 1), 2))
json.dump({'w': W, 'h': H, 'px': out.flatten().tolist()}, open('portrait.json', 'w'))
print('ok', isbg.mean())
