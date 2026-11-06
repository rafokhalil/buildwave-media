"""Timeline: 'Saytın parça-parçadır?' — jigsaw puzzle site: 4 scattered puzzle pieces of a gym site, cursor mascot
drags each into its slot on the phone (snap), last piece missing ('Bir parça çatmır…'), mascot looks around, runs
off and pushes the big 'Məşqə yazıl' piece in upside-down, bonk, spins it, final snap → lime wave melts the seams →
taps 19:00 + button, toast; ✓ labels; drop 'Parçaları biz yığaq.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, card=0.15, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.9, 8.9, 12.2, 15.0], hOut=[5.7, 8.7, 12.0, 14.85, 17.45],
    phone=2.55, park=2.6,
    grab=[3.05, 4.2, 6.0, 7.05], snap=[3.6, 4.85, 6.6, 7.65],
    gap=8.05, q=8.6, runOff=9.7, eIn0=10.3, eIn1=11.1, bonk=11.1, ex=11.2, spin0=11.4, spin1=11.85, eSnap=12.05,
    wave0=12.4, wave1=13.2,
    chip=14.15, btn=14.75, toast=14.9, lab=[15.6, 16.1, 16.6],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
