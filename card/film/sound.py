# Synthesised soundtrack: a soft pad plus one sound per cue in events.json (written by `node render.mjs events`).
# Usage: python3 sound.py events.json sound.wav [duration]
import json, sys, wave
import numpy as np
EV, OUT = sys.argv[1], sys.argv[2]
SR, DUR = 48000, float(sys.argv[3]) if len(sys.argv) > 3 else 46.0
n = int(SR * DUR); t = np.arange(n) / SR; out = np.zeros(n)
rng = np.random.default_rng(7)

def add(at, sig, gain=1.0):
    i = int(at * SR); j = min(n, i + len(sig))
    if i < n: out[i:j] += gain * sig[: j - i]
def env(d, a=.004, r=None):
    k = np.arange(int(d * SR)) / SR; return np.minimum(1, k / a) * np.exp(-k / (r or d / 4))
def tone(f, d, a=.004, r=None, h=(1, .3, .1)):
    k = np.arange(int(d * SR)) / SR; return env(d, a, r) * sum(w * np.sin(2 * np.pi * f * (i + 1) * k) for i, w in enumerate(h))
def pop(f=900): return tone(f, .12, .002, .025, (1, .2))
def key():
    d = .03; k = np.arange(int(d * SR)) / SR; x = rng.standard_normal(len(k))
    return np.diff(np.concatenate([[0], x])) * np.exp(-k / .004) * .6 + tone(rng.uniform(1800, 2600), d, .001, .004, (1,)) * .3
def whoosh(d=.7, lo=300, hi=2500):
    k = np.arange(int(d * SR)) / SR; x = rng.standard_normal(len(k))
    fc = lo + (hi - lo) * np.sin(np.pi * k / d); a = 1 - np.exp(-2 * np.pi * fc / SR); y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s += a[i] * (x[i] - s); y[i] = s
    return y * np.sin(np.pi * k / d) ** 2
def chime(fs, d=1.4): return sum(tone(f, d, .005, d / 3, (1, .15, .05)) for f in fs) / len(fs)
def thud():
    k = np.arange(int(.5 * SR)) / SR; f = 140 * np.exp(-k * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-k * 7)

# pad: slow swell, a chord change at the feature grid, fade at the end
for f, g in [(110, .5), (164.8, .35), (220, .3), (277.2, .18), (329.6, .15)]:
    out += g * .045 * np.sin(2 * np.pi * f * t + np.sin(2 * np.pi * .2 * t)) * np.minimum(1, t / 2.5) * np.clip((DUR - t) / 3, 0, 1) * np.where(t < 25, 1, .6)
for f, g in [(146.8, .4), (220, .3), (293.7, .2), (370, .15)]:
    out += g * .045 * np.sin(2 * np.pi * f * t) * np.clip((t - 25) / 1.5, 0, 1) * np.clip((DUR - t) / 3, 0, 1)

CH = [[659.3, 830.6, 987.8], [587.3, 740, 880], [523.3, 659.3, 784.0, 1046.5], [440, 554.4, 659.3, 880]]
for at, kind, arg in json.load(open(EV)):
    if kind == 'pop': add(at, pop(arg), .3)
    elif kind == 'key': add(at, key(), .18)
    elif kind == 'line': add(at, pop(1500), .07)
    elif kind == 'ok': add(at, tone(1318.5, .25, .003, .06, (1, .2)), .18)
    elif kind == 'err': add(at, tone(220, .3, .003, .08, (1, .5, .25)), .25)
    elif kind == 'thud': add(at, thud(), .7)
    elif kind == 'whoosh': add(at, whoosh(1.4 if arg else .7, 400, 3500 if arg else 2200), .32)
    elif kind == 'click': add(at, pop(500), .5)
    elif kind == 'chime': add(at, chime(CH[arg], 3.5 if arg == 3 else 1.6), .4)

out = out / np.max(np.abs(out)) * .85
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([out, out], 1) * 32767).astype('<i2').tobytes())
