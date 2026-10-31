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
HOOK = [[(0, 72, .5), (0.5, 76, .5), (1, 79, .5), (2, 81, .5), (2.5, 79, .5), (3, 76, 1)],
        [(0, 74, .5), (0.5, 77, .5), (1.5, 81, .5), (2, 79, .5), (2.5, 77, .5), (3, 72, 1)]]
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


# =============================== day SFX: site race ===============================
def beep(f, dur=0.22, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sign(np.sin(2 * np.pi * f * t)) * 0.35 + np.sin(2 * np.pi * f * t) * 0.65
    return lowpass(s, 5000) * np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.03) * amp * 0.5
def engine_rev(dur=1.1):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 55 + 170 * (1 - np.exp(-t / 0.35))
    ph = 2 * np.pi * np.cumsum(f) / SR
    s = np.tanh(2.5 * (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.3 * np.sin(3 * ph)))
    s = lowpass(s, 1800) + bandpass(rng.standard_normal(n), 400, 2500) * 0.2
    return s * np.minimum(1, t / 0.03) * np.exp(-np.maximum(0, t - 0.6) / 0.25) * 0.5
def spinner_hum(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    am = 0.55 + 0.45 * np.sin(2 * np.pi * 1.17 * t)
    s = (np.sin(2 * np.pi * 330 * t) + 0.5 * np.sin(2 * np.pi * 333 * t)) * 0.3 + bandpass(rng.standard_normal(n), 2000, 4000) * 0.25
    return s * am * np.minimum(1, t / 0.3) * np.minimum(1, (dur - t) / 0.2) * 0.4
def stopwatch(f=2400):
    n = int(0.03 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * 0.6 + highpass(rng.standard_normal(n), 3000) * 0.4) * np.exp(-t / 0.005)
def breath(dur=0.9, f0=500, f1=900):
    n = int(dur * SR); t = np.arange(n) / SR
    x = svf_band(rng.standard_normal(n), np.geomspace(f0, f1, n), 1.5)
    x /= np.max(np.abs(x)) + 1e-9
    return x * np.sin(np.pi * t / dur) ** 2 * 0.4
def snore(dur=0.7):
    n = int(dur * SR); t = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 38 * t)) * 0.5
    x = lowpass(buzz + rng.standard_normal(n) * 0.3, 700)
    return x * np.sin(np.pi * t / dur) ** 2 * 0.5

def ding(f=1568):
    a = fm_bell(f, 0.9, 1.2, 3.5, 1.0); b = fm_bell(f * 1.5, 0.6, 0.8, 2.0, 0.4); a[:len(b)] += b; return a
def drag(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 1500, 5000) * (0.4 + 0.6 * np.abs(np.sin(np.pi * t / dur)))
    return x * np.minimum(1, t / 0.05) * np.minimum(1, (dur - t) / 0.08) * 0.35


def key_click(f=2200):
    n = int(0.05 * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), f * 0.6, f * 1.8) * np.exp(-t / 0.008)
    x += 0.4 * np.sin(2 * np.pi * 160 * t) * np.exp(-t / 0.012)
    return x * 0.8
def scroll_whir(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    fl = 0.5 + 0.5 * np.sign(np.sin(2 * np.pi * (18 + 30 * np.sin(np.pi * t / dur)) * t))
    x = bandpass(rng.standard_normal(n), 900, 4500) * fl * np.sin(np.pi * t / dur) ** 0.7
    return x * 0.45
def step_up(f):
    a = glide(f, f * 1.5, 0.18, 0.6); b = tick(f * 2, 0.04, 0.6); a[:len(b)] += b; return a
def brush(dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = svf_band(rng.standard_normal(n), np.linspace(1500, 4000, n), 0.6) * (0.3 + 0.7 * np.sin(np.pi * t / dur))
    return x * 0.5

# =============================== day SFX: checklist ===============================
def checkmark():  # pen-stroke tick: short scratch + bright two-note ding
    n = int(0.12 * SR); t = np.arange(n) / SR
    x = svf_band(rng.standard_normal(n), np.linspace(2500, 6000, n), 0.9) * np.sin(np.pi * t / 0.12) * 0.5
    d = ding(2093); d[:n] += x; return d
def msg_in(f=1760):  # soft chat "incoming" double tone
    a = fm_bell(f, 0.35, 0.6, 1.0, 0.7); b = fm_bell(f * 1.335, 0.4, 0.6, 1.0, 0.7)
    out = np.zeros(max(len(a), len(b)) + int(0.07 * SR)); out[:len(a)] += a; out[int(0.07 * SR):int(0.07 * SR) + len(b)] += b; return out
def typing_dots(dur=0.35):
    out = np.zeros(int(dur * SR))
    for k in range(4):
        c = key_click(2600 + k * 200)[:int(0.04 * SR)]; i = int(k * dur / 4 * SR); out[i:i + len(c)] += c * 0.5
    return out
def land(f=900):  # light plastic landing for falling bubbles
    n = int(0.08 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * 0.5 + bandpass(rng.standard_normal(n), 1500, 5000) * 0.5) * np.exp(-t / 0.018)
def wobble(dur=1.0):  # confused wobbly tone for the lost pin
    n = int(dur * SR); t = np.arange(n) / SR
    f = 700 + 120 * np.sin(2 * np.pi * 5.5 * t)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / dur) * 0.25

# hook (loud first frame)
sp(boom(1.0), 0.0, 0.7); sp(snap(), T["hookB"], 0.3); sp(glass(3520), T["hookB"], 0.25)
sp(soft_whoosh(0.4, 600, 3000), T["card"], 0.18)
sp(swipe(0.18, 1600, 6500), T["sub"], 0.12)
sp(hop(), T["curIn"], 0.3, 0.2)
for i, h in enumerate(T["hA"]):
    sp(swipe(0.16, 1800, 7000), h, 0.12, 0.1)
# NEW: paper rustle + pen scribble
def paper(dur=0.5, seed=3):
    r = np.random.default_rng(seed); n = int(dur * SR)
    x = r.standard_normal(n) * (r.random(n) < 0.25)
    env = np.exp(-np.linspace(0, 4, n)) * (0.6 + 0.4 * np.abs(np.sin(np.linspace(0, 30, n))))
    return bandpass(x * env, 1500, 8000)
def scribble(dur=0.22):
    n = int(dur * SR); tt = np.arange(n) / SR
    x = np.random.default_rng(9).standard_normal(n)
    am = 0.5 + 0.5 * np.sin(2 * np.pi * 28 * tt)
    return bandpass(x * am * np.hanning(n), 2500, 7000)
def scanner(dur=0.7):
    n = int(dur * SR); tt = np.arange(n) / SR
    f = 900 + 500 * tt / dur
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 * np.hanning(n) + np.sin(2 * np.pi * 60 * tt) * 0.05
def flip(dur=0.3):
    return whoosh(dur, 2500, 400, 0.9, 0.7)
sp(paper(0.4, 1), T["card"] + 0.05, 0.35, -0.1)
sp(glass(2093, 0.3), T["stain"], 0.12)
for i, c in enumerate(T["scr"]):
    sp(hop(0.25), c - 0.45, 0.22, 0.3)
    sp(scribble(0.22), c, 0.5, 0.25); sp(tick(2400 + i * 200, 0.03), c + 0.17, 0.3, 0.25)
sp(paper(0.25, 4), T["note"], 0.35); sp(thock(), T["note"] + 0.08, 0.3)
# crumple + kick into the bin
sp(crumble(0.8), T["crum0"], 0.45); sp(paper(0.7, 7), T["crum0"], 0.55)
sp(soft_whoosh(0.4, 500, 2500), T["crum1"] - 0.1, 0.15)
sp(hop(0.3), T["crum1"], 0.28, -0.3)
sp(thud(180, 70, 0.3), T["kick"], 0.45); sp(snap(), T["kick"], 0.25)
sp(whoosh(0.5, 400, 3000, 0.9, 0.6), T["kick"] + 0.02, 0.22, 0.3)
sp(clank(), T["bin"], 0.5, 0.4)
sp(hop(0.3), T["bin"] + 0.1, 0.22, 0.3)
sp(soft_whoosh(0.35, 3000, 600), T["menuOut"], 0.15)
# table, QR flip, modules, scan, pixels fly
sp(thud(110, 50, 0.5), T["table"] + 0.1, 0.4)
sp(flip(0.35), T["qr"], 0.3); sp(thock(), T["qr"] + 0.4, 0.4)
for k in range(10): sp(tick(2000 + (k % 5) * 350, 0.025), T["mods"] + k * 0.05, 0.22, ((k % 3) - 1) * 0.3)
sp(soft_whoosh(0.45, 400, 2400), T["phone"], 0.2, 0.3)
sp(scanner(T["scan1"] - T["scan0"]), T["scan0"], 0.35, 0.1)
sp(beep(1760, 0.08), T["scan1"], 0.3); sp(beep(2349, 0.12), T["scan1"] + 0.09, 0.3)
sp(sparkle(14, 0.5, 0.8), T["fly0"], 0.3, 0.2)
for k in range(8): sp(thock(), T["fly0"] + 0.25 + k * 0.045, 0.16, 0.3)
sp(soft_whoosh(0.5, 600, 2600), T["center"], 0.2)
# lime wave paints the menu
sp(brush(T["wave1"] - T["wave0"]), T["wave0"], 0.6); sp(shimmer_up(T["wave1"] - T["wave0"] + 0.1), T["wave0"], 0.25)
sp(swipe(0.6, 800, 7000, 0.8), T["wave0"], 0.2); sp(boom(0.8), T["wave1"], 0.4)
# cart + order
for j, c in enumerate(T["plus"]):
    sp(hop(0.25), c - 0.42, 0.22, 0.2)
    sp(snap(), c, 0.3, 0.2); sp(fm_bell([1319, 1568, 1760][j], 0.6, 1.2, 2.0, 1.0), c + 0.02, 0.22, 0.2)
sp(hop(0.25), T["order"] - 0.42, 0.25)
sp(snap(), T["order"], 0.35); sp(glass(3951, 0.4), T["order"], 0.25); sp(sparkle(12, 0.4, 0.9), T["order"] + 0.02, 0.35)
for j, f in enumerate([1319, 1568, 2093]): sp(fm_bell(f, 1.1, 1.4, 2.0, 1.0), T["toast"] + j * 0.06, 0.22, (j - 1) * 0.2)
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
dest = os.path.join("/tmp/claude-0/-home-claude-buildwave-media/e68b26dc-f4b7-52a6-86b3-845c424bf5c4/scratchpad", "vid_audio.wav")
wavfile.write(dest, SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
print("wrote", dest, "sec", round(n_out / SR, 2), "kicks", len(kick_times))
