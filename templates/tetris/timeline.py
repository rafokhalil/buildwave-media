"""Timeline: 'Hələ zənglə növbə yazırsan?' — SITE TETRIS: a busy landline (Məşğuldur pills) for a dental clinic; a phone
with a tetris grid slides in and the dental site's blocks fall as tetris pieces bottom-up with a ghost outline; one card
falls sideways and gets stuck, cursor mascot presses the big rotate key then the hard-drop key; rows complete -> flash,
lime wave paints the blocks into the clinic site; mascot picks 11:00 + 'Növbə al' (toast); 3 lime tetrominoes = new
bookings drop in. Drop 'Növbəni sayt yazsın.'; logo outro."""
FPS = 30
RENDER_FPS = 60
DURATION = 24.0
BPM = 120
T = dict(
    hookA=0.0, hookB=0.12, sub=0.9, curIn=1.2, hookOut=2.65,
    hA=[2.8, 5.6, 8.3, 11.9, 15.0], hOut=[5.45, 8.1, 11.75, 14.85, 17.45],
    busy=[0.35, 0.95, 1.55],
    phone=2.6,
    # piece fall starts (land = start + 0.38): btn, chips, card1, card2(crooked), hero, brand, url
    fall=[3.2, 3.65, 4.1, 4.55, 7.0, 7.35, 7.6],
    stuck=4.93, rot=5.95, hard=6.55,
    clear=8.05, wave0=8.45, wave1=9.25,
    size=12.4, btn=13.1, toast=13.25,
    planes=[15.1, 15.75, 16.4],
    outro0=17.45,
    drop=18.0, t6b=18.5, sweep=18.9, s6_out=19.65,
    streak2=19.70, tile=20.00, wave2_0=20.20, wave2_1=20.70, cur0=20.25, cur1=20.80,
    click2=20.90, wm=21.00, cta1=21.40, cta2=21.70, pill=22.00,
)
