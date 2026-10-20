# Builds dark_mode.svg and light_mode.svg: an ASCII portrait beside a neofetch-style card that types itself out.
# Stats come from stats.json (written daily by the GitHub Action); everything else is in INFO below.
# Standard library only. Usage: python3 gen.py
import json
import pathlib
from html import escape

HERE = pathlib.Path(__file__).parent
WIDTH = 60                      # characters per info line, so the values line up on the right
FONT, CW = 14, 8.43             # font size and the width of one monospace character at that size
ART_LH, INFO_LH = 17, 20        # line heights
ART_X, INFO_X, TOP = 22, 380, 34

INFO = [
    ('title', 'Harris-py'),
    ('kv', 'OS', 'macOS, Linux'),
    ('kv', 'Host', '127.0.0.1'),
    ('kv', 'Kernel', 'AI developer tools, local LLMs'),
    ('kv', 'IDE', 'Claude Code, Codex, VS Code'),
    ('gap',),
    ('kv', 'Languages.Programming', 'TypeScript, Python, C++'),
    ('kv', 'Languages.Systems', 'Vulkan, llama.cpp, Node'),
    ('kv', 'Languages.Protocols', 'MCP, JSON-RPC, Git'),
    ('gap',),
    ('kv', 'Creator.Of', 'Switchboard, hot-experts'),
    ('gap',),
    ('kv', 'Hobbies.Software', 'AI agents, LLM inference'),
    ('kv', 'Hobbies.Hardware', 'ESP32, Arduino'),
    ('section', 'Contact'),
    ('kv', 'GitHub', 'github.com/Harris-py'),
    ('section', 'GitHub Stats'),
    ('stats',),
]

THEMES = {
    'dark': dict(bg='#161B22', border='#30363D', text='#C9D1D9', key='#FFA657', value='#A5D6FF', dots='#616E7F', art='#C9D1D9', add='#3FB950'),
    'light': dict(bg='#F6F8FA', border='#D0D7DE', text='#24292F', key='#953800', value='#0A3069', dots='#C2CFDE', art='#24292F', add='#1A7F37'),
}


def kv(key, value):
    """'. Key: ....... value' padded to WIDTH, as (key, dots, value) parts."""
    pad = WIDTH - len('. ') - len(key) - len(': ') - len(value) - 1
    return [('dots', '. '), ('key', key), ('text', ': '), ('dots', '.' * max(pad, 1) + ' '), ('value', value)]


def lines(stats):
    out = []
    for item in INFO:
        kind = item[0]
        if kind == 'title':
            out.append([('text', item[1] + ' '), ('dots', '—' * (WIDTH - len(item[1]) - 1))])
        elif kind == 'section':
            out.append([('text', '— ' + item[1] + ' '), ('dots', '—' * (WIDTH - len(item[1]) - 3))])
        elif kind == 'gap':
            out.append([('dots', '.')])
        elif kind == 'kv':
            out.append(kv(item[1], item[2]))
        elif kind == 'stats':
            out.append(kv('Repos', f"{stats['repos']} public"))
            out.append(kv('Contributions', f"{stats['contributions']} in the last year"))
            out.append(kv('Commits', f"{stats['commits']} in the last year"))
            out.append(kv('Pull.Requests', f"{stats['prs']} in the last year"))
    return out


def svg(theme, stats):
    c = THEMES[theme]
    art = (HERE / ('art.txt' if theme == 'dark' else 'art_light.txt')).read_text().rstrip('\n').split('\n')
    info = lines(stats)
    height = max(TOP + len(art) * ART_LH, TOP + len(info) * INFO_LH) + 18
    width = INFO_X + WIDTH * CW + 24
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
    # The portrait scans in from the top, one row at a time.
    for i, row in enumerate(art):
        o.append(f'<text class="a" x="{ART_X}" y="{TOP + i * ART_LH}" style="animation-delay:{i * .045:.3f}s" xml:space="preserve">{escape(row)}</text>')
    # The card types itself out line by line: each line is revealed by a clip that grows at a steady typing speed.
    o.append('<defs>')
    t, cps = 0.6, 240                    # start time and characters per second
    timing = []
    for i, parts in enumerate(info):
        n = sum(len(s) for _, s in parts)
        dur = max(n / cps, .08)
        o.append(f'<clipPath id="c{i}"><rect x="{INFO_X}" y="{TOP + i * INFO_LH - FONT - 2}" height="{INFO_LH + 2}" width="0">'
                 f'<animate attributeName="width" from="0" to="{n * CW + 4:.1f}" begin="{t:.2f}s" dur="{dur:.2f}s" fill="freeze"/></rect></clipPath>')
        timing.append((t, dur, n))
        t += dur + .04
    o.append('</defs>')
    for i, parts in enumerate(info):
        spans = ''.join(f'<tspan class="{cls}">{escape(s)}</tspan>' for cls, s in parts)
        o.append(f'<text class="l" x="{INFO_X}" y="{TOP + i * INFO_LH}" clip-path="url(#c{i})" xml:space="preserve">{spans}</text>')
    # A cursor rides along the line being typed, then blinks after the last line.
    last = len(info) - 1
    o.append(f'<rect class="cur" width="{CW:.1f}" height="{FONT + 2}" fill="{c["add"]}" x="{INFO_X}" y="{TOP - FONT + 1}">')
    for i, (start, dur, n) in enumerate(timing):
        y = TOP + i * INFO_LH - FONT + 1
        o.append(f'<set attributeName="y" to="{y}" begin="{start:.2f}s"/>'
                 f'<animate attributeName="x" from="{INFO_X}" to="{INFO_X + n * CW:.1f}" begin="{start:.2f}s" dur="{dur:.2f}s" fill="freeze"/>')
    o.append('</rect>')
    o.append('</svg>')
    return '\n'.join(o)


if __name__ == '__main__':
    stats = json.loads((HERE / 'stats.json').read_text())
    for theme in THEMES:
        (HERE / f'{theme}_mode.svg').write_text(svg(theme, stats))
    print('wrote dark_mode.svg, light_mode.svg')
