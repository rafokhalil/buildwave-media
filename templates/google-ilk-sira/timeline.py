"""Timeline: 'Google-da səni tapırlar?' — a search panel: query types, grey results cascade, mascot scrolls
pages (Səhifə 1→5) and can't find the clinic; a new card appears and the lime wave paints it; the card climbs
the list to #1 with the mascot riding on it; tap → card morphs into the dental site, booking toast; 3 chips
(how); final #1 card; drop 'Qoy axtaran səni tapsın.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, panel=0.25, type0=0.75, type1=1.95, curIn=1.0, search=2.2, cards=2.35,
    hookOut=3.3, hA=[3.45, 5.75, 7.75, 9.35, 10.75], hOut=[5.6, 7.6, 9.2, 10.6, 12.55],
    scroll0=3.9, scroll1=5.3, bangT=5.45, reset=6.0, slot=6.3, wave0=7.0, wave1=7.75,
    climb=[8.2, 8.7, 9.2], top=9.6, tapCard=10.9, morph=11.0, click=12.0, toast=12.15,
    fall=12.6, secret=12.8, chips=[13.4, 14.2, 15.0], secOut=15.75,
    bars=16.0, finIn=16.1, outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
