# card.json -> film.html (run export.py first).
import pathlib
here = pathlib.Path(__file__).parent
(here / 'film.html').write_text((here / 'film.src.html').read_text().replace('__CARD__', (here / 'card.json').read_text()))
