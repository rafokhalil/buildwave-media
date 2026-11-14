"""Timeline: 'Müştərini tuta bilmirsən?' — CLAW MACHINE: in the hook a claw grabs a customer and drops him (he runs off);
an arcade claw cabinet rises with the florist site's pieces piled inside (Düymə / Şəkil / Buket / Buket); cursor mascot
steers the joystick and stomps the big button; first grab slips ('!'), second grab works and drops the piece into the
chute, then 3 fast grabs; the cabinet morphs into a phone, pieces fly into their slots, lime wave paints the florist
site; mascot picks 'Sabah' + 'Sifariş et' (toast); the claw now drops 3 customers into the phone (new orders).
Drop 'Müştərini sayt tutsun.'; logo outro."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.6, 8.3, 10.75, 12.75, 15.25], hOut=[5.45, 8.1, 10.6, 12.6, 15.1, 17.45],
    hgrab=0.62, hslip=1.32,
    cab=2.55,
    joy0=3.3, joy1=4.1, press=[4.3, 6.4, 8.3, 9.05, 9.8],
    grab1=5.0, slip=5.3, grab2=7.05, rel2=8.05,
    morph=10.6, morph1=11.2, fly=11.25, wave0=12.0, wave1=12.6,
    size=13.3, btn=13.9, toast=14.05,
    planes=[15.55, 16.15, 16.75],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
