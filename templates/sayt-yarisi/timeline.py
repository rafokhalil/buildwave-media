"""Timeline: 'Saytın neçə saniyəyə açılır?' — split-screen race: two phones load the same car-service
site after F1-style start lights; slow one spins (mascot waits, yawns, falls asleep), fast one is painted
in by the lime wave in 0.9 s; mascot wakes, jumps to the fast phone and books; 3 'secret' chips;
8.7 vs 0.9 bars; drop 'Müştəri gözləmir.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=1.0, lights=[2.0, 2.5, 3.0], go=3.5, fastDone=4.4, hookOut=4.45,
    hA=[4.6, 6.2, 7.8, 9.3, 11.3], hOut=[6.05, 7.65, 9.15, 11.15, 12.55],
    curIn=3.6, yawn=6.1, sleep=7.6, wake=9.0, freeze=9.0, jump=9.2, land=9.7,
    row=10.2, click=10.9, toast=11.05,
    fall=12.6, secret=12.8, chips=[13.4, 14.2, 15.0], secOut=15.75,
    bars=16.0, barSlow=16.3, barFast=16.5, barsOut=17.45, outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
