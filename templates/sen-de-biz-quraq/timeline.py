"""Timeline: 'Sən de, biz quraq' — cursor character, pixel explosion, crane build, wave paint (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.20, hookB=0.55, hops=[2.0, 2.35, 2.7, 3.0], poke=3.40, boom=3.50, land=4.15, getup=4.6,
    h2a=4.30, h2b=4.60, h2out=5.80, crane=5.40,
    blocks=[6.0, 7.0, 8.0, 8.5, 9.0, 9.5],          # nav, hero, card0, card1, card2, button
    gather=10.0, push=11.30, wave0=12.0, wave1=13.0,
    toBtn=13.9, click=14.5, toast=14.6, lie=15.4, outro0=16.6,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
T["stage"] = []  # unused
