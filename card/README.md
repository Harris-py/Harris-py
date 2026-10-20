# Profile card

Edit `info.txt` (any length; the card grows to fit) and push. The Action rebuilds `dark_mode.svg` and `light_mode.svg` and refreshes the stats daily. To rebuild by hand: `python3 gen.py`.

`art.txt` is the ASCII art; `ascii_avatar.py avatar.png 44` regenerates it from the avatar (see `../crt/avatar.svg`).

`card.gif` (the profile header) is the same card as a short film: `film/` renders it with the same method as the Switchboard demo (an HTML page that is a pure function of time, stepped through by Playwright, encoded with ffmpeg). The Action re-renders it daily. `card-demo.mp4` is a version with sound for posting elsewhere.
