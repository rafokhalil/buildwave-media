import os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import T, DURATION

SR = 44100
TAIL = 2.0
N = int((DURATION + TAIL) * SR)
rng = np.random.default_rng(23)

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
HOOK = [[(0, 76, .5), (0.5, 79, .5), (1, 81, .75), (2, 79, .5), (2.5, 76, .5), (3, 74, 1)],
        [(0, 72, .5), (0.5, 74, .5), (1, 76, .75), (2, 79, .5), (2.5, 77, .5), (3, 76, 1)]]
BAR = 2.0; BEAT = 0.5
DROP = T["drop"]; END = T["pill"]; FILL0 = 17.0; GAP = (17.5, 18.0)
def in_rng(t, r): return r[0] <= t < r[1]
kick_times = []

for b in range(11):
    ch = PROG[b]
    vel = 0.55 if b == 0 else (0.8 if b < 3 else 1.0)
    cut = 900 + b * 160 if b < 2 else (2600 if b < 9 else 3200)
    if in_rng(b * BAR, GAP): continue
    place(pad([note(m) for m in CHORDS[ch]], 2.2, vel, cut), b * BAR, 1.0, 0.0, "music")
place(pad([note(m) for m in CHORDS["C"] + [72]], 2.0 + TAIL - 0.2, 1.1, 2600), END, 1.0, 0.0, "music")

# drums
t = 0.0
while t < END - 1e-6:
    beat_in_bar = round((t % BAR) / BEAT, 3)
    if not in_rng(t, GAP):
        if t >= 2.0:
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

# cheesy 8-bit jingle for the old website (0 .. poke), then a "tape stop" glitch
def square(f, dur, duty=0.5, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    ph = (f * t) % 1.0
    s = np.where(ph < duty, 1.0, -1.0)
    s = lowpass(s, 5000, 1)
    env = np.minimum(1, t / 0.004) * np.exp(-t / (dur * 1.6)) * np.minimum(1, (dur - t) / 0.01)
    return s * env * amp
MEL = [(0.00, 76, .18), (0.20, 79, .18), (0.40, 84, .18), (0.60, 83, .38), (1.00, 79, .18), (1.20, 81, .18), (1.40, 79, .18),
       (1.60, 76, .38), (2.00, 72, .18), (2.20, 76, .18), (2.40, 79, .18), (2.60, 81, .18), (2.80, 83, .18), (3.00, 84, .3)]
for off, m, d in MEL:
    tt = 0.05 + off
    if tt >= T["poke"]: break
    place(square(note(m), d, 0.25, 0.22), tt, 1.0, -0.1, "music")
    place(square(note(m - 12), d, 0.5, 0.10), tt, 1.0, 0.1, "music")
for k in range(int(T["poke"] / 0.4)):
    place(square(note(48 if k % 2 == 0 else 55), 0.16, 0.5, 0.16), 0.05 + k * 0.4, 1.0, 0.0, "music")
# tape-stop glitch at the poke
n = int(0.12 * SR); tt = np.arange(n) / SR
gl = np.sin(2 * np.pi * np.cumsum(np.geomspace(1300, 120, n)) / SR) * (1 - tt / tt[-1])
place(gl * 0.25, T["poke"], 1.0, 0.0, "sfx")
# hook
sp(reverse_swell(0.25), 0.0, 0.2)
sp(boom(1.0), T["hookA"], 0.6); sp(snap(), T["hookB"], 0.3); sp(glass(3520), T["hookB"], 0.25)
# cursor character hops in
for t0 in T["hops"]:
    sp(hop(), t0, 0.32, 0.3)
    sp(thock(), t0 + 0.33, 0.3, 0.3)
sp(glass(4186, 0.2), T["poke"], 0.35); sp(snap(), T["poke"] + 0.05, 0.3)
# explosion into pixels
sp(reverse_swell(0.15), T["boom"] - 0.15, 0.25)
sp(boom(1.4), T["boom"], 0.9); sp(crash(1.4), T["boom"], 0.2); sp(zap(0.2), T["boom"], 0.18)
sp(crumble(1.4), T["boom"] + 0.08, 0.7)
sp(gravel(0.6), T["boom"] + 0.6, 0.5)
sp(whoosh(0.6, 2500, 300, peak=0.3), T["boom"], 0.25, 0.4)    # cursor blown back
sp(thock(), T["land"], 0.4, 0.4)
sp(swipe(0.18, 1600, 6500), T["h2a"], 0.14); sp(swipe(0.18, 1600, 6500), T["h2b"], 0.14)
# crane arrives, blocks lowered and land
sp(soft_whoosh(0.6, 200, 1500), T["crane"], 0.25, 0.4)
for i, land in enumerate(T["blocks"]):
    sp(motor(0.62), land - 0.95, 0.25, 0.2)
    sp(soft_whoosh(0.55, 300, 1800), land - 0.55, 0.14)
    sp(boom(0.5), land, 0.45); sp(clank(), land, 0.3, (-0.3 + i * 0.12)); sp(gravel(0.3), land + 0.02, 0.25)
# pixels gather into the cake
sp(shimmer_up(1.0), T["gather"], 0.3)
sp(crumble(0.9), T["gather"] + 0.05, 0.35)
sp(sparkle(10, 0.3, 0.8), T["gather"] + 0.95, 0.35)
sp(glass(3136, 0.4), T["gather"] + 0.98, 0.25)
# cursor pushes the crooked card
sp(hop(), 10.9, 0.3, 0.4); sp(thock(), 11.25, 0.35, 0.4)
sp(snap(), T["push"] + 0.05, 0.3, 0.4); sp(clank(), T["push"] + 0.1, 0.2, 0.4)
# wave paints the site (cursor surfs)
sp(hop(), 11.6, 0.3, -0.3)
sp(whoosh(1.1, 300, 4500, q=0.9, peak=0.5), T["wave0"] - 0.05, 0.45)
sp(shimmer_up(1.1), T["wave0"], 0.35)
for j, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
    sp(fm_bell(f, 1.0, 1.4, 2.0, 1.0), T["wave0"] + 0.15 + j * 0.22, 0.2, (-0.6 + j * 0.4))
# click the order button
sp(hop(), T["toBtn"], 0.3)
sp(snap(), T["click"], 0.35); sp(glass(3951, 0.4), T["click"], 0.25)
sp(sparkle(14, 0.4, 0.9), T["click"] + 0.02, 0.4)
for j, f in enumerate((1046.5, 1318.5, 1568.0, 2093.0)):
    sp(fm_bell(f, 1.2, 1.4, 2.0, 1.0), T["toast"] + j * 0.06, 0.22, (j - 1.5) * 0.2)
# lie down, snore-ish soft breaths
sp(hop(), 14.9, 0.25)
for k in range(3):
    n = int(0.5 * SR); tt = np.arange(n) / SR
    br = lowpass(rng.standard_normal(n), 700) * np.sin(np.pi * tt / tt[-1]) ** 2 * 0.25
    sp(br, T["lie"] + 0.5 + k * 0.4, 0.4)
# riser and drop
sp(soft_whoosh(0.8, 200, 2000), T["outro0"], 0.2)
sp(riser(DROP - 16.6, 9000), 16.6, 0.4)
sp(reverse_swell(0.9), DROP - 0.9, 0.3)
sp(boom(1.4), DROP, 0.75); sp(crash(2.0), DROP, 0.2)
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
sp(crash(1.6), END, 0.2); sp(boom(1.2), END, 0.5)

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
dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vid_audio.wav")
wavfile.write(dest, SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
print("wrote", dest, "sec", round(n_out / SR, 2), "kicks", len(kick_times))
