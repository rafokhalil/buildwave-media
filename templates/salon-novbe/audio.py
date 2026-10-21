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


# ------------------------------ MUSIC ------------------------------
def kick():
    n = int(0.38 * SR)
    t = np.arange(n) / SR
    f = 46 + 120 * np.exp(-t / 0.032)
    s = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.15))
    c = lowpass(rng.standard_normal(n), 3000) * np.exp(-t / 0.003) * 0.35
    return s + c


def hat(open_=False, vel=1.0):
    d = 0.14 if open_ else 0.04
    n = int(d * SR)
    t = np.arange(n) / SR
    return highpass(rng.standard_normal(n), 7000, 2) * np.exp(-t / (0.05 if open_ else 0.012)) * vel


def clap(vel=1.0):
    n = int(0.22 * SR)
    t = np.arange(n) / SR
    x = bandpass(rng.standard_normal(n), 1100, 4200)
    env = np.exp(-t / 0.075)
    for off in (0.0, 0.011, 0.023):
        j = int(off * SR); env[j:j + int(0.006 * SR)] += 1.2
    return x * env * 0.55 * vel


def bass_note(f, dur):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * 2 * f * t) + 0.18 * np.sin(2 * np.pi * 3 * f * t)
    s = np.tanh(1.6 * s) * 0.6
    env = np.minimum(1, t / 0.006) * np.exp(-t / (dur * 0.9)) * np.minimum(1, (dur - t) / 0.03)
    return s * env


def pad_chord(freqs, dur, vel=1.0, rel=0.6):
    n = int(dur * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for f in freqs:
        for det in (-0.7, 0.0, 0.7):
            ph = rng.uniform(0, 6.28)
            s += np.sin(2 * np.pi * (f + det) * t + ph) + 0.35 * np.sin(2 * np.pi * 2 * (f + det) * t + ph * 1.3)
    s = lowpass(s, 1500)
    env = np.minimum(1, t / 0.25) * np.minimum(1, (dur - t) / rel)
    return s * env * vel / (len(freqs) * 3)


CH = {
    "Am": dict(root=110.00, pad=[220.00, 261.63, 329.63], arp=[440.00, 523.25, 659.25, 523.25]),
    "F":  dict(root=87.31,  pad=[174.61, 220.00, 261.63], arp=[349.23, 440.00, 523.25, 440.00]),
    "C":  dict(root=130.81, pad=[261.63, 329.63, 392.00], arp=[523.25, 659.25, 783.99, 659.25]),
    "G":  dict(root=98.00,  pad=[196.00, 246.94, 293.66], arp=[392.00, 493.88, 587.33, 493.88]),
}
PROG = ["Am", "F", "C", "G"] * 3
BAR = 2.0
DROP = T["drop"]        # 18.0
END = T["pill"]         # 22.0 final hit
FILL0 = 17.0            # snare roll start
GAP = (17.5, 18.0)      # drums/bass out before the drop
TRANS = (5.5, 6.0)      # small breath between S2 and S3

def in_rng(t, r):
    return r[0] <= t < r[1]

kick_times = []

# pad
for b in range(11):
    name = PROG[b]
    vel = 0.5 if b == 0 else (0.75 if b < 3 else 1.0)
    place(pad_chord(CH[name]["pad"], 2.5, vel), b * BAR, 1.0, 0.0, "music")
place(pad_chord(CH["Am"]["pad"] + [440.0], 2.0 + TAIL - 0.2, 1.15, rel=1.6), END, 1.0, 0.0, "music")

# hats
t = 0.75
while t < END - 0.01:
    if not in_rng(t, GAP):
        off = abs((t % 0.5) - 0.25) < 1e-6
        if t < 2.0:
            if off: place(hat(False, 0.5), t, 0.2, 0.2, "drum")
        else:
            vel = (0.32 if t < 6.0 else 0.42) * (1.5 if off else 1.0)
            if t >= 6.0 and abs((t % 1.0) - 0.75) < 1e-6:
                place(hat(True, 0.55), t, 0.24, 0.25, "drum")
            else:
                place(hat(False, vel), t, 0.22, -0.15 if int(t * 4) % 2 else 0.2, "drum")
    t = round(t + 0.25, 4)

# kick (4 on the floor from 2.0)
t = 2.0
while t < END:
    if not in_rng(t, GAP) and not (t == 5.5):
        place(kick(), t, 0.9, 0.0, "drum"); kick_times.append(t)
    t = round(t + 0.5, 4)
place(kick(), END, 1.0, 0.0, "drum"); kick_times.append(END)

# claps on 2 & 4 from S3, roll before the drop
t = 6.0
while t < END:
    for off in (0.5, 1.5):
        tt = t + off
        if tt < FILL0 or (DROP <= tt < END):
            place(clap(0.9), tt, 0.5, 0.0, "drum")
    t += 2.0
for k in range(8):
    place(clap(0.3 + 0.09 * k), FILL0 + k * 0.0625, 0.42, 0.0, "drum")

# bass from bar 1
for b in range(1, 11):
    root = CH[PROG[b]]["root"]
    for off, dur, mul in ((0.0, 0.5, 1.0), (0.75, 0.22, 1.0), (1.0, 0.4, 1.0), (1.5, 0.4, 2.0)):
        tt = b * BAR + off
        if in_rng(tt, GAP) or tt >= END or in_rng(tt, TRANS):
            continue
        place(bass_note(root * mul, dur), tt, 0.48, 0.0, "music")
place(bass_note(CH["Am"]["root"], 1.6), END, 0.55, 0.0, "music")

# arpeggio: 8ths in S3/S4, 16ths in S5 and drop/logo
for b in range(3, 11):
    arp = CH[PROG[b]]["arp"]
    step = 0.25 if b < 7 else 0.125
    gain = 0.16 if b < 5 else (0.19 if b < 7 else 0.22)
    k = 0; tt = b * BAR
    while tt < (b + 1) * BAR - 1e-6:
        if not in_rng(tt, (FILL0 + 0.5, DROP)) and tt < END:
            f = arp[k % 4] * (2.0 if (b >= 7 and (k // 4) % 2 == 1) else 1.0)
            place(fm_bell(f, 0.4, 1.6, 2.0, 1.0), tt, gain, (-0.35 if k % 2 else 0.35), "music")
        k += 1; tt = round(tt + step, 4)

# sidechain
duck = np.ones(N)
seg = int(0.45 * SR)
ds = 1.0 - 0.6 * np.exp(-(np.arange(seg) / SR) / 0.11)
for kt in kick_times:
    i = int(kt * SR); m = min(seg, N - i)
    if m > 0: duck[i:i + m] = np.minimum(duck[i:i + m], ds[:m])
M_L *= duck; M_R *= duck

# =============================== SFX SCORE ===============================
PENT = [440.00, 523.25, 659.25, 783.99, 880.0, 1046.5, 1318.5]

# ---- S1: streaks converge into the logo ----
place(reverse_swell(0.75), 0.0, 0.32)
place(whoosh(0.7, 200, 4000, q=1.0, peak=0.8), 0.05, 0.18, -0.3)
place(whoosh(0.6, 300, 5000, q=1.0, peak=0.8), 0.15, 0.16, 0.3)
place(thud(140, 40, 0.9), T["hit"], 0.95)
place(sparkle(8, 0.3, 0.7), T["hit"] + 0.02, 0.4)
place(chime(1318.5, 1.3, 0.6), T["hit"] + 0.02, 0.25)
place(glide(500, 1500, T["wave1"] - T["wave0"], 0.8), T["wave0"], 0.12, -0.2)
for i in range(9):
    place(tick(1700 + i * 170, 0.04, 0.7), T["wm1"] + i * 0.05, 0.32, (i - 4) * 0.06)
place(whoosh(0.6, 200, 5000, q=0.9, peak=0.75), T["s1_out"] - 0.05, 0.36)

# ---- S2: DMs pile up ----
place(whoosh(0.7, 2500, 250, q=0.9, peak=0.3), T["s2_in"], 0.22, 0.1)
place(tap(110, 0.2), T["s2_in"] + 0.65, 0.45)
place(swipe(0.18, 1600, 6500), T["h2a"], 0.15, -0.2)
place(swipe(0.18, 1600, 6500), T["h2b"], 0.15, -0.2)
for i, t0 in enumerate(T["msg"]):
    f = PENT[(i * 2) % 5 + (1 if i > 6 else 0)] * 2
    gain = 0.20 + 0.012 * i
    place(fm_bell(f, 0.45, 1.4, 3.0, 1.0), t0, gain, (-0.4 if i % 2 else 0.4))
    place(tick(2400, 0.02, 0.5), t0, 0.12)
place(thud(90, 40, 0.5), T["shake"], 0.55)
place(zap(0.18), T["shake"], 0.2)
place(whoosh(0.6, 3500, 200, peak=0.4), T["s2_out"], 0.3, -0.2)

# ---- S3: site builds itself ----
place(whoosh(0.5, 260, 3200, peak=0.6), T["s3_in"], 0.22, 0.15)
place(swipe(0.18, 1600, 6500), T["h3a"], 0.14)
place(swipe(0.18, 1600, 6500), T["h3b"], 0.14)
place(glide(380, 1700, T["out1"] - T["out0"], 0.9), T["out0"], 0.12, 0.2)
place(swipe(T["out1"] - T["out0"], 3000, 9000, 0.6), T["out0"], 0.08, -0.2)
place(tap(120, 0.18), T["panel"], 0.45)
for i in range(14):
    place(tick(1300 + rng.uniform(-120, 200), 0.028, 0.5), T["url"] + i * (0.55 / 14), 0.24, -0.1)
for t0, f in ((T["hero"], 523.25), (T["btn"], 659.25)):
    place(swipe(0.2, 1500, 6000), t0 - 0.03, 0.17)
    place(tap(140, 0.14), t0 + 0.3, 0.38)
    place(fm_bell(f, 0.7, 2.0, 2.0, 1.0), t0 + 0.3, 0.2)
for i, t0 in enumerate(T["card"]):
    place(swipe(0.16, 1800, 7000), t0 - 0.02, 0.13, (-0.3 if i % 2 == 0 else 0.3))
    place(tap(150, 0.12), t0 + 0.3, 0.3, (-0.3 if i % 2 == 0 else 0.3))
    place(fm_bell([523.25, 659.25, 783.99, 1046.5][i], 0.6, 1.8, 2.0, 1.0), t0 + 0.3, 0.2, (-0.3 if i % 2 == 0 else 0.3))
for i, t0 in enumerate(T["bub"]):
    place(whoosh(0.45, 600, 3000, q=1.1, peak=0.5), t0 - 0.05, 0.14, -0.5 + i * 0.3)
    place(chime([1318.5, 1568.0, 1760.0][i], 0.9, 0.7), t0 + 0.45, 0.32, -0.2 + i * 0.2)
    place(tick(3000, 0.03, 0.8), t0 + 0.45, 0.2)
place(chime(2093.0, 0.9, 0.6), T["bub"][2] + 0.62, 0.22, 0.4)
place(riser(0.6, 9000), T["push"], 0.3)
place(whoosh(0.7, 200, 6000, q=0.9, peak=0.85), T["push"], 0.3)

# ---- S4: customer orders ----
place(whoosh(0.6, 3000, 300, peak=0.35), T["s4_in"], 0.2, -0.1)
place(swipe(0.18, 1600, 6500), T["h4a"], 0.14)
place(swipe(0.18, 1600, 6500), T["h4b"], 0.14)
for dt, f in ((0.4, 523.25), (0.72, 659.25), (0.85, 783.99)):
    place(swipe(0.14, 2000, 7000), T["s4_in"] + dt, 0.1)
    place(fm_bell(f, 0.5, 1.6, 2.0, 1.0), T["s4_in"] + dt + 0.05, 0.13)
place(click(), T["tap"], 0.85)
place(click(), T["tapSlot"], 0.7)
place(fm_bell(1046.5, 0.6, 1.6, 2.0, 1.0), T["tapSlot"] + 0.02, 0.2)
n_ld = 8
for k in range(n_ld):  # loading: accelerating soft ticks
    frac = 1 - (1 - k / n_ld) ** 1.6
    place(tick(1800 + k * 120, 0.025, 0.6), T["load0"] + frac * (T["order"] - T["load0"] - 0.08), 0.16, 0.1)
place(thud(110, 46, 0.6), T["order"], 0.55)
for j, f in enumerate((523.25, 659.25, 783.99, 1046.5)):
    place(fm_bell(f, 1.2, 1.6, 2.0, 1.0), T["order"] + 0.05 + j * 0.07, 0.3, (j - 1.5) * 0.15)
place(sparkle(10, 0.35, 0.8), T["order"] + 0.3, 0.38)
place(chime(2093.0, 1.2, 0.6), T["order"] + 0.32, 0.14)
place(whoosh(0.7, 2500, 200, peak=0.4), T["s4_out"], 0.24)

# ---- S5: night city ----
place(whoosh(0.8, 150, 1500, q=0.9, peak=0.6), T["s5_in"], 0.22)
place(swipe(0.18, 1600, 6500), T["h5a"], 0.13)
place(swipe(0.18, 1600, 6500), T["h5b"], 0.13)
place(swipe(0.2, 1500, 6000), T["card5"], 0.14)
for i, t0 in enumerate(T["step"]):
    place(fm_bell([659.25, 783.99, 880.0, 1046.5][i], 0.6, 1.6, 2.0, 1.0), t0, 0.2 if i < 3 else 0.3, 0.3)
    place(tick(2600, 0.03, 0.6), t0, 0.14, 0.3)
rd = T["route1"] - T["route0"]
place(glide(300, 820, rd, 0.9), T["route0"], 0.05, -0.2)
place(whoosh(rd, 400, 2400, q=1.6, peak=0.5), T["route0"], 0.1, 0.2)
for i, t0 in enumerate(T["cell"]):
    place(tick(2200 + (i % 5) * 260, 0.03, 0.6), t0, 0.12, (-0.5 + (i % 7) * 0.16))
    if i % 3 == 0:
        place(fm_bell([1318.5, 1568.0, 1760.0, 2093.0][(i // 3) % 4], 0.45, 1.2, 3.0, 1.0), t0, 0.08, (-0.4 + (i % 5) * 0.2))
place(chime(1318.5, 1.4, 0.7), T["arrive"], 0.3)
place(sparkle(8, 0.3, 0.7), T["arrive"] + 0.02, 0.3)
place(riser(DROP - 16.6, 9000), 16.6, 0.5)
place(reverse_swell(0.9), DROP - 0.9, 0.3)

# ---- S6: drop tagline ----
place(thud(150, 38, 1.0), DROP, 0.55)
place(crash(2.0), DROP, 0.17)
place(zap(0.2), DROP + 0.01, 0.14)
place(thud(130, 42, 0.8), T["t6b"], 0.8)
place(fm_bell(1318.5, 1.0, 2.2, 2.0, 1.0), T["t6b"], 0.25)
place(swipe(0.75, 2000, 9500, 0.8), T["sweep"], 0.18, -0.3)
place(chime(2637.0, 1.0, 0.5), T["sweep"] + 0.35, 0.1, 0.3)
place(whoosh(0.5, 3000, 300, peak=0.4), T["s6_out"], 0.24)

# ---- S7: logo + CTA ----
place(reverse_swell(0.4), T["tile"] - 0.4, 0.22)
place(thud(125, 38, 0.9), T["tile"], 0.85)
place(sparkle(6, 0.25, 0.6), T["tile"] + 0.05, 0.3, 0.3)
place(glide(500, 1500, T["wave2_1"] - T["wave2_0"], 0.8), T["wave2_0"], 0.12, -0.2)
place(whoosh(0.55, 800, 2600, q=1.0, peak=0.5), T["cur0"], 0.14, 0.2)
place(click(), T["click2"], 0.9)
place(sparkle(10, 0.3, 0.8), T["click2"] + 0.02, 0.4, -0.1)
for i in range(9):
    place(tick(1700 + i * 170, 0.04, 0.7), T["wm"] + i * 0.06, 0.35, (i - 4) * 0.06)
place(swipe(0.2, 1500, 6500), T["cta1"], 0.16)
place(fm_bell(659.25, 0.9, 2.2, 2.0, 1.0), T["cta1"], 0.22)
place(swipe(0.22, 1500, 7000), T["cta2"], 0.18)
place(fm_bell(880.0, 1.0, 2.4, 2.0, 1.0), T["cta2"], 0.26)
place(crash(1.6), END, 0.22)
for j, f in enumerate((440.0, 523.25, 659.25, 880.0, 1318.5)):
    place(fm_bell(f, 1.8, 1.8, 2.0, 1.0), END + 0.02 + j * 0.06, 0.26, (j - 2) * 0.12)
place(swipe(0.7, 2200, 9000, 0.7), END + 0.45, 0.1, 0.2)

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
MUSIC_GAIN, DRUM_GAIN = 0.50, 0.40
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
dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vidb_audio.wav")
wavfile.write(dest, SR, (np.clip(out, -1, 1) * 32767).astype(np.int16))
print("wrote", dest, "sec", round(n_out / SR, 2), "kicks", len(kick_times))
