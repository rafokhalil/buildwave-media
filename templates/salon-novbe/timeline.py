"""Shared timeline (seconds) for the Buildwave story video v3.
Music: 120 BPM, beat = 0.5 s, bar = 2 s. Scene changes land on bar lines."""
FPS = 30
RENDER_FPS = 60          # rendered at 60, blended to 30 for motion blur
DURATION = 24.0
BPM = 120

MSG_T = [2.75, 3.15, 3.50, 3.80, 4.05, 4.25, 4.42, 4.57, 4.70, 4.82, 4.93, 5.03]
CARD_T = [7.55, 7.70, 7.85, 8.00]
BUB_T = [8.35, 8.55, 8.75]           # "Qiymət?" bubbles fly to price tags (land +0.45)
PIN_T = [14.90, 15.25, 15.55, 15.80, 16.05, 16.30]
STEP_T = [14.55, 14.90, 15.20, 16.45]

T = dict(
    # S1 intro: light streaks -> logo
    streak0=0.0, hit=0.75, wave0=0.95, wave1=1.35, wm1=1.05, s1_out=1.60,
    # S2 DMs
    s2_in=1.85, h2a=2.30, h2b=2.55, shake=5.15, s2_out=5.55,
    # S3 website builds
    s3_in=5.90, h3a=6.10, h3b=6.40, out0=6.15, out1=6.75, panel=6.60,
    url=6.80, hero=7.00, btn=7.35, push=9.45,
    # S4 customer orders
    s4_in=9.90, h4a=10.15, h4b=10.40, tapSlot=10.95, tap=11.45, load0=11.55, order=12.00, s4_out=13.30,
    # S5 night city map
    s5_in=13.55, h5a=14.05, h5b=14.30, card5=14.30, route0=15.20, route1=16.40,
    arrive=16.45, s5_out=17.40,
    # S6 drop tagline
    drop=18.00, t6b=18.50, sweep=18.90, s6_out=19.65,
    # S7 logo + CTA
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
T["msg"] = MSG_T
T["card"] = CARD_T
T["bub"] = BUB_T
T["pin"] = PIN_T
T["step"] = STEP_T

import random as _r
_r.seed(5)
CELL_T = sorted(round(14.45 + i*0.085 + _r.uniform(-0.02,0.02),3) for i in range(30))
T["cell"] = CELL_T
