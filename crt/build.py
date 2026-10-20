# Fill crt.src.html with the portrait grid and info.txt, writing crt.html.
import json, pathlib
here = pathlib.Path(__file__).parent
h = (here / 'crt.src.html').read_text()
h = h.replace('__PORTRAIT__', (here / 'portrait.json').read_text()).replace('__TEXT__', json.dumps((here / 'info.txt').read_text()))
(here / 'crt.html').write_text(h)
