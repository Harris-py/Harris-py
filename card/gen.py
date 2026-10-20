# Builds dark_mode.svg and light_mode.svg: ASCII art beside a neofetch-style card that types itself out.
# The card's content is info.txt (any length; the card grows to fit). Stats come from stats.json,
# which the GitHub Action refreshes daily. Standard library only. Usage: python3 gen.py
import json
import pathlib
import textwrap
from html import escape

HERE = pathlib.Path(__file__).parent
WIDTH = 60                      # characters per info line, so the values line up on the right
FONT, CW = 14, 8.43             # font size and the width of one monospace character at that size
ART_LH, INFO_LH = 17, 20        # line heights
ART_X, TOP, GAP = 22, 34, 34

THEMES = {
    'dark': dict(bg='#161B22', border='#30363D', text='#C9D1D9', key='#FFA657', value='#A5D6FF', dots='#616E7F', art='#C9D1D9', add='#3FB950'),
    'light': dict(bg='#F6F8FA', border='#D0D7DE', text='#24292F', key='#953800', value='#0A3069', dots='#C2CFDE', art='#24292F', add='#1A7F37'),
}


def kv(key, value):
    """'. Key: ....... value' padded to WIDTH; a value too long for one line wraps onto right-aligned lines."""
    room = WIDTH - len('. ') - len(key) - len(': ') - 2
    if len(value) <= room:
        pad = room - len(value) + 1
        return [[('dots', '. '), ('key', key), ('text', ': '), ('dots', '.' * pad + ' '), ('value', value)]]
    first = textwrap.wrap(value, room)[0]
    rest = textwrap.wrap(value[len(first):].strip(), WIDTH - 4)
    out = [[('dots', '. '), ('key', key), ('text', ': '), ('dots', '.' * (room - len(first) + 1) + ' '), ('value', first)]]
    for chunk in rest:   # continuation lines stay right-aligned under the value
        out.append([('dots', '. ' + ' ' * (WIDTH - 2 - len(chunk))), ('value', chunk)])
    return out


def lines(stats):
    out = []
    raw = [l.rstrip() for l in (HERE / 'info.txt').read_text().splitlines() if not l.startswith('# ')]
    while raw and not raw[0].strip():
        raw.pop(0)
    title, *body = raw or ['']
    out.append([('text', title + ' '), ('dots', '—' * (WIDTH - len(title) - 1))])
    for line in body:
        if not line.strip():
            out.append([('dots', '.')])
        elif line.startswith('== '):
            name = line[3:].strip()
            out.append([('text', '— ' + name + ' '), ('dots', '—' * (WIDTH - len(name) - 3))])
        elif line.strip() == '{stats}':
            out += kv('Repos', f"{stats['repos']} public")
            out += kv('Contributions', f"{stats['contributions']} in the last year")
            out += kv('Commits', f"{stats['commits']} in the last year")
            out += kv('Pull.Requests', f"{stats['prs']} in the last year")
        elif ':' in line:
            k, v = line.split(':', 1)
            out += kv(k.strip(), v.strip())
        else:
            out.append([('text', '. ' + line.strip())])
    return out


def svg(theme, stats):
    c = THEMES[theme]
    art = (HERE / 'art.txt').read_text().rstrip('\n').split('\n')
    info_x = ART_X + max(len(r) for r in art) * CW + GAP
    info = lines(stats)
    height = max(TOP + len(art) * ART_LH, TOP + len(info) * INFO_LH) + 18
    width = info_x + WIDTH * CW + 24
    o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height}" viewBox="0 0 {width:.0f} {height}" font-family="ui-monospace, SFMono-Regular, Consolas, \'Liberation Mono\', Menlo, monospace" font-size="{FONT}px">',
         '<style>',
         f'.a{{fill:{c["art"]};white-space:pre;opacity:0;animation:in .5s ease-out forwards}}',
         '@keyframes in{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}',
         f'.text{{fill:{c["text"]}}} .key{{fill:{c["key"]}}} .value{{fill:{c["value"]}}} .dots{{fill:{c["dots"]}}}',
         '.l{white-space:pre}',
         '.cur{animation:blink 1s steps(1) infinite}@keyframes blink{50%{opacity:0}}',
         '@media (prefers-reduced-motion: reduce){.a{animation:none;opacity:1}}',
         '</style>',
         f'<rect width="{width:.0f}" height="{height}" rx="15" fill="{c["bg"]}" stroke="{c["border"]}"/>']
    # The art scans in from the top, one row at a time; it sits in the middle of the card's height.
    art_top = TOP + max(0, (len(info) * INFO_LH - len(art) * ART_LH) // 2)
    for i, row in enumerate(art):
        o.append(f'<text class="a" x="{ART_X}" y="{art_top + i * ART_LH}" style="animation-delay:{i * .045:.3f}s" xml:space="preserve">{escape(row)}</text>')
    # The card types itself out line by line: each line is revealed by a clip that grows at a steady typing speed.
    # Longer cards type faster so the whole card always finishes in about 8 seconds.
    total = sum(sum(len(s) for _, s in p) for p in info)
    t, cps = 0.6, max(240, total / 7.5)
    o.append('<defs>')
    timing = []
    for i, parts in enumerate(info):
        n = sum(len(s) for _, s in parts)
        dur = max(n / cps, .05)
        o.append(f'<clipPath id="c{i}"><rect x="{info_x:.1f}" y="{TOP + i * INFO_LH - FONT - 2}" height="{INFO_LH + 2}" width="0">'
                 f'<animate attributeName="width" from="0" to="{n * CW + 4:.1f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        timing.append((t, dur, n))
        t += dur + .03
    o.append('</defs>')
    for i, parts in enumerate(info):
        spans = ''.join(f'<tspan class="{cls}">{escape(s)}</tspan>' for cls, s in parts)
        o.append(f'<text class="l" x="{info_x:.1f}" y="{TOP + i * INFO_LH}" clip-path="url(#c{i})" xml:space="preserve">{spans}</text>')
    # A cursor rides along the line being typed, then blinks after the last line.
    o.append(f'<rect class="cur" width="{CW:.1f}" height="{FONT + 2}" fill="{c["add"]}" x="{info_x:.1f}" y="{TOP - FONT + 1}">')
    for i, (start, dur, n) in enumerate(timing):
        o.append(f'<set attributeName="y" to="{TOP + i * INFO_LH - FONT + 1}" begin="{start:.2f}s"/>'
                 f'<animate attributeName="x" from="{info_x:.1f}" to="{info_x + n * CW:.1f}" begin="{start:.2f}s" dur="{dur:.2f}s" fill="freeze"/>')
    o.append('</rect>')
    o.append('</svg>')
    return '\n'.join(o)


if __name__ == '__main__':
    stats = json.loads((HERE / 'stats.json').read_text())
    for theme in THEMES:
        (HERE / f'{theme}_mode.svg').write_text(svg(theme, stats))
    print('wrote dark_mode.svg, light_mode.svg')
