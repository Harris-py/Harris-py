# CRT profile card

`../profile-crt.gif` is rendered from code here, in the style of yetone's green-phosphor profile.

- `avatar.svg`: the avatar, redrawn as a vector.
- `portrait_avatar.py`: turns it into a grid of CRT tones (`portrait.json`).
- `crt.src.html`: the whole animation on a canvas, a pure function of time. Edit `INFO` and `PROMPT` near the top to change the text.
- `render.mjs`: steps through the animation in headless Chromium and writes a lossless video.

```bash
node rast.mjs "$PWD/avatar.svg" avatar.png
python3 portrait_avatar.py avatar.png
python3 -c "open('crt.html','w').write(open('crt.src.html').read().replace('__PORTRAIT__', open('portrait.json').read()))"
node render.mjs stills 10 stills/          # check one frame
node render.mjs video crt.mkv 12
ffmpeg -i crt.mkv -vf "split[a][b];[a]palettegen=max_colors=64:stats_mode=diff[p];[b][p]paletteuse=dither=none:diff_mode=rectangle" -loop 0 ../profile-crt.gif
```

Needs Node with Playwright, Python with Pillow and numpy, and ffmpeg. Font: VT323 (SIL Open Font License).
