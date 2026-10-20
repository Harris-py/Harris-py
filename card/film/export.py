# Writes card.json (the card's art and lines, exactly as gen.py lays them out) for the animated film.
import importlib.util, json, pathlib
here = pathlib.Path(__file__).parent
spec = importlib.util.spec_from_file_location('gen', here.parent / 'gen.py'); gen = importlib.util.module_from_spec(spec); spec.loader.exec_module(gen)
stats = json.loads((here.parent / 'stats.json').read_text())
art = (here.parent / 'art.txt').read_text().rstrip('\n').split('\n')
(here / 'card.json').write_text(json.dumps({'art': art, 'lines': gen.lines(stats), 'width': gen.WIDTH}))
print(len(art), 'art rows,', len(gen.lines(stats)), 'lines')
