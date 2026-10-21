"""Timeline for the 'Sayt necə yaranır' reel (120 BPM, 2 s bars)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hit=0.20, hookA=0.20, hookB=0.60, grid=0.95, hookUp=1.60,
    bgFill=7.05, navFill=7.25, heroFill=7.45, title=7.65, btnFill=8.20, contact=9.15,
    edIn=10.0, edOut=14.0, morph0=14.5, morph1=15.6,
    url=16.6, live=17.15, scroll0=17.0,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
T["stage"] = [2.0, 6.0, 10.0, 14.0, 16.5]
T["sk"] = [round(2.30 + i * 0.27, 3) for i in range(12)]      # sketch strokes
T["sw"] = [6.25, 6.40, 6.55, 6.70, 6.85]                         # palette swatches + Aa
T["cards"] = [8.45, 8.65, 8.85]
T["lines"] = [10.40, 10.85, 11.30, 11.75, 12.20, 12.65, 13.10]   # code lines
