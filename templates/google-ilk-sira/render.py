import sys, os, json, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from timeline import T, RENDER_FPS, DURATION
from playwright.sync_api import sync_playwright

SRC = os.path.dirname(os.path.abspath(__file__))
SCR = "/tmp/claude-0/-home-claude-buildwave-media/0e9a44db-545f-575c-a073-2509aef66159/scratchpad"
HTML = "file://" + os.path.join(SRC, "gs.html")


def run(times, outdir, prefix, start_index=0):
    os.makedirs(outdir, exist_ok=True)
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--disable-gpu-vsync"])
        ctx = b.new_context(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg = ctx.new_page()
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.add_init_script("window.T = " + json.dumps(T) + ";")
        pg.goto(HTML)
        pg.wait_for_timeout(700)
        pg.evaluate("document.fonts.ready")
        t0 = time.time()
        for i, t in enumerate(times):
            pg.evaluate(f"render({t})")
            pg.screenshot(path=os.path.join(outdir, f"{prefix}{start_index + i:05d}.png"))
        b.close()
    if errs:
        print("PAGE ERRORS:", errs[:5])
    return time.time() - t0


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode == "test":
        ts = [float(x) for x in sys.argv[2:]]
        el = run(ts, os.path.join(SCR, "vidd_test"), "t_")
        print("test frames", len(ts), "in", round(el, 1), "s")
    elif mode == "all":
        n = int(round(DURATION * RENDER_FPS))
        a = int(sys.argv[2]) if len(sys.argv) > 2 else 0
        z = int(sys.argv[3]) if len(sys.argv) > 3 else n
        ts = [i / RENDER_FPS for i in range(a, min(z, n))]
        el = run(ts, os.path.join(SCR, "vidd_frames"), "f_", start_index=a)
        print("frames", a, "to", min(z, n), "in", round(el, 1), "s")
