import os, sys
import numpy as np
from scipy import signal
from scipy.io import wavfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import T, DURATION

SR = 44100
TAIL = 2.0
N = int((DURATION + TAIL) * SR)
rng = np.random.default_rng(57)

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


def note(n):  # MIDI -> Hz
    return 440.0 * 2 ** ((n - 69) / 12)

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


# =============================== day SFX: site tetris (dental clinic) ===============================
def busy_tone(dur=0.32):  # landline busy beep (480+620 Hz), slightly filtered like a phone line
    n = int(dur * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 480 * t) + np.sin(2 * np.pi * 620 * t)) * np.minimum(1, t / 0.01) * np.minimum(1, (dur - t) / 0.02)
    return bandpass(x, 300, 3400) * 0.45
def ring_rattle(dur=2.2):  # old phone bell rattle
    n = int(dur * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * 1700 * t) + 0.6 * np.sin(2 * np.pi * 2300 * t)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 19 * t)))
    return x * np.minimum(1, t / 0.05) * np.exp(-t / 1.4) * 0.12
def chip8(f0, f1, dur=0.12, amp=1.0):  # square-wave blip sweep (tetris console)
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.geomspace(f0, f1, n); ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sign(np.sin(ph)) * np.exp(-t / (dur * 0.6)) * 0.18 * amp
def block_land(seed):  # chunky block lands: low thock + plastic click
    r = np.random.default_rng(seed); n = int(0.25 * SR); t = np.arange(n) / SR
    th = np.sin(2 * np.pi * (90 + 60 * np.exp(-t / 0.02)) * t) * np.exp(-t / 0.06)
    ck = bandpass(r.standard_normal(n), 1800, 6000) * np.exp(-t / 0.008) * 0.6
    return th * 0.9 + ck
def fall_whistle(dur=0.38):  # short falling sweep
    n = int(dur * SR); t = np.arange(n) / SR
    x = svf_band(rng.standard_normal(n), np.geomspace(4000, 900, n), 2.5); x /= np.max(np.abs(x)) + 1e-9
    return x * (t / dur) * 0.35
def ratchet(n_clicks=4, span=0.28):
    out = np.zeros(int((span + 0.05) * SR))
    for k in range(n_clicks):
        c = tick(3000 - k * 200, 0.02, 1.0); i = int(k * span / n_clicks * SR); out[i:i + len(c)] += c
    return out
def buzz_wrong(dur=0.35):  # stuck piece error buzz
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sign(np.sin(2 * np.pi * 110 * t)) * lowpass(np.ones(n), 50) * np.exp(-t / 0.2) * 0.12
def line_clear():  # 8-bit arpeggio up
    out = np.zeros(int(0.6 * SR))
    for k, m in enumerate([72, 76, 79, 84, 88]):
        c = chip8(note(m), note(m), 0.1, 1.0); i = int(k * 0.07 * SR); out[i:i + len(c)] += c
    return out
def booking_ding():
    a = fm_bell(1760, 0.6, 1.0, 2.0); b = fm_bell(2637, 0.7, 1.0, 2.0)
    out = np.zeros(len(b) + int(0.08 * SR)); out[:len(a)] += a; out[int(0.08 * SR):int(0.08 * SR) + len(b)] += b
    return out

# ---- claw-machine SFX ----
def claw_whir(dur):  # small gear motor of the claw carriage
    n = int(dur * SR); t = np.arange(n) / SR
    f = 160 + 25 * np.sin(2 * np.pi * 3 * t)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.5 + bandpass(rng.standard_normal(n), 1500, 4000) * 0.4
    return lowpass(x, 2500) * np.minimum(1, t / 0.03) * np.minimum(1, (dur - t) / 0.05) * 0.18
def clamp_clack():  # metal prongs close
    r = np.random.default_rng(7); n = int(0.18 * SR); t = np.arange(n) / SR
    m = (np.sin(2 * np.pi * 1850 * t) + 0.7 * np.sin(2 * np.pi * 2730 * t)) * np.exp(-t / 0.03)
    return m * 0.35 + bandpass(r.standard_normal(n), 2000, 7000) * np.exp(-t / 0.006) * 0.8
def cable_zip(dur, up=True):  # cable reel
    n = int(dur * SR); t = np.arange(n) / SR
    f = np.geomspace(900, 1800, n) if up else np.geomspace(1800, 900, n)
    x = svf_band(rng.standard_normal(n), f, 6.0); x /= np.max(np.abs(x)) + 1e-9
    return x * np.minimum(1, t / 0.02) * np.minimum(1, (dur - t) / 0.03) * 0.22
def arcade_btn():  # chunky arcade button
    n = int(0.14 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * (140 + 80 * np.exp(-t / 0.01)) * t) * np.exp(-t / 0.04) * 0.9 + tick(4200, 0.02, 0.6)[:n].sum() * 0
def chute_rattle():  # plastic piece rattles down the chute
    out = np.zeros(int(0.45 * SR))
    for k, d in enumerate([0, 0.06, 0.13, 0.19, 0.27]):
        c = block_land(100 + k) * (0.9 - k * 0.15); i = int(d * SR); out[i:i + len(c)] += c[:len(out) - i]
    return out
def arcade_coin():
    a = chip8(note(83), note(83), 0.07); b = chip8(note(88), note(88), 0.25)
    out = np.zeros(len(b) + int(0.07 * SR)); out[:len(a)] += a; out[int(0.07 * SR):] += b
    return out
def scamper(dur=0.7):  # little feet running off
    out = np.zeros(int((dur + 0.05) * SR))
    for k in range(int(dur / 0.07)):
        c = tap(260 + (k % 2) * 60, 0.06); i = int(k * 0.07 * SR); out[i:i + len(c)] += c[:len(out) - i] * 0.6
    return out

# ---- slot machine SFX (new) ----
def reel_spin(dur, r0=28, r1=5, f=2100):  # decelerating click rattle of a spinning reel
    out = np.zeros(int((dur + 0.1) * SR)); tt = 0.0
    while tt < dur:
        q = tt / dur; rate = r0 + (r1 - r0) * q
        c = tick(f * (0.9 + 0.2 * rng.random()), 0.02, 0.8); i = int(tt * SR); out[i:i + len(c)] += c[:len(out) - i]
        tt += 1.0 / rate
    return lowpass(out, 6000) * 0.8
def reel_stop():  # heavy mechanical clunk
    n = int(0.25 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * (180 - 300 * t) * t) * np.exp(-t / 0.05)
    clk = bandpass(rng.standard_normal(n), 1500, 4500) * np.exp(-t / 0.012)
    return body * 0.8 + clk * 0.6
def lever_pull(dur=0.35):  # spring stretch creak + ratchet
    n = int(dur * SR); t = np.arange(n) / SR
    cr = bandpass(rng.standard_normal(n), 700, 1300) * np.exp(-((t - dur / 2) / (dur / 2)) ** 2) * 0.5
    sp_ = np.sin(2 * np.pi * (300 + 700 * t / dur) * t) * 0.15 * np.exp(-t / 0.3)
    out = cr + sp_; r = ratchet(5, dur * 0.8); out[:len(r)] += r[:n] * 0.6
    return out
def spring_back():
    n = int(0.5 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 220 * t * (1 + 0.3 * np.sin(2 * np.pi * 14 * t))) * np.exp(-t / 0.12) * 0.5
def coin_ting(f):
    return fm_bell(f, 0.35, 1.8, 3.1, 0.6)
def jackpot_bells(dur=1.2):
    out = np.zeros(int((dur + 0.6) * SR))
    for k in range(int(dur / 0.06)):
        f = [2093, 2637, 3136, 2637][k % 4] * (1 + 0.004 * rng.standard_normal())
        c = fm_bell(f, 0.3, 1.2, 2.0, 0.5); i = int(k * 0.06 * SR); out[i:i + len(c)] += c[:len(out) - i]
    return out
def lose_jingle():  # 3 descending 8-bit blips
    out = np.zeros(int(0.6 * SR))
    for k, (a, b) in enumerate([(660, 600), (520, 470), (330, 220)]):
        c = chip8(a, b, 0.14 if k < 2 else 0.22); i = int(k * 0.15 * SR); out[i:i + len(c)] += c[:len(out) - i]
    return out

# ---- code-rain SFX
def digi_tick(f, dur=0.03):  # tiny digital glyph tick (sine blip, fast decay)
    n = int(dur * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.008) * 0.8
def rain_bed(dur, rate, seed, f0=2200, f1=5200):  # stream of glyph ticks
    r = np.random.default_rng(seed); out = np.zeros(int(dur * SR) + SR // 10); tt = 0.0
    while tt < dur:
        s = digi_tick(r.uniform(f0, f1)) * r.uniform(0.3, 1.0); i = int(tt * SR); out[i:i + len(s)] += s[:len(out) - i]
        tt += r.exponential(1.0 / rate)
    return out
def data_fill(dur=0.35, f0=500, f1=1600):  # block fills: rising stepped square chirp + clicks
    n = int(dur * SR); t = np.arange(n) / SR; steps = np.floor(t / dur * 8) / 8
    f = f0 + (f1 - f0) * steps; ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sign(np.sin(ph)) * 0.25 * np.exp(-t / (dur * 0.9)) * np.clip(t / 0.01, 0, 1)
def skitter(dur=0.45, seed=3):  # bug legs scuttling
    r = np.random.default_rng(seed); out = np.zeros(int(dur * SR) + 400)
    for k in range(int(dur * 38)):
        n = 250; s = bandpass(r.standard_normal(n), 2500, 7000) * np.exp(-np.arange(n) / 60) * r.uniform(.4, 1)
        i = int(k / 38 * SR); out[i:i + n] += s
    return out
def squish(dur=0.3):  # wet squash: lowpassed noise burst + downward thump
    n = int(dur * SR); t = np.arange(n) / SR
    nz = lowpass(np.random.default_rng(9).standard_normal(n), 900) * np.exp(-t / 0.06)
    return nz * 0.9 + thud(160, 60, dur)[:n] * 0.6
def bonk():  # hollow wooden bonk on the head
    n = int(0.3 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 620 * t) * 0.7 + np.sin(2 * np.pi * 1290 * t) * 0.3) * np.exp(-t / 0.05)

# ---- zoom / paper SFX
def paper_flutter(dur, seed, rate=14):  # paper notes fluttering on the board
    r = np.random.default_rng(seed); out = np.zeros(int(dur * SR) + SR // 5); tt = 0.0
    while tt < dur:
        n = int(r.uniform(0.03, 0.07) * SR); s = bandpass(r.standard_normal(n), 900, 5000) * np.hanning(n) * r.uniform(.3, 1)
        i = int(tt * SR); out[i:i + n] += s[:len(out) - i]; tt += r.exponential(1.0 / rate)
    return out
def tear(dur=0.28):  # tear-off tab rips
    r = np.random.default_rng(5); n = int(dur * SR); t = np.arange(n) / SR
    nz = bandpass(r.standard_normal(n), 1500, 7000) * (0.5 + 0.5 * (r.random(n) > 0.6)) * np.exp(-t / 0.12)
    return nz * np.clip(t / 0.01, 0, 1)
def zoom_rush(dur):  # rising rush with pitch sweep: the camera dives into the tab
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    nz = np.random.default_rng(8).standard_normal(n)
    out = np.zeros(n); seg = 2048
    for i in range(0, n, seg):
        fc = 300 * (25 ** (p[i]**1.6)); out[i:i + seg] = bandpass(nz[i:i + seg + 0], max(80, fc * .6), min(16000, fc * 1.6 + 200))[:len(out[i:i+seg])]
    f = 120 * (12 ** (p ** 2)); tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    return (out * 0.7 + tone) * (p ** 1.3) * np.clip((dur - t) / 0.03, 0, 1)
def zslam(k):  # block zooms in and slams: short down-swish + thock + pitched glass
    w = whoosh(0.22, 4000, 600, 0.9, 0.3) * 0.5; th = thock()
    out = np.zeros(int(0.5 * SR)); out[:len(w)] += w; i = int(0.2 * SR); out[i:i + len(th)] += th[:len(out) - i]
    return out
def inflate(f0, f1, dur=0.3):  # hero photo pumps up: rising rubbery tone
    n = int(dur * SR); t = np.arange(n) / SR; f = f0 + (f1 - f0) * (t / dur) ** 0.7
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.3 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * np.exp(-t / (dur * .6)) * np.clip(t / 0.01, 0, 1) * 0.6
def key_jingle():  # bunch of keys
    r = np.random.default_rng(11); out = np.zeros(int(0.5 * SR))
    for k in range(6):
        s = glass(r.uniform(3000, 5200), 0.25) * r.uniform(.4, 1); i = int(r.uniform(0, 0.12) * SR); out[i:i + len(s)] += s[:len(out) - i]
    return out

def wood_clack(seed, f=1800):  # hard wooden book edge hits the next one
    r = np.random.default_rng(seed); n = int(0.09 * SR); t = np.arange(n) / SR
    body = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.012) + 0.6 * np.sin(2 * np.pi * f * 1.52 * t) * np.exp(-t / 0.008)
    noise = bandpass(r.standard_normal(n), 1500, 6000) * np.exp(-t / 0.006) * 0.5
    return (body + noise) * 0.8
def book_thud(seed):  # book slaps flat on the shelf
    r = np.random.default_rng(seed); n = int(0.25 * SR); t = np.arange(n) / SR
    return thud(160, 60, 0.25)[:n] * 0.8 + lowpass(r.standard_normal(n), 1200) * np.exp(-t / 0.025) * 0.6
def rewind(dur=0.45):  # tape-rewind chirp: fast rising warble + noise
    n = int(dur * SR); t = np.arange(n) / SR; f = 300 + 2600 * (t / dur) ** 1.5 + 120 * np.sin(2 * np.pi * 22 * t)
    s = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + highpass(rng.standard_normal(n), 2500) * 0.25
    return lowpass(s, 5000) * np.clip(t / 0.03, 0, 1) * np.clip((dur - t) / 0.05, 0, 1)
def desk_bell():  # reception desk bell: bright inharmonic ring
    out = fm_bell(2637, 1.6, 1.1, 2.76, 1.0); b = fm_bell(3951, 1.2, 0.8, 1.41, 1.0); out[:len(b)] += 0.5 * b
    return out
def page_flip(seed):  # quick paper riffle as a book flies
    r = np.random.default_rng(seed); n = int(0.22 * SR); t = np.arange(n) / SR
    env = np.abs(np.sin(2 * np.pi * 28 * t)) * np.exp(-t / 0.09)
    return bandpass(r.standard_normal(n), 2000, 8000) * env * 0.7

# ---- pinball SFX (new) ----
def bumper_hit(f, seed):  # pop bumper: hard plastic thwack + bright metallic ring rising slightly
    r = np.random.default_rng(seed); n = int(0.4 * SR); t = np.arange(n) / SR
    knock = bandpass(r.standard_normal(n), 800, 5000) * np.exp(-t / 0.008) * 0.8
    fr = f * (1 + 0.04 * np.minimum(1, t / 0.05))
    ring = (np.sin(2 * np.pi * np.cumsum(fr) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(fr * 2.01) / SR)) * np.exp(-t / 0.12) * 0.5
    return knock + ring
def flipper_clack(seed):  # solenoid flipper: low thump + click
    r = np.random.default_rng(seed); n = int(0.18 * SR); t = np.arange(n) / SR
    return thud(110, 55, 0.18)[:n] * 0.9 + highpass(r.standard_normal(n), 3000) * np.exp(-t / 0.004) * 0.5
def ball_roll(dur, seed):  # steel ball rolling on wood: filtered rumble with flutter
    r = np.random.default_rng(seed); n = int(dur * SR); t = np.arange(n) / SR
    x = bandpass(r.standard_normal(n), 150, 900) * (0.7 + 0.3 * np.sin(2 * np.pi * 17 * t))
    return x * np.clip(t / 0.05, 0, 1) * np.clip((dur - t) / 0.08, 0, 1) * 0.5
def drain_buzz(dur=0.5):  # ball lost: two low square buzzes
    out = np.zeros(int(dur * SR))
    for k, f in enumerate([196, 147]):
        n = int(0.18 * SR); t = np.arange(n) / SR
        s = np.sign(np.sin(2 * np.pi * f * t)) * 0.35 * np.exp(-t / 0.15); i0 = int(k * 0.2 * SR); out[i0:i0 + n] += lowpass(s, 2500)
    return out
def plunger_pull(dur=0.45):  # spring stretching: rising metallic creak
    n = int(dur * SR); t = np.arange(n) / SR; f = 600 + 900 * t / dur
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (0.5 + 0.5 * np.sin(2 * np.pi * 40 * t)) * 0.25
    return s * np.clip(t / 0.05, 0, 1)
def plunger_fire():  # spring release: twang + launch swish
    n = int(0.5 * SR); t = np.arange(n) / SR
    tw = np.sin(2 * np.pi * 220 * t + 3 * np.sin(2 * np.pi * 9 * t)) * np.exp(-t / 0.12) * 0.5
    out = tw + thock()[:n] * 0.6 if len(thock()) >= n else tw
    return out
def score_count(n_steps=6, f0=1568):  # LED score ticking up
    out = np.zeros(int(0.5 * SR))
    for k in range(n_steps):
        s = chip8(f0 * 2 ** (k / 12), f0 * 2 ** (k / 12), 0.05, 0.5); i0 = int(k * 0.045 * SR); out[i0:i0 + len(s)] += s[:len(out) - i0]
    return out

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

# =============== MUSIC: 100 BPM dembow groove in D minor (marimba + EP stabs + 808) ===============
from timeline import GRID0
BEAT = 0.6; S16 = 0.15; BARD = 2.4
DROP = T["drop"]; END = 22.8; CUT0, CUT1 = 4.25, 5.4; GAP = (17.4, 18.0)
def in_rng(t, r): return r[0] <= t < r[1]
def silent(t): return in_rng(t, (CUT0, CUT1)) or t >= END
kick_times = []

def kick808():
    n = int(0.5 * SR); t = np.arange(n) / SR
    f = 46 + 150 * np.exp(-t / 0.025)
    s = np.tanh(2.6 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.2))
    c = bandpass(rng.standard_normal(n), 1500, 6000) * np.exp(-t / 0.002) * 0.5
    return s + c
def snare_rg(vel=1.0):  # tight reggaeton snare
    n = int(0.2 * SR); t = np.arange(n) / SR
    nz = bandpass(rng.standard_normal(n), 1800, 9000) * np.exp(-t / 0.055)
    tone = np.sin(2 * np.pi * (240 - 40 * t / 0.2) * t) * np.exp(-t / 0.04) * 0.6
    return (nz + tone) * vel * 0.8
def rim(vel=1.0):
    n = int(0.06 * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * 1650 * t) * 0.6 + bandpass(rng.standard_normal(n), 2000, 7000)) * np.exp(-t / 0.01) * vel
def timbale(f, vel=1.0):
    n = int(0.3 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.09) + 0.4 * np.sin(2 * np.pi * f * 2.3 * t) * np.exp(-t / 0.05)
    return (s + bandpass(rng.standard_normal(n), 1500, 6000) * np.exp(-t / 0.006) * 0.6) * vel * 0.6
def bass808(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    ff = f * (1 + 0.5 * np.exp(-t / 0.02))
    s = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(ff) / SR))
    env = np.minimum(1, t / 0.004) * np.minimum(1, (dur - t) / 0.03) * (0.75 + 0.25 * np.exp(-t / 0.15))
    return lowpass(s, 700) * env * 0.85
def ep(freqs, dur=0.32, vel=1.0):  # electric-piano stab (tine + bark)
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        mod = np.sin(2 * np.pi * f * 14 * t) * 0.9 * np.exp(-t / 0.012)
        s += np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 0.28) + 0.25 * np.sin(4 * np.pi * f * t) * np.exp(-t / 0.12)
    s *= (1 + 0.15 * np.sin(2 * np.pi * 5.5 * t)) * np.minimum(1, t / 0.003) * np.minimum(1, (dur - t) / 0.03)
    return s * vel / len(freqs) * 0.9
def marimba(f, dur=0.6, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / 0.3) + 0.45 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t / 0.05) \
        + 0.15 * np.sin(2 * np.pi * f * 9.2 * t) * np.exp(-t / 0.015)
    s += bandpass(rng.standard_normal(n), 2000, 7000) * np.exp(-t / 0.003) * 0.25
    return s * np.minimum(1, t / 0.0015) * vel * 0.7
def pad2(freqs, dur, vel=1.0, cutoff=1500):
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for det in (-0.12, 0.12):
            ph = rng.uniform(0, 6); s += np.sin(2 * np.pi * f * 2 ** (det / 12) * t + ph) + 0.3 * np.sin(4 * np.pi * f * 2 ** (det / 12) * t + ph)
    s = lowpass(s, cutoff)
    return s * np.minimum(1, t / 0.15) * np.minimum(1, (dur - t) / 0.3) * vel / (len(freqs) * 2)
def brass(freqs, dur=0.4):  # synth brass stab for the drop
    n = int(dur * SR); t = np.arange(n) / SR; s = np.zeros(n)
    for f in freqs:
        for det in (-0.1, 0.0, 0.1):
            ff = f * 2 ** (det / 12); s += signal.sawtooth(2 * np.pi * ff * t + rng.uniform(0, 6))
    cut = 600 + 4000 * np.exp(-t / 0.08)
    out = np.zeros(n); seg = 512
    for i in range(0, n, seg):
        out[i:i + seg] = lowpass(s[max(0, i - 2048):i + seg], cut[i])[-len(s[i:i + seg]):]
    return out * np.minimum(1, t / 0.005) * np.exp(-t / 0.25) / (len(freqs) * 3)

CH = {"Dm": [62, 65, 69], "Bb": [62, 65, 70], "F": [60, 65, 69], "C": [60, 64, 67], "Gm": [62, 67, 70], "A": [61, 64, 69]}
RT = {"Dm": 38, "Bb": 34, "F": 41, "C": 36, "Gm": 43, "A": 45}
PROG = [["Dm"], ["Bb"], ["F"], ["C"], ["Dm"], ["Bb"], ["Gm", "A"], ["Dm"], ["Bb"]]
def chord_at(t):
    b = int((t - GRID0) // BARD); b = max(0, min(b, len(PROG) - 1)); pr = PROG[b]
    half = ((t - GRID0) % BARD) >= BARD / 2
    return pr[1] if (len(pr) > 1 and half) else pr[0]

# drums + bass + EP on a 16th grid
for i in range(int((END - GRID0) / S16) + 1):
    tt = round(GRID0 + i * S16, 4)
    if tt >= END or silent(tt): continue
    pos = i % 8  # position in a 2-beat dembow cell
    gap = in_rng(tt, GAP)
    ch = chord_at(tt); r = note(RT[ch])
    if pos in (0, 4) and not gap:
        place(kick808(), tt, 0.9, 0.0, "drum"); kick_times.append(tt)
    if pos in (3, 6) and not gap:
        place(snare_rg(1.0), tt, 0.5, 0.05, "drum")
        if tt >= DROP: place(clap(0.8), tt, 0.3, 0.0, "drum")
    if not gap:
        place(shaker(1.0 if i % 2 else 0.55), tt, 0.16, -0.35, "drum")
        if tt >= 8.4 and pos in (2, 6): place(hat(True, 0.7), tt, 0.14, 0.35, "drum")
        if pos in (1, 5) and tt >= 3.0: place(rim(0.6), tt, 0.12, 0.4, "drum")
    # bass
    if not gap:
        for p_, ln, mul in ((0, 3, 1), (3, 1, 1), (4, 2, 1), (6, 2, 1.5)):
            if pos == p_: place(bass808(r * mul, ln * S16 * 0.95), tt, 0.6, 0.0, "music")
    # EP skank on the snare positions, from the second fader
    if tt >= 3.6 and pos in (3, 6) and not gap:
        place(ep([note(m) for m in CH[ch]], 0.3, 1.0), tt, 0.42 if tt < DROP else 0.48, 0.15, "music")
# timbale fills at bar ends
for tb in (8.4 - 0.6, 15.6 - 0.6):
    for k, f in enumerate([520, 520, 390, 390]):
        place(timbale(f, 0.6 + 0.1 * k), tb + k * S16, 0.32, (-0.3, 0.3)[k % 2], "drum")
# snare roll into the drop
for k in range(16):
    place(snare_rg(0.3 + 0.05 * k), GAP[0] + k * 0.0375, 0.35, 0.0, "drum")
# marimba hook from bar 2 (6.0 s)
A_ = [(0, 81, 2), (3, 81, 2), (6, 79, 2), (8, 77, 2), (10, 79, 1), (11, 77, 1), (12, 74, 2), (14, 77, 2)]
B_ = [(0, 72, 2), (3, 74, 2), (6, 77, 2), (8, 79, 2), (10, 81, 2), (12, 84, 1), (13, 81, 1), (14, 79, 2)]
C_ = [(0, 79, 2), (3, 79, 2), (6, 82, 2), (8, 81, 2), (10, 79, 2), (12, 76, 2), (14, 73, 2)]
LEAD = {2: B_, 3: B_, 4: A_, 5: A_, 6: C_, 7: A_, 8: B_}
for b, ph_ in LEAD.items():
    for p_, m, ln in ph_:
        tt = GRID0 + b * BARD + p_ * S16
        if silent(tt) or in_rng(tt, (GAP[0] - 0.3, GAP[1])): continue
        g = 0.34 if b < 7 else 0.38
        place(marimba(note(m), 0.7), tt, g, -0.2, "music")
        place(marimba(note(m) * 1.004, 0.7), tt + 0.01, g * 0.4, 0.3, "music")
        if b >= 7: place(marimba(note(m + 12), 0.5), tt, g * 0.4, 0.1, "music")
# soft pad bed from 6.0, fuller after the drop
for b in range(2, 9):
    t0 = GRID0 + b * BARD
    for k, ch in enumerate(PROG[b]):
        ts = t0 + k * BARD / len(PROG[b]); ln = BARD / len(PROG[b])
        if in_rng(ts, GAP): continue
        place(pad2([note(m - 12) for m in CH[ch]] + [note(CH[ch][0])], ln + 0.2, 1.0, 1300 if b < 7 else 2000), ts, 0.5 if b < 7 else 0.7, 0.0, "music")
# drop brass stabs
for ts in (DROP, DROP + 0.45, 20.4, 20.85):
    place(brass([note(m) for m in CH["Dm" if ts < 20.4 else "Bb"]] + [note(74 if ts < 20.4 else 70)], 0.4), ts, 0.5, 0.0, "music")
# ending: Dm ring
place(pad2([note(m) for m in [50, 62, 65, 69]], 1.3 + TAIL, 1.0, 2200), END, 1.0, 0.0, "music")
place(marimba(note(86), 1.2), END, 0.35, 0.0, "music"); place(bass808(note(38), 1.0), END, 0.6, 0.0, "music")
place(kick808(), END, 0.9, 0.0, "drum"); kick_times.append(END)
# pickup (0-1.2 s): bright marimba arpeggio, so the first second is not quiet
for k, m in enumerate([74, 77, 81, 86, 81, 77, 81, 86]):
    place(marimba(note(m), 0.5), k * S16, 0.5, (k % 2 - 0.5) * 0.5, "music")
place(pad2([note(m) for m in [50, 62, 65, 69]], 1.3, 1.0, 1800), 0.0, 1.0, 0.0, "music")

# sidechain
duck = np.ones(N); seg = int(0.3 * SR)
ds = 1.0 - 0.4 * np.exp(-(np.arange(seg) / SR) / 0.08)
for kt in kick_times:
    i = int(kt * SR); m = min(seg, N - i)
    if m > 0: duck[i:i + m] = np.minimum(duck[i:i + m], ds[:m])
M_L *= duck; M_R *= duck

# "muted speaker": 1.2-3.0 s the groove plays through a wall (lowpass), the Logo fader opens it
tt_all = np.arange(N) / SR
w_full = np.clip(1 - (tt_all - 1.15) / 0.1, 0, 1) + np.clip((tt_all - T["f1"]) / 0.3, 0, 1)
w_full = np.clip(w_full, 0, 1)
def muffle(x): return lowpass(x, 420, 4) * 0.95
for A in (M_L, M_R, D_L, D_R):
    A[:] = A * w_full + muffle(A) * (1 - w_full)
# tape-stop at the jam (4.25), silence until the unjam (5.4)
i0 = int(CUT0 * SR); L_ts = int(0.45 * SR); tq = np.arange(L_ts) / SR
pos = (tq - tq ** 2 / (2 * 0.45)) * SR
for A in (M_L, M_R, D_L, D_R):
    src = A[i0:i0 + int(0.3 * SR)].copy()
    ts_ = np.interp(pos, np.arange(len(src)), src) * np.clip((0.45 - tq) / 0.1, 0, 1)
    A[i0:i0 + L_ts] = ts_
    A[i0 + L_ts:int(CUT1 * SR)] = 0

# =============================== day SFX: DJ mixer ===============================
def fader_slide(dur=0.3, up=True):
    n = int(dur * SR); t = np.arange(n) / SR
    fc = np.geomspace(500, 2600, n) if up else np.geomspace(2600, 500, n)
    x = svf_band(rng.standard_normal(n), fc, 1.8); x /= np.max(np.abs(x)) + 1e-9
    return x * np.sin(np.pi * t / t[-1]) ** 0.7 * 0.45
def fader_stop():
    out = np.zeros(int(0.15 * SR)); a = thock(); b = tick(3200, 0.03, 0.8)
    out[:len(a)] += a; out[:len(b)] += b * 0.6
    return out
def needle_scratch(dur=0.42):
    n = int(dur * SR); t = np.arange(n) / SR
    fc = 700 * 2 ** (1.6 * np.sin(2 * np.pi * 5.0 * t))
    x = svf_band(rng.standard_normal(n), fc, 3.0); x /= np.max(np.abs(x)) + 1e-9
    return x * np.abs(np.sin(2 * np.pi * 5.0 * t)) ** 0.5 * np.exp(-t / 0.35) * 0.7
def crackle(dur, seed, rate=18):
    r = np.random.default_rng(seed); out = np.zeros(int(dur * SR) + 200); tt = 0.0
    while tt < dur:
        c = tick(r.uniform(1500, 5000), 0.006, r.uniform(0.2, 1.0)); i = int(tt * SR); out[i:i + len(c)] += c[:len(out) - i]
        tt += r.exponential(1.0 / rate)
    return lowpass(out, 6000) * 0.35
def stomp():
    out = thud(150, 55, 0.3) * 0.7; c = block_land(31)[:len(out)]; out[:len(c)] += c * 0.6
    return out
def grind(dur=0.35):  # jammed fader grinding
    n = int(dur * SR); t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 300, 1500) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 34 * t)))
    return x * np.exp(-t / 0.25) * 0.5

# hook: bright pickup + rewind, crackle while the speaker is muted
sp(boom(0.8), 0.02, 0.32); sp(rewind(0.4), 0.0, 0.18); sp(soft_whoosh(0.4, 3000, 600), 0.05, 0.18)
sp(crackle(3.0, 1), 0.0, 0.5, -0.1); sp(crackle(1.2, 2), CUT0, 0.6, 0.1)
sp(hop(0.3), T["curIn"], 0.22, -0.4); sp(thock(), 1.4, 0.3, -0.4)
# faders up
for k, f in enumerate((T["f1"], T["f2"], T["f4"])):
    sp(fader_slide(0.3), f, 0.5, (-0.4, -0.15, 0.4)[k]); sp(fader_stop(), f + 0.3, 0.4, (-0.4, -0.15, 0.4)[k])
    sp(glass([2637, 3136, 3951][k], 0.3), f + 0.3, 0.18)
sp(boom(0.7), T["f1"] + 0.3, 0.35); sp(shimmer_up(0.5), T["f1"], 0.15)
for h in (3.32, 3.92, 5.75): sp(hop(0.25), h, 0.2, 0.1)
# jam: short slide, grind, needle scratch, tape stop
sp(fader_slide(0.12), T["f3"], 0.45, 0.15); sp(grind(0.4), T["jam"], 0.5, 0.15); sp(needle_scratch(0.45), CUT0 - 0.02, 0.55)
sp(buzz_wrong(0.35), T["jam"] + 0.08, 0.35)
for k, s in enumerate(T["st"]):
    sp(hop(0.22), s - 0.28, 0.15, 0.15); sp(stomp(), s, 0.55 if k < 2 else 0.6, 0.15)
    if k < 2: sp(ratchet(3, 0.12), s + 0.02, 0.35, 0.15)
sp(fader_slide(0.2), T["st"][2], 0.55, 0.15); sp(boom(1.0), T["st"][2], 0.6); sp(sparkle(10, 0.4, 0.8), T["st"][2] + 0.05, 0.3)
sp(reverse_swell(0.4), T["st"][2] - 0.4, 0.2)
sp(hop(0.3), 6.32, 0.22, 0.4)
for j, f in enumerate([1175, 1397, 1760]): sp(fm_bell(f, 0.8, 1.2, 2.0, 1.0), T["f4"] + 0.32 + j * 0.06, 0.16, 0.2)
# chips fly into the phone and land as blocks
sp(soft_whoosh(0.4, 500, 3000), T["ph"], 0.2)
for k, f in enumerate(T["fill"]):
    if k in (0, 2, 3, 6): sp(soft_whoosh(0.3, 800, 4000), f - 0.35, 0.15, (k % 3 - 1) * 0.3)
    sp(thock(), f, 0.38, (k % 3 - 1) * 0.3); sp(glass([2349, 2794, 3136, 3520, 4186, 4699, 5274][k], 0.25), f + 0.2, 0.12)
# lime wave paints the site
sp(shimmer_up(T["wave1"] - T["wave0"] + 0.1), T["wave0"], 0.32)
sp(swipe(0.8, 900, 7000, 0.8), T["wave0"], 0.2)
sp(boom(0.9), T["wave1"], 0.45); sp(sparkle(10, 0.5, 0.8), T["wave1"] + 0.05, 0.3)
for k in range(5): sp(glass([2349, 2794, 3520, 4186, 4699][k], 0.35), T["wave1"] + 0.2 + k * 0.2, 0.15, (k - 2) * 0.2)
for w in (T["wave1"] + 0.1, T["wave1"] + 0.55): sp(hop(0.25), w, 0.15, 0.4)
# order
sp(hop(0.25), T["size"] - 0.42, 0.22, -0.2); sp(snap(), T["size"], 0.3, -0.2); sp(marimba(note(81), 0.5), T["size"] + 0.02, 0.25, -0.2)
sp(hop(0.25), T["btn"] - 0.42, 0.22)
sp(snap(), T["btn"], 0.35); sp(glass(3520, 0.4), T["btn"], 0.25); sp(sparkle(12, 0.4, 0.9), T["btn"] + 0.02, 0.35)
for j, m in enumerate([74, 77, 81, 86]): sp(marimba(note(m), 0.6), T["toast"] + j * 0.06, 0.28, (j - 1.5) * 0.2)
sp(hop(0.3), T["toast"] + 0.05, 0.22, 0.3)
# lime notes = new orders
for k, w in enumerate(T["planes"]):
    sp(fall_whistle(0.4), w - 0.4, 0.2, (-0.4, 0.4, 0.0)[k])
    sp(thock(), w, 0.35); sp(hop(0.25), w, 0.15, 0.4)
    for j, m in enumerate([(81, 86), (84, 88), (86, 93)][k]): sp(marimba(note(m), 0.5), w + j * 0.07, 0.3, (-0.3, 0.3, 0)[k])
# riser and drop
sp(hop(0.3), T["outro0"], 0.3, -0.5)
sp(riser(0.6), T["drop"] - 0.6, 0.3); sp(needle_scratch(0.3), T["drop"] - 0.32, 0.25)
sp(boom(1.2), T["drop"], 0.75); sp(crash(1.6), T["drop"], 0.25)
sp(boom(1.0), T["t6b"], 0.55); sp(snap(), T["t6b"], 0.25)
sp(swipe(0.75, 2000, 9500, 0.8), T["sweep"], 0.16, -0.3)
sp(soft_whoosh(0.5, 3000, 300), T["s6_out"], 0.22)
# outro: cursor jumps into the logo
sp(reverse_swell(0.4), T["tile"] - 0.4, 0.22)
sp(boom(1.0), T["tile"], 0.6)
sp(hop(0.3), T["cur0"], 0.35, 0.2)
sp(shimmer_up(T["wave2_1"] - T["wave2_0"] + 0.1), T["wave2_0"], 0.18, -0.2)
sp(snap(), T["click2"], 0.35); sp(glass(3520, 0.4), T["click2"], 0.25)
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
MUSIC_GAIN, DRUM_GAIN = 1.0, 0.85
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
dest = os.path.join("/tmp/claude-0/-home-claude-buildwave-media/7c5179ff-f3c6-5954-85d6-fc31dc7fbada/scratchpad", "vid_audio.wav")
wavfile.write(dest, SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
print("wrote", dest, "sec", round(n_out / SR, 2), "kicks", len(kick_times))
