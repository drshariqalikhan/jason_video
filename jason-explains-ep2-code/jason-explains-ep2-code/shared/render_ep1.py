"""Jason Explains Ep1 — "Don't Touch Stocks Until You Do These 3 Things".
Option A, 30 fps PIL, single pass, dark near-black navy, own stick figures
with the v2 articulated walk/run cycle. Frames piped to ffmpeg (no frame
files on disk). Work dir: ~/workspace/youtube-pipeline/jason-explains/ep1-before-investing
"""
import math, os, re, subprocess, sys, time
sys.path.insert(0, "/home/hatch/workspace/youtube-pipeline/whysector-pilot/build")
import render_pilot as R
from PIL import Image, ImageDraw

BASE = "/home/hatch/workspace/youtube-pipeline/jason-explains/ep1-before-investing"
OUT = f"{BASE}/build"
W, H = 1920, 1080
FPS = 30
BG = R.BG
TEXT, MUTED = R.TEXT, R.MUTED
RED, CYAN, WHITE = R.RED, R.CYAN, R.WHITE
AMBER, GOLD, GREEN = R.AMBER, R.GOLD, R.GREEN
font, ease_out_cubic, clamp01 = R.font, R.ease_out_cubic, R.clamp01
faded_text, faded_text_c = R.faded_text, R.faded_text_c

# measured mp3 durations (s) — ground truth from ffprobe (5 segments)
AUD = [28.248, 73.992, 63.672, 71.088, 67.680]
BEAT = 0.25
D = [a + (BEAT if i < 4 else 0.0) for i, a in enumerate(AUD)]
STARTS = []
_acc = 0.0
for d in D:
    STARTS.append(_acc)
    _acc += d
TOTAL = _acc
print("video durs:", [round(x, 3) for x in D], "starts:", [round(x, 3) for x in STARTS],
      "total:", round(TOTAL, 3), flush=True)

SCRIPT = open(f"{BASE}/script-jason.txt").read()
_parts = re.split(r"\[SEG (\d+)\]", SCRIPT)
SEGTEXT = {}
for i in range(1, len(_parts), 2):
    SEGTEXT[int(_parts[i])] = _parts[i + 1].strip()
SENTS, SST = {}, {}
for i in range(5):
    SENTS[i], SST[i] = R.sent_starts(SEGTEXT[i], AUD[i])
    print(f"seg{i} sents:", [(round(s, 2), t[:44]) for s, t in zip(SST[i], SENTS[i])], flush=True)

# ---------------------------------------------------------------- runner (v2 articulated cycle, copied from render_v2.py)
def draw_runner(d, x, ground_y, s, phase, run, col):
    lw = max(4, int(s * 0.05))
    lean = 0.14 if run else 0.04
    swing = 0.95 if run else 0.55
    swing2 = 1.15 if run else 0.75
    arm_swing = 0.85 if run else 0.45
    bob_amp = 0.045 * s if run else 0.02 * s
    bob = -bob_amp * (0.5 + 0.5 * math.cos(2 * phase))
    hip_x, hip_y = x, ground_y - 0.52 * s + bob
    sh_x, sh_y = x + lean * 0.28 * s, ground_y - 0.80 * s + bob
    head_x = x + lean * 0.34 * s
    head_cy = ground_y - 0.94 * s + bob
    r = 0.11 * s
    d.ellipse([head_x - r, head_cy - r, head_x + r, head_cy + r],
              outline=col, width=lw)
    d.line([sh_x, sh_y, hip_x, hip_y], fill=col, width=lw)
    L1, L2 = 0.27 * s, 0.27 * s
    for ph in (phase, phase + math.pi):
        a1 = swing * math.sin(ph)
        a2 = swing2 * math.sin(ph - 0.9)
        kx = hip_x + L1 * math.sin(a1)
        ky = hip_y + L1 * math.cos(a1)
        fx = kx + L2 * math.sin(a2)
        fy = ky + L2 * math.cos(a2)
        d.line([hip_x, hip_y, kx, ky, fx, fy], fill=col, width=lw, joint="curve")
    A1, A2 = 0.20 * s, 0.18 * s
    for ph in (phase + math.pi, phase):
        b1 = -arm_swing * math.sin(ph)
        b2 = -arm_swing * 1.2 * math.sin(ph - 0.7)
        ex = sh_x + A1 * math.sin(b1)
        ey = sh_y + A1 * math.cos(b1)
        hx = ex + A2 * math.sin(b2)
        hy = ey + A2 * math.cos(b2)
        d.line([sh_x, sh_y, ex, ey, hx, hy], fill=col, width=lw, joint="curve")

def chip(d, x0, y0, x1, y1, text, f, fill, outline):
    d.rounded_rectangle([x0, y0, x1, y1], radius=32, outline=outline, width=3)
    d.text(((x0 + x1) // 2, (y0 + y1) // 2 - 4), text, font=f, fill=fill, anchor="mm")

# ---------------------------------------------------------------- S0 hook
def scene0(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[0]
    faded_text_c(frame, 960, 150, "DON'T TOUCH STOCKS YET", font(84, True), TEXT, t, s[0], 0.6)
    faded_text_c(frame, 960, 270, "3 THINGS FIRST", font(84, True), GOLD, t, s[1], 0.6)
    # cyan "you" walks in along the bottom during the hook
    if t > s[1]:
        ph = 2 * math.pi * 2.0 * (t - s[1])
        x = 200 + 90 * (t - s[1])
        if x < 1750:
            draw_runner(d, x, 980, 150, ph, False, CYAN + (255,))
    # three step chips, staggered
    chips = [("1 · EMERGENCY FUND", CYAN), ("2 · DEBT PLAN", RED),
             ("3 · A SIMPLE BUDGET", GREEN)]
    for k, (txt, col) in enumerate(chips):
        st = s[2] + k * 1.2
        if t > st:
            e = ease_out_cubic(clamp01((t - st) / 0.5))
            y = 480 + k * 110
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            chip(od, 560, y, 1360, y + 78, txt, font(40, True), col + (255,), col + (255,))
            frame.paste(ov.convert("RGB"), (0, 0),
                        ov.split()[3].point(lambda v: int(v * e)))
    if t > s[4]:
        faded_text_c(frame, 960, 860, "CALM — NOT PANIC", font(36, True), MUTED, t, s[4], 0.5)
    return frame

# ---------------------------------------------------------------- S1 emergency fund
def _cushion(d, cx, cy, w, h, prog):
    """Soft safety cushion: big rounded pillow, cyan outline, $ emblem."""
    e = ease_out_cubic(clamp01(prog))
    if e <= 0:
        return
    hh = int(h * e)
    if hh < 40:
        return
    d.rounded_rectangle([cx - w // 2, cy - hh // 2, cx + w // 2, cy + hh // 2],
                        radius=60, fill=(15, 27, 45), outline=CYAN, width=6)
    # pillow seam (only once the cushion is tall enough for the inner ellipse)
    if hh > 90:
        d.arc([cx - w // 2 + 20, cy - hh // 2 + 20, cx + w // 2 - 20, cy + hh // 2 - 20],
              start=0, end=360, fill=(56, 189, 248), width=3)
    if e > 0.7:
        d.text((cx, cy - 10), "$", font=font(110, True), fill=GOLD, anchor="mm")

def _tyre(frame, cx, cy, r, prog):
    e = ease_out_cubic(clamp01(prog))
    if e <= 0:
        return
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 44, 52, 255),
               outline=WHITE + (255,), width=5)
    od.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45],
               outline=MUTED + (255,), width=4)
    for k in range(6):
        a = math.pi * k / 3
        od.line([cx + r * 0.45 * math.cos(a), cy + r * 0.45 * math.sin(a),
                 cx + r * 0.9 * math.cos(a), cy + r * 0.9 * math.sin(a)],
                fill=MUTED + (255,), width=4)
    frame.paste(ov.convert("RGB"), (0, 0),
                ov.split()[3].point(lambda v: int(v * e)))

def scene1(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[1]
    d.text((90, 58), "1 · YOUR EMERGENCY FUND — THE SAFETY CUSHION",
           font=font(28, True), fill=MUTED)
    _cushion(d, 960, 560, 620, 380, (t - s[0]) / 0.6)
    # spare tyre gag appears with the joke sentence
    if len(s) > 2:
        _tyre(frame, 420, 830, 95, (t - s[2]) / 0.5)
        if t > s[2] + 0.4:
            faded_text(frame, 560, 800, "THE SPARE TYRE", font(30, True), TEXT, t, s[2] + 0.4, 0.5)
            faded_text(frame, 560, 850, "YOU HOPE YOU NEVER NEED IT", font(26), MUTED, t, s[2] + 0.7, 0.5)
    # savings pot fills as the fund builds
    if len(s) > 14 and t > s[14]:
        p = ease_out_cubic(clamp01((t - s[14]) / 3.0))
        d.rounded_rectangle([1330, 620, 1560, 880], radius=16, outline=GREEN, width=4)
        fh = int(240 * p)
        d.rounded_rectangle([1338, 872 - fh, 1552, 872], radius=10, fill=GREEN)
        d.text((1445, 560), "YOUR FUND", font=font(26, True), fill=MUTED, anchor="ma")
        d.text((1445, 900), "START WITH $500", font=font(30, True), fill=GREEN, anchor="ma")
    # 3-6 months target
    if len(s) > 10 and t > s[10]:
        faded_text_c(frame, 960, 180, "TARGET: 3–6 MONTHS OF ESSENTIAL EXPENSES",
                     font(40, True), AMBER, t, s[10], 0.5)
    if len(s) > 18 and t > s[18]:
        faded_text_c(frame, 960, 980, "NOT EXCITING. THAT'S THE POINT.",
                     font(36, True), TEXT, t, s[18], 0.5)
    return frame

# ---------------------------------------------------------------- S2 debt vs investing
def _hbar(d, x0, y, w_max, frac, fill, label, val_txt, t, start):
    p = ease_out_cubic(clamp01((t - start) / 2.0))
    w = int(w_max * frac * p)
    d.rounded_rectangle([x0, y, x0 + w_max, y + 70], radius=12,
                        outline=MUTED, width=2)
    if w > 0:
        d.rounded_rectangle([x0, y, x0 + w, y + 70], radius=12, fill=fill)
    d.text((x0, y - 44), label, font=font(30, True), fill=TEXT)
    if p > 0.9:
        d.text((x0 + w + 24, y + 4), val_txt, font=font(40, True), fill=fill)

def scene2(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[2]
    d.text((90, 58), "2 · HIGH-INTEREST DEBT VS INVESTING",
           font=font(28, True), fill=MUTED)
    d.rounded_rectangle([90, 130, 600, 168], radius=18, outline=MUTED, width=2)
    d.text((345, 138), "EXAMPLE — TYPICAL CARD RATE ~24%", font=font(20, True),
           fill=MUTED, anchor="ma")
    # debt bar: $1,000 + $240 interest — first bar appears with the section
    # so the frame is never title-only while Jason opens the point
    _hbar(d, 220, 300, 900, 1.0, RED, "CREDIT CARD DEBT — $1,000 YOU OWE",
          "$1,000", t, s[0] + 0.5)
    if len(s) > 4 and t > s[4]:
        _hbar(d, 220, 470, 900, 1.24, RED, "PLUS A YEAR OF INTEREST",
              "$1,240", t, s[4])
        faded_text(frame, 220, 560, "−$240 A YEAR, JUST IN INTEREST",
                   font(36, True), RED, t, s[4] + 0.8, 0.5)
    # investing bar: $1,000 + ~$100 in a good year
    if len(s) > 6 and t > s[6]:
        _hbar(d, 220, 700, 900, 1.10, GREEN, "INVESTING THE SAME $1,000 — A GOOD YEAR",
              "$1,100", t, s[6])
        faded_text(frame, 220, 790, "+$80–$100 — WHILE PAYING $240 THE OTHER WAY",
                   font(36, True), GREEN, t, s[6] + 0.8, 0.5)
    if len(s) > 11 and t > s[11]:
        faded_text_c(frame, 960, 920, "PAY DOWN THE EXPENSIVE DEBT FIRST",
                     font(44, True), TEXT, t, s[11], 0.5)
    if len(s) > 14 and t > s[14]:
        faded_text_c(frame, 960, 1000, "THAT'S A FIRE. PUT IT OUT FIRST.",
                     font(36, True), RED, t, s[14], 0.5)
    return frame

# ---------------------------------------------------------------- S3 budget jars
def _jar(d, cx, top, w, h, fill_frac, col, label, sub, t, start):
    e = ease_out_cubic(clamp01((t - start) / 0.6))
    if e <= 0:
        return
    fh = int((h - 16) * clamp01(fill_frac))
    d.rounded_rectangle([cx - w // 2, top, cx + w // 2, top + h], radius=18,
                        outline=col, width=4)
    if fh > 0:
        d.rounded_rectangle([cx - w // 2 + 8, top + h - 8 - fh,
                             cx + w // 2 - 8, top + h - 8], radius=12, fill=col)
    # rim
    d.line([cx - w // 2, top, cx + w // 2, top], fill=col, width=6)
    d.text((cx, top + h + 18), label, font=font(32, True), fill=TEXT, anchor="ma")
    d.text((cx, top + h + 62), sub, font=font(24), fill=MUTED, anchor="ma")

def scene3(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[3]
    d.text((90, 58), "3 · A BUDGET YOU CAN STICK TO",
           font=font(28, True), fill=MUTED)
    jars = [(420, "ESSENTIALS", "RENT · FOOD · BILLS", CYAN, 0.75),
            (960, "FUN", "YES, FUN GETS A JAR", AMBER, 0.45),
            (1500, "YOUR FUTURE", "FUND TOP-UP · INVESTING", GREEN, 0.6)]
    # jars fade in right at the start of the section so the frame is never
    # empty while Jason introduces the idea; the names land on visible jars
    for k, (cx, label, sub, col, frac) in enumerate(jars):
        st = s[0] + 0.4 + k * 0.8
        _jar(d, cx, 420, 300, 300, frac, col, label, sub, t, st)
    # coins dropping into the future jar
    if len(s) > 7 and t > s[7]:
        for k in range(3):
            ct = (t - s[7] - k * 0.7) % 2.1
            cy = 300 + int(140 * ease_out_cubic(clamp01(ct / 0.9)))
            if ct < 0.9:
                d.ellipse([1480, cy, 1520, cy + 40], fill=GOLD, outline=(0, 0, 0), width=2)
                d.text((1500, cy + 4), "$", font=font(26, True), fill=(0, 0, 0), anchor="ma")
    if len(s) > 9 and t > s[9]:
        faded_text_c(frame, 960, 220, "PAY YOURSELF FIRST",
                     font(44, True), TEXT, t, s[9], 0.5)
    if len(s) > 10 and t > s[10]:
        faded_text_c(frame, 960, 880, "AUTOMATE IT — EVERY PAYDAY",
                     font(40, True), CYAN, t, s[10], 0.5)
    if len(s) > 11 and t > s[11]:
        faded_text_c(frame, 960, 960, "$50 A MONTH, EVERY MONTH, BEATS ONE BIG LUMP SUM",
                     font(32, True), GREEN, t, s[11], 0.5)
    return frame

# ---------------------------------------------------------------- S4 close
def scene4(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[4]
    d.text((90, 58), "YOU'RE READY — WHAT'S NEXT?",
           font=font(28, True), fill=MUTED)
    checks = ["1 · SAFETY CUSHION", "2 · DEBT PLAN", "3 · BUDGET YOU CAN STICK TO"]
    for k, txt in enumerate(checks):
        st = s[2 + k] if len(s) > 2 + k else 4 + k
        if t > st:
            e = ease_out_cubic(clamp01((t - st) / 0.4))
            y = 180 + k * 90
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            od = ImageDraw.Draw(ov)
            od.rounded_rectangle([560, y, 1360, y + 64], radius=32,
                                 outline=GREEN + (255,), width=3)
            od.text((640, y + 12), "✓", font=font(40, True), fill=GREEN + (255,))
            od.text((700, y + 12), txt, font=font(36, True), fill=TEXT + (255,))
            frame.paste(ov.convert("RGB"), (0, 0),
                        ov.split()[3].point(lambda v: int(v * e)))
    # confident walk across the bottom
    if len(s) > 7 and t > s[7]:
        ph = 2 * math.pi * 2.0 * (t - s[7])
        x = 200 + 110 * (t - s[7])
        if x < 1750:
            draw_runner(d, x, 980, 150, ph, False, CYAN + (255,))
    # Part 2 hook card
    if len(s) > 12 and t > s[12]:
        faded_text_c(frame, 960, 560, "NEXT · PART 2", font(36, True), CYAN, t, s[12], 0.5)
        faded_text_c(frame, 960, 620, "IS INVESTING IN STOCKS TOO RISKY?",
                     font(56, True), GOLD, t, s[12] + 0.5, 0.5)
    # disclaimer line at y=940 — clear of the bottom captions (which sit
    # ~1030-1065); the walker has left the frame by the time it appears
    if len(s) > 15 and t > s[15]:
        faded_text_c(frame, 960, 940, "EDUCATION, NOT PERSONAL FINANCIAL ADVICE",
                     font(26, True), MUTED, t, s[15], 0.5)
    return frame

# ---------------------------------------------------------------- main
SCENES = [scene0, scene1, scene2, scene3, scene4]

def main():
    out = f"{OUT}/ep1_v.mp4"
    if os.path.exists(out):
        os.remove(out)
    cmd = ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-vf", "format=yuv420p", "-c:v", "libx264", "-preset", "veryfast",
           "-crf", "20", "-r", str(FPS), out]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    n = int(round(TOTAL * FPS))
    prev_final = None
    t0 = time.time()
    for i in range(n):
        tg = i / FPS
        k = 0
        while k < 4 and tg >= STARTS[k + 1]:
            k += 1
        tl = tg - STARTS[k]
        frame = Image.new("RGB", (W, H), BG)
        frame = SCENES[k](frame, tl)
        if k > 0 and tl < 0.5 and prev_final is not None:
            frame = Image.blend(prev_final, frame, ease_out_cubic(tl / 0.5))
        if i + 1 >= n or (k < 4 and (i + 1) / FPS >= STARTS[k + 1]):
            prev_final = frame.copy()
        p.stdin.write(frame.tobytes())
        if (i + 1) % 600 == 0:
            print(f"  frame {i+1}/{n} {time.time()-t0:.1f}s", flush=True)
    p.stdin.close()
    p.wait()
    assert p.returncode == 0, "ffmpeg failed"
    print(f"rendered {n} frames ({TOTAL:.2f}s) in {time.time()-t0:.1f}s -> {out}", flush=True)

if __name__ == "__main__":
    main()
