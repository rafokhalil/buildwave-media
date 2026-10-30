"""Timeline: 'Sənə sayt lazımdır?' — kinetic checklist: 3 signs (night DMs / everyone asks the price / can't find
the address), each with its own mini-animation (chat at 23:40, raining 'Qiymət?' bubbles piling up, a lost pin on a
map); the cursor mascot ticks each box; lime wave sweeps the checklist into the pet shop site 'Pəncə Pet'; night
order toast 23:41; 3 answer labels; drop 'Qoy saytın cavab versin.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, card=0.2, curIn=1.0, hookOut=2.65,
    hA=[2.8, 5.9, 8.9, 11.8, 13.1, 15.0], hOut=[5.7, 8.7, 11.65, 12.95, 14.85, 17.45],
    zone=2.75, bub=[3.15, 3.7, 4.25], row=[4.5, 7.5, 10.4], tick=[5.1, 8.1, 11.0], zoneOut=[5.75, 8.75, 11.7],
    rain0=6.05, rain1=7.4, map0=8.95, pin0=9.2, q=[9.45, 9.85, 10.25],
    allFlash=12.0, wave0=12.3, wave1=12.95, click=14.3, toast=14.45, labs=[15.3, 15.8, 16.3],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
