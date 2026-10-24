"""Timeline: '1 sayt, 3 stil' — grey wireframe barber site; lime wave paints style 1 (Sadə),
3D phone flip into style 2 (Rəngli), click circle-reveal into style 3 (Lüks), 3-phone line-up
'Hansı sənindir?' (comment 1/2/3), drop, logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, hint=0.25, cur_in=0.9, taps=[1.5, 2.0, 2.5], hookOut=2.9,
    st=[3.1, 7.3, 11.2], stOut=[6.9, 10.9, 14.6],
    wave0=3.3, wave1=4.6, push=6.9, flip0=7.0, flip1=7.55, stick=7.5,
    click=11.0, circ1=11.75,
    grid=14.8, gridH=14.9, chips=[15.3, 15.45, 15.6], ghint=15.6, gtap=[16.0, 16.6, 17.2], outro0=17.4,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
