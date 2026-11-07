"""Timeline: 'Sayt da ev kimi tikilir.' — BLUEPRINT → 3D BUILD: violet blueprint grid in a phone, cursor mascot draws
the site plan line by line (lime pen trail, dimension arrows), phone tilts into isometric 3D, grey slabs (floors)
drop from the sky one by one (clank), the last one lands crooked, phone flattens, mascot stomps it straight (snap),
lime wave paints the slabs into the furniture shop site, mascot bounces on the sofa, adds to cart, toast;
drop 'Planı biz çəkək.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, card=0.15, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.9, 8.9, 12.2, 15.0], hOut=[5.7, 8.7, 12.0, 14.85, 17.45],
    phone=0.1,
    draw=[2.85, 3.55, 4.25, 4.95], dd=0.6,
    tilt0=6.0, tilt1=6.6,
    land=[6.95, 7.4, 8.35, 7.85], fall=0.45,
    flat0=9.0, flat1=9.6, ex=9.6, st=[10.4, 10.9], fix=10.9,
    wave0=12.4, wave1=13.2, sofa=13.95, boing=[14.15, 14.45],
    chip=15.25, btn=15.8, toast=15.95, lab=[16.3, 16.65, 17.0],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
