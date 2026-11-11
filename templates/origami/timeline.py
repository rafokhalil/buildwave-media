"""Timeline: 'Hələ vərəqə paylayırsan?' — ORIGAMI / PAPER PLANE: an ugly paper flyer for a clothing boutique falls
toward a bin with other flyers; the cursor mascot catches it and folds it origami-style (2 corner folds, fold in half,
wings open) into a paper plane, rides it through a loop with a dashed lime trail and dives into a phone; the paper
unfolds on screen as cream skeleton blocks, the lime wave paints them into the boutique site; mascot picks size M +
'Səbətə at' (toast); small paper planes = orders fly into the phone. Drop 'Vərəqə atılır, sayt qalır.'; logo outro."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.6, 8.3, 11.9, 15.0], hOut=[5.45, 8.1, 11.75, 14.85, 17.45],
    catch=2.75,
    fL=[3.3, 3.8], fR=[3.95, 4.45], fH=[4.65, 5.15], fW=[5.35, 5.85],
    fly0=6.0, fly1=7.7, phone=6.3,
    unf=7.75, wave0=8.45, wave1=9.25,
    hop=9.9, size=12.4, btn=13.1, toast=13.25,
    planes=[15.1, 15.75, 16.4],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
