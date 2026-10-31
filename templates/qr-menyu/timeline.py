"""Timeline: 'Menyun hələ kağızdadır?' — old paper menu (stain, prices crossed out & re-scribbled, 'Bitib!' sticky
note) → paper crumples into a ball, cursor mascot kicks it into a bin → wooden table, QR stand flips up out of the
table, QR modules pop in, phone scans (scan line), QR pixels fly into the phone and stack into a grey skeleton →
lime wave paints it into the restaurant menu site 'Tandır Evi' → mascot taps 3 '+' buttons (cart counter), order to
'Masa 7' toast; drop 'Kağız getdi, QR gəldi.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, card=0.2, curIn=1.0, hookOut=2.65,
    hA=[2.8, 5.9, 8.9, 11.8, 15.0], hOut=[5.7, 8.7, 11.65, 14.85, 17.45],
    stain=1.4, scr=[3.2, 3.7, 4.2], note=4.7,
    crum0=6.0, crum1=6.7, kick=7.05, bin=7.55, menuOut=8.0,
    table=8.75, qr=9.1, mods=9.35, phone=9.9, scan0=10.25, scan1=10.95, fly0=11.0, fly1=11.6,
    center=11.65, wave0=12.3, wave1=12.95,
    plus=[15.2, 15.7, 16.2], order=16.65, toast=16.8,
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
