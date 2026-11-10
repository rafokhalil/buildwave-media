"""Timeline: 'Otaqların boş qalır?' — BEFORE/AFTER SLIDER: a guesthouse site in a phone with an Əvvəl/Sonra slider.
Old 90s site (grey, Times, blue links, marquee, hit counter) on the left, new site on the right. Cursor mascot rides the
slider knob: 2 pulls reveal the new site, it gets dragged back to the old one ("!" + 8-bit glitch), then a final pull
with the lime wave wipes the old site away. Mascot picks a day + books (toast); a little house under the phone lights a
window per booking, night falls (moon, 02:14) and the last windows light up -> "Dolu ✓". Slider comes back at 50%:
"Hansından sifariş edərdin?" (comment bait). Drop 'Otaqlar boş qalmasın.'; logo outro (120 BPM)."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, card=0.15, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.6, 8.2, 12.0, 15.0], hOut=[5.45, 8.0, 11.85, 14.85, 17.45],
    phone=0.1,
    grab=2.75,
    drag=[[3.2, 3.75, .92, .62], [4.35, 4.9, .62, .30], [5.55, 6.0, .30, .82], [6.9, 7.7, .82, 0.0]],
    ex=6.0, glitch=6.05,
    wave0=6.9, wave1=7.7,
    chip=8.6, btn=9.15, toast=9.3,
    house=8.3, win=[9.45, 10.4, 11.1, 12.7, 13.4], night=12.0, full=14.0,
    back=15.05, back1=15.6,
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
