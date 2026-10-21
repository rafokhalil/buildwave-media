# Reel templates

`story-v3/` is the approved Buildwave Reel ("Sən yatırsan, sayt satır", 2026-10-21):
- `story.html`: all scenes; `render(t)` draws time t (1080x1920). Brand: Qara Voltaj.
- `timeline.py`: shared timing (scenes land on 2 s bars at 120 BPM). Visuals and audio both read it.
- `render.py`: Playwright → PNG frames at 60 fps (`python3 render.py all A B` for a frame range).
- `audio.py`: synthesized SFX + 120 BPM music → `vid_audio.wav`.

Encode (motion blur 60→30 fps, then shrink):
ffmpeg -framerate 60 -i vid_frames/f_%05d.png -i vid_audio.wav -filter_complex "[0:v]tmix=frames=2:weights='1 1',select='not(mod(n\,2))',setpts=N/30/TB[v]" -map "[v]" -map 1:a -af loudnorm=I=-14:TP=-1.0:LRA=7 -c:v libx264 -preset slow -crf 16 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -movflags +faststart big.mp4
ffmpeg -i big.mp4 -vf hqdn3d=1:1:4:4 -c:v libx264 -preset slow -crf 23 -maxrate 6M -bufsize 12M -pix_fmt yuv420p -c:a copy -movflags +faststart final.mp4
