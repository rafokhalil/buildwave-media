"""Timeline: 'Sifariş yarıda qalır?' — DOMINO CHAIN of books on a shelf (Klik · Kitab · [gap] · Ödəniş · Çatdırılma)
under the hook; cursor mascot pushes the first book, the chain topples and stops at the missing 'Səbət' book
('Bir halqa çatmır!', red dashed gap, '!'); books rewind upright, mascot rides the lime 'Səbət' book down from the sky
into the gap, pushes again — full chain topples and the last book rings a desk bell ('Sifariş gəldi!'); books fly
into a phone and become site blocks; lime wave paints the bookstore site; mascot picks a book + 'Səbətə at' (toast);
3 lime books drop in = new orders (banner + counter). Drop 'Zənciri biz quraq.'; logo outro."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, curIn=1.0, push1=1.6, fail=2.12, hookOut=2.65,
    hA=[2.8, 4.55, 6.3, 8.4, 9.95, 12.4, 14.9], hOut=[4.4, 6.15, 8.25, 9.8, 12.25, 14.75, 17.45],
    rw0=3.1, rw1=3.5, lb0=3.5, lb1=4.1, push2=4.9, bell=5.79,
    ph=6.0, fill=[6.45, 6.7, 6.95, 7.2, 7.45, 7.7, 7.95],
    wave0=8.6, wave1=9.2,
    size=10.6, btn=11.2, toast=11.35,
    planes=[12.9, 13.65, 14.4],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
