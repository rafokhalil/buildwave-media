"""Timeline: 'Saytın şansa qalıb?' — SLOT MACHINE: a 3-reel slot cabinet spins site parts under the hook and lands on
junk (90s 'SALAM!!' / 404 / ✕); cursor mascot rides the lever down — junk again (loading spinner, '!'); 'Şansla olmur.
Əllə quraq.' — mascot stomps each reel by hand (ratchet) onto Logo / Şəkil / Düymə, frames turn lime, JACKPOT (lights,
lime coins burst into the tray); cabinet morphs into a phone, the 3 symbols fly into their slots, lime wave paints the
language-course site; mascot picks 18:00 + 'Qeydiyyat' (toast); 3 lime coins drop in = new students.
Drop 'Şansa buraxma, gəl quraq.'; logo outro."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.6, 8.3, 10.75, 12.75, 15.25], hOut=[5.45, 8.1, 10.6, 12.6, 15.1, 17.45],
    cab=0.0, hs0=0.2, hstop=[0.95, 1.2, 1.45], hbad=1.5,
    pull=3.3, pull1=3.65, spin=3.6, stop=[4.5, 4.8, 5.1], bad=5.15,
    st=[[6.0, 6.25, 6.5], [6.95, 7.2], [7.7]], jack=8.0,
    morph=10.6, morph1=11.2, fly=11.25, wave0=12.0, wave1=12.6,
    size=13.3, btn=13.9, toast=14.05,
    planes=[15.55, 16.15, 16.75],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
