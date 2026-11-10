import os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import T, DURATION

SR = 44100
TAIL = 2.0
N = int((DURATION + TAIL) * SR)
rng = np.random.default_rng(41)

S_L = np.zeros(N); S_R = np.zeros(N)          # sfx (reverb)
M_L = np.zeros(N); M_R = np.zeros(N)          # melodic music (sidechained)
D_L = np.zeros(N); D_R = np.zeros(N)          # drums


def place(sig, t, gain=1.0, pan=0.0, bus="sfx"):
    i = int(round(t * SR))
    if i < 0 or i >= N:
        return
    n = min(len(sig), N - i)
    th = (pan + 1.0) * np.pi / 4.0
    gl, gr = gain * np.cos(th), gain * np.sin(th)
    L, R = {"sfx": (S_L, S_R), "music": (M_L, M_R), "drum": (D_L, D_R)}[bus]
    L[i:i + n] += sig[:n] * gl
    R[i:i + n] += sig[:n] * gr


def lowpass(x, fc, order=2):
    b, a = signal.butter(order, min(fc, SR * 0.45) / (SR / 2), "low")
    return signal.lfilter(b, a, x)


def highpass(x, fc, order=2):
    b, a = signal.butter(order, fc / (SR / 2), "high")
    return signal.lfilter(b, a, x)


def bandpass(x, lo, hi, order=2):
    b, a = signal.butter(order, [lo / (SR / 2), min(hi, SR * 0.45) / (SR / 2)], "band")
    return signal.lfilter(b, a, x)


def svf_band(x, fc, q=0.8):
    out = np.zeros_like(x)
    low = band = 0.0
    qi = 1.0 / q
    f_arr = 2.0 * np.sin(np.pi * np.minimum(fc, SR * 0.2) / SR)
    for i in range(len(x)):
        f = f_arr[i]
        low += f * band
        high = x[i] - low - qi * band
        band += f * high
        out[i] = band
    return out


# ------------------------------- SFX -------------------------------
def whoosh(dur=0.6, f0=300, f1=3500, q=0.8, peak=0.6):
    n = int(dur * SR)
    y = svf_band(rng.standard_normal(n), np.geomspace(f0, f1, n), q)
    y /= (np.max(np.abs(y)) + 1e-9)
    t = np.linspace(0, 1, n)
    return y * np.sin(np.pi * np.power(t, peak)) ** 2


def swipe(dur=0.16, f0=1800, f1=7000, amp=1.0):
    n = int(dur * SR)
    y = svf_band(rng.standard_normal(n), np.geomspace(f0, f1, n), 1.4)
    y /= (np.max(np.abs(y)) + 1e-9)
    t = np.linspace(0, 1, n)
    return y * np.sin(np.pi * np.power(t, 0.5)) ** 2 * amp


def fm_bell(f, dur=0.7, idx=2.2, ratio=2.0, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    mod = np.sin(2 * np.pi * f * ratio * t) * idx * np.exp(-t / 0.07)
    s = np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 0.20)
    s += 0.25 * np.sin(2 * np.pi * f * 2.0 * t) * np.exp(-t / 0.10)
    s *= np.minimum(1, t / 0.003)
    return s * amp * 0.8


def tick(f=2600, dur=0.035, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    nz = np.diff(rng.standard_normal(n + 1)) * np.exp(-t / 0.0035)
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.006)
    return (nz * 0.35 + s * 0.65) * amp


def thud(f0=130, f1=42, dur=0.7):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f1 + (f0 - f1) * np.exp(-t / 0.07)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2)
    s = np.tanh(2.2 * s) * 0.75
    nz = lowpass(rng.standard_normal(n), 400) * np.exp(-t / 0.03) * 0.6
    return s + nz


def tap(f=170, dur=0.16):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.035)
    c = lowpass(rng.standard_normal(n), 1500) * np.exp(-t / 0.004) * 0.5
    return (s + c) * np.minimum(1, t / 0.002)


def chime(f=1319, dur=1.4, amp=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m, a, tau in ((1.0, 1.0, 0.55), (2.0, 0.32, 0.32), (3.01, 0.16, 0.2), (4.2, 0.07, 0.12)):
        s += a * np.sin(2 * np.pi * f * m * t) * np.exp(-t / tau)
    return s * np.minimum(1, t / 0.004) * amp * 0.7


def click():
    a = tick(1700, 0.04, 1.0); b = tick(1000, 0.04, 0.8)
    out = np.zeros(int(0.12 * SR))
    out[:len(a)] += a
    j = int(0.07 * SR); out[j:j + len(b)] += b
    th = tap(150, 0.1) * 0.6; out[:len(th)] += th
    return out


def sparkle(n_blips=7, span=0.35, amp=0.6):
    n = int((span + 0.25) * SR)
    out = np.zeros(n)
    for _ in range(n_blips):
        f = rng.uniform(2600, 6200)
        st = int(rng.uniform(0, span) * SR)
        d = int(0.16 * SR)
        t = np.arange(d) / SR
        b = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.045) * np.minimum(1, t / 0.002)
        out[st:st + d] += b[:max(0, min(d, n - st))] * rng.uniform(0.4, 1.0)
    return out * amp


def glide(f0, f1, dur, amp=1.0):
    n = int(dur * SR)
    s = np.sin(2 * np.pi * np.cumsum(np.geomspace(f0, f1, n)) / SR)
    return s * (np.sin(np.pi * np.linspace(0, 1, n)) ** 1.5) * amp


def riser(dur=0.65, f_hi=7000):
    n = int(dur * SR)
    y = svf_band(rng.standard_normal(n), np.geomspace(250, f_hi, n), 1.2)
    y /= (np.max(np.abs(y)) + 1e-9)
    t = np.linspace(0, 1, n)
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(220, 1800, n)) / SR) * 0.3
    return (y * 0.9 + tone) * t ** 2.2


def zap(dur=0.14):
    n = int(dur * SR)
    t = np.arange(n) / SR
    y = svf_band(rng.standard_normal(n), np.geomspace(5000, 900, n), 2.5)
    y /= (np.max(np.abs(y)) + 1e-9)
    return y * np.exp(-t / 0.05)


def crash(dur=1.8):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = highpass(rng.standard_normal(n), 3500, 2)
    return x * np.exp(-t / 0.55) * np.minimum(1, t / 0.002) * 0.6


def reverse_swell(dur=0.8, f=2000):
    """Noise swell that grows into a hit (like a reversed cymbal)."""
    n = int(dur * SR)
    t = np.linspace(0, 1, n)
    x = bandpass(rng.standard_normal(n), 900, 9000)
    return x * t ** 3


# ------------------------------ MUSIC v2 (uplifting, clearly audible) ------------------------------
def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

def saw(f, n_samp, harmonics=None, phase=0.0):
    t = np.arange(n_samp) / SR
    kmax = harmonics or max(1, min(40, int(16000 / max(f, 1))))
    s = np.zeros(n_samp)
    for k in range(1, kmax + 1):
        s += np.sin(2 * np.pi * f * k * t + phase * k) / k
    return s * 0.55

def kick():
    n = int(0.42 * SR); t = np.arange(n) / SR
    f = 48 + 130 * np.exp(-t / 0.03)
    s = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.17))
    c = lowpass(rng.standard_normal(n), 4000) * np.exp(-t / 0.003) * 0.4
    return s + c

def clap(vel=1.0):
    n = int(0.25 * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 1000, 5000)
    env = np.exp(-t / 0.09)
    for off in (0.0, 0.012, 0.025):
        j = int(off * SR); env[j:j + int(0.006 * SR)] += 1.3
    return x * env * 0.6 * vel

def hat(open_=False, vel=1.0):
    d = 0.18 if open_ else 0.045; n = int(d * SR); t = np.arange(n) / SR
    return highpass(rng.standard_normal(n), 7500, 2) * np.exp(-t / (0.07 if open_ else 0.013)) * vel

def shaker(vel=1.0):
    n = int(0.08 * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 5000, 12000)
    return x * np.sin(np.pi * t / t[-1]) ** 2 * vel * 0.5

def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * saw(f * 2, n, 8)
    s = lowpass(np.tanh(1.4 * s), 900)
    env = np.minimum(1, t / 0.005) * np.exp(-t / (dur * 1.2)) * np.minimum(1, (dur - t) / 0.02)
    return s * env * 0.8

def pad(freqs, dur, vel=1.0, cutoff=2200):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.25, 0.0, 0.25):
            ff = f * 2 ** (det / 12)
            s += saw(ff, n, 10, rng.uniform(0, 6))
    s = lowpass(s, cutoff, 2)
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.25)
    return s * env * vel / (len(freqs) * 3)

def pluck(f, dur=0.32):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in ((1, 1.0), (2, 0.45), (3, 0.3), (4, 0.15), (5, 0.12)):
        s += a * np.sin(2 * np.pi * f * k * t) * np.exp(-t / (0.16 / k ** 0.5))
    return s * np.minimum(1, t / 0.002) * 0.6

CHORDS = {"C": [60, 64, 67], "G": [55, 59, 62, 67], "Am": [57, 60, 64], "F": [53, 57, 60, 65]}
ROOTS = {"C": 36, "G": 31, "Am": 33, "F": 29}
PROG = ["C", "G", "Am", "F"] * 3
# lead hook: (beat offset within bar, midi, length in beats) — one 2-bar phrase repeated
HOOK = [[(0, 72, .5), (0.5, 76, .5), (1, 79, .5), (1.5, 84, .5), (2.5, 83, .5), (3, 79, 1)],
        [(0, 81, .5), (0.5, 79, .5), (1, 76, .5), (2, 77, .5), (2.5, 76, .5), (3, 74, .5), (3.5, 72, .5)]]
PROG = ["C", "Am", "F", "G"] * 3
BAR = 2.0; BEAT = 0.5
DROP = T["drop"]; END = T["pill"]; FILL0 = 17.0; GAP = (17.5, 18.0)
def in_rng(t, r): return r[0] <= t < r[1]
kick_times = []

for b in range(11):
    ch = PROG[b]
    vel = 0.85 if b == 0 else (0.8 if b < 3 else 1.0)
    cut = 900 + b * 160 if b < 2 else (2600 if b < 9 else 3200)
    if in_rng(b * BAR, GAP): continue
    place(pad([note(m) for m in CHORDS[ch]], 2.2, vel, cut), b * BAR, 1.0, 0.0, "music")
place(pad([note(m) for m in CHORDS["C"] + [72]], 2.0 + TAIL - 0.2, 1.1, 2600), END, 1.0, 0.0, "music")

# drums
t = 0.0
while t < END - 1e-6:
    beat_in_bar = round((t % BAR) / BEAT, 3)
    if not in_rng(t, GAP):
        if t >= 1.0:
            if abs(t * 2 - round(t * 2)) < 1e-6:            # on beats
                place(kick(), t, 0.95, 0.0, "drum"); kick_times.append(t)
            if t >= 6.0 and abs((t % 1.0) - 0.5) < 1e-6:     # beats 2 & 4
                place(clap(1.0), t, 0.55, 0.0, "drum")
            off = abs((t % 0.5) - 0.25) < 1e-6
            if off:
                place(hat(t >= 10.0 and abs((t % 1.0) - 0.75) < 1e-6, 0.9), t, 0.28, 0.25, "drum")
            if t >= 10.0:
                place(shaker(0.8), t, 0.18, -0.3, "drum")
        else:
            if abs((t % 0.5) - 0.25) < 1e-6:
                place(hat(False, 0.5), t, 0.18, 0.2, "drum")
    t = round(t + 0.125, 4) if t >= 10.0 else round(t + 0.25, 4)
for k in range(8):
    place(clap(0.35 + 0.08 * k), FILL0 + k * 0.0625, 0.45, 0.0, "drum")
place(kick(), END, 1.0, 0.0, "drum"); kick_times.append(END)

# bass: offbeat-driven pattern
for b in range(1, 11):
    r = note(ROOTS[PROG[b]])
    for off, dur, mul in ((0.0, 0.22, 1), (0.25, 0.2, 1), (0.75, 0.2, 2), (1.0, 0.22, 1), (1.25, 0.2, 1), (1.5, 0.2, 1), (1.75, 0.2, 2)):
        tt = b * BAR + off
        if in_rng(tt, GAP) or tt >= END: continue
        place(bass(r * mul, dur), tt, 0.55, 0.0, "music")
place(bass(note(36), 1.6), END, 0.6, 0.0, "music")

# lead hook from bar 3 (6 s), octave up in the drop
for b in range(3, 11):
    phrase = HOOK[(b - 3) % 2]
    for off, m, ln in phrase:
        tt = b * BAR + off * BEAT
        if in_rng(tt, (FILL0 + 0.5, DROP)) or tt >= END: continue
        mm = m + (12 if b >= 9 else 0)
        g = 0.20 if b < 9 else 0.24
        place(pluck(note(mm), max(0.25, ln * BEAT * 1.4)), tt, g, -0.15, "music")
        place(pluck(note(mm) * 1.003, max(0.25, ln * BEAT * 1.4)), tt + 0.012, g * 0.6, 0.25, "music")

# intro arpeggio so the first second is not quiet
for k, m in enumerate([67, 72, 76, 79, 84, 79, 76, 72]):
    place(pluck(note(m), 0.3), k * 0.125, 0.45, (k % 2 - 0.5) * 0.4, "music")
place(pad([note(m) for m in [60, 64, 67, 72]], 1.2, 1.0, 2400), 0.0, 1.6, 0.0, "music")
# sidechain (lighter than before so the music stays present)
duck = np.ones(N); seg = int(0.4 * SR)
ds = 1.0 - 0.45 * np.exp(-(np.arange(seg) / SR) / 0.09)
for kt in kick_times:
    i = int(kt * SR); m = min(seg, N - i)
    if m > 0: duck[i:i + m] = np.minimum(duck[i:i + m], ds[:m])
M_L *= duck; M_R *= duck

# =============================== SFX v2 ===============================
def boom(dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 38 + 70 * np.exp(-t / 0.08)
    s = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.45))
    nz = lowpass(rng.standard_normal(n), 300) * np.exp(-t / 0.12) * 0.5
    return s + nz

def snap():
    n = int(0.06 * SR); t = np.arange(n) / SR
    return highpass(rng.standard_normal(n), 2500) * np.exp(-t / 0.008)

def glass(f=3200, dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.06) + 0.4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.03)
    return s * np.minimum(1, t / 0.001) * 0.6

def marker(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 900, 3200)
    env = np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.06) * (0.8 + 0.2 * np.sin(2 * np.pi * 9 * t))
    return x * env * 0.45

def thock():
    n = int(0.07 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * rng.uniform(170, 210) * t) * np.exp(-t / 0.012)
    clk = bandpass(rng.standard_normal(n), 700, 2600) * np.exp(-t / 0.006)
    return body * 0.8 + clk * 0.7

def shimmer_up(dur=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for k, f0 in enumerate((880, 1320, 1760)):
        f = np.geomspace(f0 * 0.7, f0 * 1.4, n)
        s += np.sin(2 * np.pi * np.cumsum(f) / SR + k) * (0.6 - 0.15 * k)
    env = np.sin(np.pi * np.linspace(0, 1, n)) ** 1.2
    return s * env * 0.5

def soft_whoosh(dur=0.5, f0=400, f1=2500):
    return whoosh(dur, f0, f1, q=0.7, peak=0.5)

SFX = 0.9
def sp(sig, t, g=1.0, pan=0.0): place(sig, t, g * SFX, pan)

def hop(dur=0.18):
    """Small rising swish for a hop (upward pitch, no 'bloop')."""
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.geomspace(500, 1400, n)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) ** 2
    return s * 0.35 + swipe(dur, 1500, 6000, 0.6) * 0.6

def crumble(dur=1.4):
    """Hundreds of tiny clicks thinning out = pixels raining down."""
    n = int(dur * SR); out = np.zeros(n)
    for k in range(220):
        tt = (rng.random() ** 1.8) * (dur - 0.05)
        j = int(tt * SR); c = tick(rng.uniform(1500, 6000), 0.02, rng.uniform(0.2, 0.9))
        out[j:j + len(c)] += c[:max(0, min(len(c), n - j))]
    return out * 0.5

def gravel(dur=0.5):
    n = int(dur * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 300, 2500) * (rng.random(n) < 0.08)
    return lowpass(x, 3000) * np.exp(-t / 0.2) * 3

def motor(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = 0.6 * np.sin(2 * np.pi * 62 * t) + 0.3 * np.sin(2 * np.pi * 124 * t) + 0.15 * np.sin(2 * np.pi * 186 * t)
    s *= 0.7 + 0.3 * np.sin(2 * np.pi * 9 * t)
    nz = bandpass(rng.standard_normal(n), 200, 900) * 0.25
    env = np.minimum(1, t / 0.08) * np.minimum(1, (dur - t) / 0.12)
    return (s + nz) * env * 0.5

def clank():
    n = int(0.6 * SR); t = np.arange(n) / SR
    s = np.zeros(n)
    for f, a, tau in ((420, 1, .12), (1130, .6, .08), (2210, .4, .05), (3170, .25, .04)):
        s += a * np.sin(2 * np.pi * f * t) * np.exp(-t / tau)
    return s * 0.35 * np.minimum(1, t / 0.001)


# =============================== day SFX: camera viewfinder ===============================
def slide_grind(dur=0.5, f0=600, f1=1400, seed=3):  # plastic slider handle gliding: filtered noise + soft rail rumble
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    fc = np.linspace(f0, f1, n)
    x = svf_band(r.standard_normal(n), fc, 1.6) * 0.8 + np.sin(2 * np.pi * np.cumsum(fc * 0.12) / SR) * 0.15
    return x * np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.7 * 0.6
def notch_click(f=2200):  # slider snaps into place
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008) + highpass(rng.standard_normal(n), 3000) * np.exp(-t / 0.004) * 0.6) * 0.8
def chip8(notes, step=0.07, amp=0.5):  # 8-bit square jingle for the old site
    out = np.zeros(int((len(notes) * step + 0.1) * SR))
    for k, m in enumerate(notes):
        n = int(step * SR); t = np.arange(n) / SR
        sq = np.sign(np.sin(2 * np.pi * note(m) * t)) * np.exp(-t / 0.09) * amp
        i = int(k * step * SR); out[i:i + n] += sq
    return lowpass(out, 6000)
def glitch_buzz(dur=0.5):  # bit-crushed buzz for the old-site glitch
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sign(np.sin(2 * np.pi * 110 * t * (1 + 0.5 * np.sin(2 * np.pi * 13 * t))))
    x = np.round(x * rng.random(n) * 4) / 4
    return lowpass(x, 3500) * (np.sin(np.pi * t / dur)) * 0.35
def light_on(f=1046):  # warm window light switching on: click + soft glow tone
    n = int(0.8 * SR); t = np.arange(n) / SR
    c = np.zeros(n); m = int(0.02 * SR); c[:m] = highpass(rng.standard_normal(m), 2000) * np.exp(-np.arange(m) / SR / 0.003)
    g = (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t)) * np.minimum(t / 0.05, 1) * np.exp(-t / 0.35) * 0.35
    return c * 0.9 + g
def cricket(dur=1.2, seed=7):  # night crickets
    n = int(dur * SR); t = np.arange(n) / SR
    am = (np.sin(2 * np.pi * 28 * t) > 0.3).astype(float) * (np.sin(2 * np.pi * 1.6 * t) > -0.2)
    return np.sin(2 * np.pi * 4300 * t) * am * np.sin(np.pi * t / dur) * 0.2
def notif():  # phone notification ding-ding
    return fm_bell(1976, 0.5, 1.0, 2.0) + np.pad(fm_bell(2637, 0.6, 1.0, 2.0), (int(0.09 * SR), 0))[:int(0.6 * SR) + int(0.09*SR)][:len(fm_bell(1976, 0.5, 1.0, 2.0))]

# hook: phone in, 8-bit old-site jingle under the question
sp(soft_whoosh(0.4, 500, 2600), T["phone"], 0.25)
sp(chip8([72, 76, 79, 76, 72, 67, 72, 79], 0.08, 0.4), 0.15, 0.22, -0.2)
sp(boom(0.8), 0.02, 0.35)
# mascot grabs the knob
sp(hop(0.3), T["grab"], 0.25, 0.3); sp(notch_click(1800), T["drag"][0][0] - 0.05, 0.4, 0.3)
for j, (t0, t1, a, b) in enumerate(T["drag"]):
    d = t1 - t0
    sp(slide_grind(d, 500 + j * 150, 1500 + j * 250 if b < a else 500, j), t0, 0.55, (a + b) - 1.0)
    sp(soft_whoosh(d, 600, 3000 if b < a else 800), t0, 0.15)
    sp(notch_click(2000 + j * 200), t1, 0.45, b * 2 - 1)
# dragged back to the old site: 8-bit sad jingle + glitch + alert
sp(chip8([79, 74, 71, 67, 62], 0.08, 0.5), T["glitch"], 0.3)
sp(glitch_buzz(0.55), T["glitch"], 0.35)
sp(fm_bell(1760, 0.4, 2.5, 3.0), T["ex"] + 0.05, 0.2, 0.3)
# lime wave wipe
sp(shimmer_up(T["wave1"] - T["wave0"] + 0.1), T["wave0"], 0.32)
sp(swipe(0.8, 7000, 900, 0.8), T["wave0"], 0.2)
sp(boom(0.9), T["wave1"], 0.45); sp(sparkle(10, 0.5, 0.8), T["wave1"] + 0.05, 0.3)
for k in range(5): sp(glass([3136, 3520, 3951, 4186, 4699][k], 0.35), T["wave1"] + 0.2 + k * 0.2, 0.15, (k - 2) * 0.2)
sp(hop(0.3), T["drag"][3][1] + 0.1, 0.22)
# booking
sp(hop(0.25), T["chip"] - 0.42, 0.22, -0.2); sp(snap(), T["chip"], 0.3, -0.2); sp(fm_bell(1568, 0.6, 1.2, 2.0), T["chip"] + 0.02, 0.2, -0.2)
sp(hop(0.25), T["btn"] - 0.42, 0.22)
sp(snap(), T["btn"], 0.35); sp(glass(3951, 0.4), T["btn"], 0.25); sp(sparkle(12, 0.4, 0.9), T["btn"] + 0.02, 0.35)
for j, f in enumerate([1319, 1568, 2093]): sp(fm_bell(f, 1.1, 1.4, 2.0, 1.0), T["toast"] + j * 0.06, 0.22, (j - 1) * 0.2)
# house: panel in, windows light up one by one
sp(soft_whoosh(0.45, 400, 2400), T["house"], 0.2); sp(thock(), T["house"] + 0.4, 0.25)
sp(hop(0.3), T["toast"] + 0.05, 0.22, 0.3)
for j, w in enumerate(T["win"]):
    sp(hop(0.2), w - 0.3, 0.14, 0.3)
    sp(light_on([1046, 1175, 1319, 1397, 1568][j]), w, 0.45, (j - 2) * 0.15)
    sp(tick(3000 + j * 200, 0.04), w + 0.1, 0.2)
# night: crickets, notifications
sp(reverse_swell(0.6, 900), T["night"] - 0.3, 0.15)
sp(cricket(2.2), T["night"] + 0.1, 0.25, 0.4)
for w in (T["win"][3], T["win"][4]): sp(notif(), w - 0.12, 0.3)
sp(boom(0.9), T["full"], 0.45); sp(fm_bell(2093, 0.8, 1.2, 2.0), T["full"] + 0.02, 0.22); sp(sparkle(10, 0.4, 0.8), T["full"] + 0.03, 0.3)
# back to 50/50 question
sp(slide_grind(0.55, 1200, 600, 9), T["back"], 0.5); sp(notch_click(2400), T["back1"], 0.45)
sp(hop(0.3), T["back"] + 0.1, 0.25)
sp(chip8([72, 72, 79], 0.1, 0.35), T["back1"] + 0.3, 0.18, -0.4)
# riser and drop
sp(hop(0.3), T["outro0"], 0.3, -0.5)
sp(riser(0.55), T["drop"] - 0.55, 0.3)
sp(boom(1.2), T["drop"], 0.75); sp(crash(1.6), T["drop"], 0.25)
sp(boom(1.0), T["t6b"], 0.55); sp(snap(), T["t6b"], 0.25)
sp(swipe(0.75, 2000, 9500, 0.8), T["sweep"], 0.16, -0.3)
sp(soft_whoosh(0.5, 3000, 300), T["s6_out"], 0.22)
# outro: cursor jumps into the logo
sp(reverse_swell(0.4), T["tile"] - 0.4, 0.22)
sp(boom(1.0), T["tile"], 0.6)
sp(hop(0.3), T["cur0"], 0.35, 0.2)
sp(shimmer_up(T["wave2_1"] - T["wave2_0"] + 0.1), T["wave2_0"], 0.18, -0.2)
sp(snap(), T["click2"], 0.35); sp(glass(3951, 0.4), T["click2"], 0.25)
sp(sparkle(10, 0.3, 0.8), T["click2"] + 0.02, 0.35, -0.1)
for i in range(9):
    sp(thock(), T["wm"] + i * 0.06, 0.28, (i - 4) * 0.06)
sp(soft_whoosh(0.3, 1500, 6500), T["cta1"], 0.16)
sp(soft_whoosh(0.3, 1500, 7000), T["cta2"], 0.18)

# ------------------------------ reverb on sfx -----------------------------
def make_ir(seed, tau=0.32):
    r = np.random.default_rng(seed)
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    ir = lowpass(r.standard_normal(n) * np.exp(-t / tau), 6000)
    ir[:int(0.012 * SR)] = 0
    return ir / np.sqrt(np.sum(ir ** 2))

S_L = S_L + signal.fftconvolve(S_L, make_ir(1))[:N] * 0.17
S_R = S_R + signal.fftconvolve(S_R, make_ir(2))[:N] * 0.17
M_L = M_L + signal.fftconvolve(M_L, make_ir(3, 0.5))[:N] * 0.08
M_R = M_R + signal.fftconvolve(M_R, make_ir(4, 0.5))[:N] * 0.08

# ------------------------------ final mix ---------------------------------
MUSIC_GAIN, DRUM_GAIN = 0.95, 0.80
L = S_L + M_L * MUSIC_GAIN + D_L * DRUM_GAIN
R = S_R + M_R * MUSIC_GAIN + D_R * DRUM_GAIN
t_all = np.arange(N) / SR
env = np.clip(t_all / 0.1, 0, 1) * np.clip((DURATION - t_all) / 1.2, 0, 1)
L *= env; R *= env
L = highpass(L, 35, 1); R = highpass(R, 35, 1)
peak = max(np.max(np.abs(L)), np.max(np.abs(R)))
L /= peak; R /= peak
L = np.tanh(1.5 * L * 0.9) / np.tanh(1.5) * 0.92
R = np.tanh(1.5 * R * 0.9) / np.tanh(1.5) * 0.92

n_out = int(DURATION * SR)
out = np.stack([L[:n_out], R[:n_out]], axis=1)
dest = os.path.join("/tmp/claude-0/-home-claude-buildwave-media/dfa22b05-59be-5a69-86df-ff78e38b6186/scratchpad", "vid_audio.wav")
wavfile.write(dest, SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
print("wrote", dest, "sec", round(n_out / SR, 2), "kicks", len(kick_times))
