"""Jason Explains Ep2 — "Is Investing in Stocks Too Risky for Beginners?"
PIL-ONLY (NO stick figure anywhere), following the approved v4 pipeline
(ep1 build-v4/render_v4.py + assemble_v4.py).

Shariq's decision 22 Nov 2026: NO stick figure in ANY scene. Every beat
is camera movement over the object/animation itself (push-ins, tracking
pans, zooms), the way the reference does it.

PIL vs Manim: PIL-ONLY, same call as v4. Every Ep2 object (eggs, basket,
rollercoaster track + cart, clock, tickets, racecourse oval, dials, bars)
is simple geometric flat-vector art that PIL draws cleanly — the PIL
equivalents already exist and are proven. Manim would add a render seam
with no visible gain, and Manim draws THINGS only (never a figure) per
the brief, so there is no Manim shot in this build at all: no Manim
scenes, no figure rig, no figure code of any kind, so no figure can
appear. See STATUS.md for the per-shot Manim-vs-PIL table (PIL for
every shot, with the reason).

THE CHART (reference treatment, copied from
whysector-pilot/ref-recreation/build/render_recreation.py via v4):
full-width glowing AREA chart, gradient fill fading to BG, glowing head
dot, number counting in sync where the script has numbers.

Numbers are the VERIFIED figures from the task (Damodaran / J.P. Morgan
Guide to the Markets / Morningstar-Ibbotson / S&P Dow Jones Indices —
see STATUS.md). No other numbers are invented. Stylised charts are
labelled STYLISED / ILLUSTRATIVE on screen where the shape is not data.

Video: 1920x1080, 30 fps. Audio/captions/loudnorm in assemble_ep2.py.
Total: 327.840 s speech + 4 x 0.25 s beats = 328.84 s (5:28.84).
"""
import math, os, re, subprocess, sys, time
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, "/home/hatch/workspace/youtube-pipeline/whysector-pilot/build")
import render_pilot as R
sys.path.insert(0, "/home/hatch/workspace/youtube-pipeline/jason-explains/ep1-before-investing/build")
import render_ep1 as E

BASE = "/home/hatch/workspace/youtube-pipeline/jason-explains/ep2-too-risky"
BUILD = f"{BASE}/build"
OUT = f"{BUILD}/ep2_v.mp4"
W, H = 1920, 1080
FPS = 30
BG = R.BG
TEXT, MUTED = R.TEXT, R.MUTED
RED, CYAN, WHITE = R.RED, R.CYAN, R.WHITE
AMBER, GOLD, GREEN = R.AMBER, R.GOLD, R.GREEN
BLACK = (0, 0, 0)
font, ease_out_cubic, clamp01 = R.font, R.ease_out_cubic, R.clamp01
faded_text, faded_text_c = R.faded_text, R.faded_text_c
RED_BR = (255, 92, 122)
GREEN_BR = (52, 211, 153)

# measured mp3 durations (s) — ground truth from ffprobe
AUD = [47.184, 98.640, 62.472, 73.296, 46.248]
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


def caption_text(s):
    """Caption-safe sentence: strip the [pause] direction, collapse space."""
    return re.sub(r"\s+", " ", s.replace("[pause]", "")).strip()


def send(j, s, aud):
    """End time of sentence j in segment with starts s and duration aud."""
    return s[j + 1] if j + 1 < len(s) else aud


def font_mono(sz, bold=False):
    p = ("/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold
         else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf")
    return ImageFont.truetype(p, sz)


def smooth(t):
    t = clamp01(t)
    return t * t * (3 - 2 * t)


# ---------------------------------------------------------------- reference chart helpers (copied from render_recreation.py via v4)
def soft_glow(size, cx, cy, rx, ry, col, alpha):
    ov = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=col + (alpha,))
    return ov.filter(ImageFilter.GaussianBlur(min(rx, ry) * 0.55))


def glow_line(frame, pts, width, col, blur=10):
    """Glowing line. Speed: the Gaussian blur runs on a CROP around the
    line (padding 80 px >> 3x the blur radius), not the whole frame —
    a Gaussian blur is local, so the result is visually identical to
    blurring the full-frame overlay, at ~3x less work."""
    if len(pts) < 2:
        return
    pad = 80
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    x0 = max(0, int(min(xs)) - pad)
    y0 = max(0, int(min(ys)) - pad)
    x1 = min(W, int(max(xs)) + pad)
    y1 = min(H, int(max(ys)) + pad)
    cw, ch = x1 - x0, y1 - y0
    ov = Image.new("RGBA", (cw, ch), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    d.line([(x - x0, y - y0) for x, y in pts], fill=col + (255,),
           width=width, joint="curve")
    ov = ov.filter(ImageFilter.GaussianBlur(blur))
    frame.paste(ov.convert("RGB"), (x0, y0), ov.split()[3])
    d2 = ImageDraw.Draw(frame)
    d2.line(pts, fill=col, width=max(3, width // 3), joint="curve")


_grad_cache = {}


def area_chart(frame, pts, base_y, prog, top_col, bot_col, line_col,
               glow=True, step=4, dot=True):
    """Gradient area fill + glowing line, drawn left->right to `prog`.
    Same code as the reference recreation. Returns head point or None."""
    if prog <= 0.001:
        return None
    base_y = int(base_y)
    x0, x1 = pts[0][0], pts[-1][0]
    head_x = x0 + (x1 - x0) * clamp01(prog)
    xs = list(range(int(x0), int(head_x) + 1, step))
    if len(xs) < 2:
        return None

    def interp(x):
        if x <= pts[0][0]:
            return pts[0][1]
        for (ax, ay), (bx, by) in zip(pts, pts[1:]):
            if x <= bx:
                f = (x - ax) / max(1, (bx - ax))
                return ay + (by - ay) * f
        return pts[-1][1]

    line = [(x, interp(x)) for x in xs]
    gh = max(1, base_y - int(min(y for _, y in line)))
    key = (top_col, bot_col, gh)
    grad = _grad_cache.get(key)
    if grad is None:
        grad = Image.new("RGB", (W, gh), (0, 0, 0))
        gd = ImageDraw.Draw(grad)
        for yy in range(gh):
            f = yy / gh
            col = tuple(int(a + (b - a) * f) for a, b in zip(top_col, bot_col))
            gd.line([0, yy, W, yy], fill=col)
        _grad_cache[key] = grad
    mask = Image.new("L", (W, H), 0)
    md = ImageDraw.Draw(mask)
    top_y = int(min(y for _, y in line))
    md.polygon(line + [(head_x, base_y), (x0, base_y)], fill=255)
    frame.paste(grad, (0, top_y), mask.crop((0, top_y, W, top_y + gh)))
    if glow:
        glow_line(frame, line, 12, line_col, blur=9)
    d = ImageDraw.Draw(frame)
    d.line(line, fill=line_col, width=4, joint="curve")
    hx, hy = line[-1]
    if dot:
        outer = tuple(int(c * 0.4) for c in line_col)
        for rr, col in ((22, outer), (13, line_col), (6, (255, 255, 255))):
            d.ellipse([hx - rr, hy - rr, hx + rr, hy + rr], fill=col)
    return (hx, hy)


def glow_text(frame, cx, y, txt, fnt, col, anchor="ma"):
    """Glowing text. Speed: the Gaussian blur runs on a CROP around the
    text (padding 80 px >> 3x the blur radius), not the whole frame —
    visually identical to the full-frame blur (see glow_line)."""
    pad = 80
    probe = ImageDraw.Draw(frame)
    bx0, by0, bx1, by1 = probe.textbbox((cx, y), txt, font=fnt, anchor=anchor)
    x0 = max(0, bx0 - pad)
    y0 = max(0, by0 - pad)
    x1 = min(W, bx1 + pad)
    y1 = min(H, by1 + pad)
    ov = Image.new("RGBA", (x1 - x0, y1 - y0), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    od.text((cx - x0, y - y0), txt, font=fnt, fill=col + (255,), anchor=anchor)
    ov = ov.filter(ImageFilter.GaussianBlur(14))
    frame.paste(ov.convert("RGB"), (x0, y0), ov.split()[3].point(lambda v: int(v * 0.65)))
    d = ImageDraw.Draw(frame)
    d.text((cx, y), txt, font=fnt, fill=col, anchor=anchor)


# ---------------------------------------------------------------- shared helpers
def pop_in(t, start, dur=0.45):
    # Floor 0.05 on the RETURNED value, not just the u<=0 case: for a
    # just-past-start u (e.g. 1e-15 from float accumulation), ease_out_cubic
    # is ~3u, so int(N * e) is still 0 and PIL raises ValueError. The
    # 22 Nov sweep caught exactly this at t=2.8 ("HONESTLY?" pop). A 0.05
    # ease is a ~2px glyph — invisible on the pre-pop frames.
    u = clamp01((t - start) / dur)
    if u <= 0:
        return 0.05
    e = ease_out_cubic(u)
    return max(0.05, e + 0.12 * math.sin(math.pi * u) * (1 - u))


def _ground(d):
    d.line([60, 980, 1860, 980], fill=(30, 45, 68), width=3)


def seg_header(d, txt):
    d.text((90, 58), txt, font=font(28, True), fill=MUTED)


def pill(d, cx, y, txt, col, fnt=None):
    """Small outlined pill label centred at (cx, y)."""
    fnt = fnt or font(26, True)
    tw = d.textlength(txt, font=fnt)
    d.rounded_rectangle([cx - tw / 2 - 18, y - 22, cx + tw / 2 + 18, y + 22],
                        radius=20, outline=col, width=3)
    d.text((cx, y - 2), txt, font=fnt, fill=col, anchor="mm")


def card(d, x0, y0, x1, y1, outline, width=4, fill=None):
    d.rounded_rectangle([x0, y0, x1, y1], radius=18,
                        fill=fill if fill else (15, 27, 45),
                        outline=outline, width=width)


def _octagon(cx, cy, r):
    return [(cx + r * math.cos(math.pi / 8 + k * math.pi / 4),
             cy + r * math.sin(math.pi / 8 + k * math.pi / 4)) for k in range(8)]


def _egg(d, cx, cy, rx=34, ry=44, cracked=False, outline=WHITE, yolk=True):
    """A simple egg: white outline ellipse. Cracked = zigzag + yolk splat."""
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=outline, width=4)
    if cracked:
        d.line([(cx - rx + 6, cy - 6), (cx - 12, cy + 6), (cx + 2, cy - 8),
                (cx + 14, cy + 4), (cx + rx - 6, cy - 6)], fill=RED, width=4)
        if yolk:
            d.ellipse([cx - 26, cy + ry - 6, cx + 26, cy + ry + 34],
                      outline=GOLD, width=4)
            d.ellipse([cx - 12, cy + ry + 4, cx + 12, cy + ry + 24], fill=GOLD)


def _basket(d, cx, cy, w=520, h=200, col=AMBER):
    """Open basket: trapezoid with weave lines clipped to the slanted sides."""
    d.polygon([(cx - w // 2, cy - h // 2), (cx + w // 2, cy - h // 2),
               (cx + w // 2 - 40, cy + h // 2), (cx - w // 2 + 40, cy + h // 2)],
              outline=col, width=5)
    for k in range(1, 4):
        yy = cy - h // 2 + k * h // 4
        # trapezoid narrows 40 px over the full height: half-width at yy
        frac = (yy - (cy - h // 2)) / h
        hw = w // 2 - int(40 * frac) - 14
        d.line([cx - hw, yy, cx + hw, yy], fill=col, width=3)


def _clock(d, cx, cy, r, t, speed=1.0, col=CYAN):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=6)
    ha = -math.pi / 2 + t * 0.8 * speed
    ma = -math.pi / 2 + t * 3.0 * speed
    d.line([cx, cy, cx + int(r * 0.5 * math.cos(ha)), cy + int(r * 0.5 * math.sin(ha))],
           fill=col, width=8)
    d.line([cx, cy, cx + int(r * 0.8 * math.cos(ma)), cy + int(r * 0.8 * math.sin(ma))],
           fill=col, width=5)


def _ticket(d, cx, cy, w, h, label, col, sub=None):
    card(d, cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2, col)
    d.line([cx - w // 2 + 16, cy + h // 2 - 46, cx + w // 2 - 16, cy + h // 2 - 46],
           fill=MUTED, width=3)
    d.text((cx, cy - 14), label, font=font(34, True), fill=col, anchor="mm")
    if sub:
        d.text((cx, cy + h // 2 - 24), sub, font=font(24, True), fill=MUTED, anchor="mm")


def stamp_x(d, cx, cy, r, col=RED, w=12):
    d.line([cx - r, cy - r, cx + r, cy + r], fill=col, width=w)
    d.line([cx + r, cy - r, cx - r, cy + r], fill=col, width=w)


def rot_sprite(w, h, draw_fn, angle_deg):
    """Draw on transparent RGBA, rotate, return image + anchor offset."""
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_fn(d, w, h)
    return ov.rotate(angle_deg, resample=Image.BICUBIC, expand=False)


def paste_sprite(frame, spr, cx, cy):
    frame.paste(spr.convert("RGB"), (int(cx - spr.width // 2), int(cy - spr.height // 2)),
                spr.split()[3])


# full-width chart point sets (reference treatment: span 80..1840)
GREEN_PTS = [(80, 620), (300, 580), (520, 600), (760, 520), (1000, 550),
             (1240, 470), (1480, 490), (1700, 420), (1840, 390)]
RED_PTS = [(80, 380), (300, 420), (520, 400), (760, 470), (1000, 450),
           (1240, 540), (1480, 520), (1700, 620), (1840, 660)]
# 2008: peak -> -57% trough -> slow climb back to peak (~5.5y). Stylised.
CRASH08_PTS = [(120, 300), (300, 380), (480, 560), (660, 640), (840, 600),
               (1020, 540), (1200, 470), (1380, 400), (1560, 340), (1740, 300)]
# 2020: fast -34% dip, fast V back to new high (~5 months). Stylised.
CRASH20_PTS = [(120, 320), (300, 360), (480, 620), (660, 640), (840, 480),
               (1020, 360), (1200, 300), (1380, 280), (1560, 270), (1740, 260)]
# long-run rising line for the +10% average beat (stylised, 1928->today)
LONG_PTS = [(80, 700), (300, 660), (520, 680), (760, 600), (1000, 620),
            (1240, 520), (1480, 540), (1700, 440), (1840, 380)]

# ---------------------------------------------------------------- SEG 0 hook (local 0:00-47.18)
def scene_hook(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[0]
    seg_header(d, "WHY IT FEELS SO SCARY")
    # 1: "So, you're thinking about investing in stocks — and honestly?"
    if t < s[1]:
        faded_text_c(frame, 960, 200, "THINKING ABOUT INVESTING?", font(56, True), TEXT, t, s[0], 0.5)
        # flashing red headline cards stack in
        heads = [("MARKET CRASHES", 0.0), ("STOCKS PLUNGE", 0.9), ("SAVINGS WIPED OUT", 1.8)]
        for k, (txt, st) in enumerate(heads):
            if t > s[0] + st:
                e = pop_in(t, s[0] + st, 0.4)
                y = 360 + k * 130
                blink = 1.0 if int((t - s[0]) * 2) % 2 == 0 else 0.75
                col = (int(RED[0] * blink), int(RED[1] * blink), int(RED[2] * blink))
                card(d, 560, y, 1360, y + 90, col, width=4)
                if e > 0.7:
                    d.text((960, y + 42), txt, font=font(40, True), fill=col, anchor="mm")
        if t > s[0] + 2.8:
            e = pop_in(t, s[0] + 2.8, 0.4)
            d.text((960, 820), "HONESTLY?", font=font(int(64 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 2: "It feels scary." — big pulsing SCARY
    if t < s[2]:
        pulse = 1 + 0.04 * math.sin((t - s[1]) * 6)
        d.text((960, 420), "IT FEELS", font=font(72, True), fill=TEXT, anchor="ma")
        d.text((960, 540), "SCARY.", font=font(int(150 * pulse), True), fill=RED, anchor="ma")
        # red edge flash
        a = int(50 * (1 - (t - s[1]) / (s[2] - s[1])))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle([0, 0, W, 26], fill=(242, 54, 69, a))
        od.rectangle([0, H - 26, W, H], fill=(242, 54, 69, a))
        frame.paste(ov.convert("RGB"), (0, 0), ov.split()[3])
        return frame
    # 3: "Every headline is red." — three red headline bars
    if t < s[3]:
        faded_text_c(frame, 960, 200, "EVERY HEADLINE IS RED", font(56, True), RED, t, s[2], 0.5)
        for k in range(3):
            st = s[2] + k * 0.4
            if t > st:
                e = pop_in(t, st, 0.35)
                y = 380 + k * 130
                d.rounded_rectangle([400, y, 1520, y + 80], radius=12, fill=(60, 10, 18),
                                    outline=RED, width=4)
                d.line([460, y + 28, 460 + int(900 * e), y + 28], fill=RED, width=10)
                d.line([460, y + 52, 460 + int(620 * e), y + 52], fill=(150, 40, 55), width=8)
        return frame
    # 4: "Somebody on the internet just lost half their savings on one stock."
    if t < s[4]:
        lt = t - s[3]
        faded_text_c(frame, 960, 200, "SOMEBODY ONLINE JUST LOST HALF", font(48, True), TEXT, t, s[3], 0.5)
        # phone card with the post
        e = pop_in(t, s[3] + 0.4, 0.45)
        if e > 0:
            card(d, 660, 340, 1260, 620, WHITE, width=4)
            d.text((960, 400), "@somebody_online", font=font(30, True), fill=MUTED, anchor="ma")
            d.text((960, 480), "lost HALF my savings", font=font(40, True), fill=TEXT, anchor="mm")
            d.text((960, 540), "on ONE stock", font=font(40, True), fill=RED, anchor="mm")
        # one stock card falls -50%
        if lt > 1.6:
            drop = ease_out_cubic(clamp01((lt - 1.6) / 1.6))
            cy = 700 + int(180 * drop)
            card(d, 700, cy, 1220, cy + 110, RED, width=5)
            d.text((960, cy + 52), "ONE STOCK  ▼ −50%", font=font(34, True), fill=RED, anchor="mm")
        return frame
    # 5: "And your brain is doing the maths: what if that happens to me?"
    if t < s[5]:
        lt = t - s[4]
        # thought bubble, camera zooms into it (see ZOOM_KEYS)
        e = pop_in(t, s[4], 0.5)
        if e > 0:
            d.ellipse([560, 330, 1360, 640], outline=CYAN, width=5)
            d.ellipse([760, 660, 800, 700], outline=CYAN, width=4)
            d.ellipse([700, 720, 730, 750], outline=CYAN, width=4)
            d.text((960, 430), "WHAT IF THAT", font=font(56, True), fill=TEXT, anchor="ma")
            d.text((960, 510), "HAPPENS TO ME?", font=font(56, True), fill=AMBER, anchor="ma")
        if lt > 2.2:
            faded_text_c(frame, 960, 840, "YOUR BRAIN IS DOING THE MATHS",
                         font(36, True), MUTED, t, s[4] + 2.2, 0.5)
        return frame
    # 6: "Here's the thing nobody tells you: you're not wrong to feel that way."
    if t < s[6]:
        e = pop_in(t, s[5], 0.45)
        if e > 0:
            d.ellipse([830, 380, 1090, 640], outline=GREEN, width=6)
            d.text((960, 505), "✓", font=font(120, True), fill=GREEN, anchor="mm")
        faded_text_c(frame, 960, 720, "YOU'RE NOT WRONG", font(64, True), GREEN, t, s[5] + 0.5, 0.5)
        faded_text_c(frame, 960, 810, "TO FEEL THAT WAY", font(44, True), TEXT, t, s[5] + 1.2, 0.5)
        return frame
    # 7: "Stocks ARE risky." — big red RISKY stamp
    if t < s[7]:
        e = pop_in(t, s[6], 0.3)
        d.text((960, 430), "STOCKS ARE", font=font(72, True), fill=TEXT, anchor="ma")
        if e > 0:
            d.text((960, 560), "RISKY.", font=font(int(170 * e), True), fill=RED, anchor="ma")
        return frame
    # 8: "The question is — risky for who, and risky for how long?"
    if t < s[8]:
        faded_text_c(frame, 960, 200, "THE QUESTION IS…", font(52, True), TEXT, t, s[7], 0.5)
        if t > s[7] + 0.7:
            e = pop_in(t, s[7] + 0.7, 0.4)
            card(d, 360, 360, 900, 540, CYAN, width=5)
            d.text((630, 445), "RISKY", font=font(36, True), fill=CYAN, anchor="mm")
            d.text((630, 495), "FOR WHO?", font=font(44, True), fill=TEXT, anchor="mm")
        if t > s[7] + 2.0:
            e = pop_in(t, s[7] + 2.0, 0.4)
            card(d, 1020, 360, 1560, 540, GOLD, width=5)
            d.text((1290, 445), "RISKY FOR", font=font(36, True), fill=GOLD, anchor="mm")
            d.text((1290, 495), "HOW LONG?", font=font(44, True), fill=TEXT, anchor="mm")
        return frame
    # 9: "Because the answer changes completely depending on those two things."
    if t < s[9]:
        lt = t - s[8]
        # the two cards swap emphasis: WHO glows, then HOW LONG glows
        who_hot = (int(lt * 1.2) % 2 == 0)
        for (x0, x1, col, hot, label) in ((360, 900, CYAN, who_hot, "WHO?"),
                                          (1020, 1560, GOLD, not who_hot, "HOW LONG?")):
            wdt = 6 if hot else 3
            card(d, x0, 360, x1, 540, col, width=wdt)
            d.text(((x0 + x1) // 2, 445), label, font=font(48, True), fill=col, anchor="mm")
        if lt > 1.5:
            e = pop_in(t, s[8] + 1.5, 0.4)
            d.text((960, 640), "THE ANSWER CHANGES", font=font(int(56 * e), True), fill=TEXT, anchor="ma")
            d.text((960, 730), "COMPLETELY", font=font(int(56 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 10: "And by the end of this video, you'll know exactly where you stand."
    if t < s[10]:
        lt = t - s[9]
        _ground(d)
        prog = clamp01(lt / 3.0)
        for i, px in enumerate(range(120, 1700, 46)):
            if i / 35.0 <= prog:
                d.ellipse([px, 972, px + 14, 986], fill=MUTED)
        if lt > 2.2:
            e = pop_in(t, s[9] + 2.2, 0.45)
            d.line([1560, 560, 1560, 980], fill=GREEN, width=8)
            d.polygon([(1560, 560), (1560 + int(150 * e), 600), (1560, 640)], fill=GREEN)
            d.rounded_rectangle([980, 620, 1460, 720], radius=24, outline=GREEN, width=4)
            d.text((1220, 666), "YOU'LL KNOW WHERE", font=font(30, True), fill=GREEN, anchor="mm")
        faded_text_c(frame, 960, 300, "BY THE END OF THIS VIDEO…", font(52, True), TEXT, t, s[9], 0.5)
        if lt > 3.2:
            d.text((960, 830), "YOU STAND", font=font(44, True), fill=GREEN, anchor="ma")
        return frame
    # 11: "Oh — and if you missed part one, go watch it first."
    if t < s[11]:
        e = pop_in(t, s[10], 0.45)
        if e > 0:
            card(d, 460, 380, 1460, 640, CYAN, width=5)
            d.text((960, 440), "MISSED PART ONE?", font=font(52, True), fill=CYAN, anchor="ma")
            d.text((960, 540), "GO WATCH IT FIRST", font=font(44, True), fill=TEXT, anchor="ma")
        faded_text_c(frame, 960, 760, "PART 1 OF 4", font(40, True), GOLD, t, s[10] + 1.0, 0.5)
        return frame
    # 12: "We covered the three things to do before you touch a single stock."
    if t < s[12]:
        faded_text_c(frame, 960, 200, "PART 1 COVERED THE THREE THINGS", font(48, True), TEXT, t, s[11], 0.5)
        chips = [("EMERGENCY FUND", CYAN, 560), ("DEBT PLAN", RED, 960),
                 ("SIMPLE BUDGET", GREEN, 1360)]
        for k, (txt, col, cx) in enumerate(chips):
            st = s[11] + k * 0.7
            if t > st:
                e = pop_in(t, st, 0.45)
                w = int(170 * e)
                d.rounded_rectangle([cx - w, 640, cx + w, 740], radius=28,
                                    outline=col, width=4)
                if e > 0.7:
                    d.text((cx, 686), txt, font=font(30, True), fill=col, anchor="mm")
                d.text((cx, 560), str(k + 1), font=font(int(72 * e), True), fill=col, anchor="ma")
        return frame
    # 13: "This is part two."
    e = pop_in(t, s[12], 0.4)
    d.text((960, 380), "THIS IS", font=font(64, True), fill=TEXT, anchor="ma")
    if e > 0:
        d.text((960, 500), "PART 2 OF 4", font=font(int(120 * e), True), fill=GOLD, anchor="ma")
        d.text((960, 660), "TOO RISKY?", font=font(int(72 * e), True), fill=RED, anchor="ma")
    return frame


# ---------------------------------------------------------------- SEG 1 history (local 0:00-98.64)
def scene_hist(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[1]
    seg_header(d, "SHORT-TERM RISK vs LONG-TERM HISTORY")
    # 1: "Let's start with the scary part, because it's real."
    if t < s[1]:
        e = pop_in(t, s[0], 0.45)
        if e > 0:
            card(d, 480, 380, 1440, 620, RED, width=5)
            d.text((960, 460), "THE SCARY PART", font=font(56, True), fill=RED, anchor="ma")
            d.text((960, 540), "IS REAL", font=font(56, True), fill=TEXT, anchor="ma")
        return frame
    # 2: "In a single year, the stock market can be brutal."
    if t < s[2]:
        faded_text_c(frame, 960, 200, "IN A SINGLE YEAR, IT CAN BE BRUTAL", font(48, True), TEXT, t, s[1], 0.5)
        # red year bars start dropping in
        for k in range(3):
            st = s[1] + 0.6 + k * 0.8
            if t > st:
                e = ease_out_cubic(clamp01((t - st) / 0.8))
                x0 = 600 + k * 260
                hgt = int(260 * e)
                d.rectangle([x0, 800 - hgt, x0 + 140, 800], fill=(120, 20, 30), outline=RED, width=3)
        _ground(d)
        return frame
    # 3: "The worst year on record, 1931, the market fell almost 44%."
    if t < s[3]:
        lt = t - s[2]
        d.text((960, 200), "WORST YEAR ON RECORD", font=font(48, True), fill=MUTED, anchor="ma")
        e = ease_out_cubic(clamp01(lt / 1.6))
        hgt = int(430 * e)
        d.rectangle([720, 800 - hgt, 1200, 800], fill=(120, 20, 30), outline=RED, width=4)
        val = int(44 * e)
        glow_text(frame, 960, 300, f"−{val}%", font(150, True), RED)
        d.text((960, 830), "1931", font=font(56, True), fill=TEXT, anchor="ma")
        _ground(d)
        return frame
    # 4: "In 2008, it fell 37%."
    if t < s[4]:
        lt = t - s[3]
        d.text((960, 200), "WORST YEAR ON RECORD", font=font(48, True), fill=MUTED, anchor="ma")
        d.rectangle([560, 800 - 430, 880, 800], fill=(120, 20, 30), outline=RED, width=4)
        d.text((720, 830), "1931  −44%", font=font(36, True), fill=RED, anchor="ma")
        e = ease_out_cubic(clamp01(lt / 1.0))
        hgt = int(360 * e)
        d.rectangle([1040, 800 - hgt, 1360, 800], fill=(120, 20, 30), outline=RED, width=4)
        val = int(37 * e)
        glow_text(frame, 1200, 300, f"−{val}%", font(130, True), RED)
        d.text((1200, 830), "2008", font=font(56, True), fill=TEXT, anchor="ma")
        _ground(d)
        return frame
    # 5: "And even in a totally normal year, the market drops about 14% at
    # some point — on average, every single year."
    if t < s[5]:
        lt = t - s[4]
        d.text((960, 170), "EVEN A TOTALLY NORMAL YEAR", font=font(48, True), fill=TEXT, anchor="ma")
        # line dips -14% then recovers to flat
        dip_pts = [(120, 420), (400, 430), (700, 640), (1000, 660), (1300, 500),
                   (1600, 430), (1840, 420)]
        p = smooth(clamp01(lt / 4.0))
        area_chart(frame, dip_pts, 760, p, (70, 12, 24), BG, RED_BR, glow=True)
        if lt > 3.0:
            e = pop_in(t, s[4] + 3.0, 0.4)
            d.text((960, 780), "DROPS ~14% AT SOME POINT", font=font(int(52 * e), True), fill=RED, anchor="ma")
            d.text((960, 860), "ON AVERAGE, EVERY SINGLE YEAR", font=font(36, True), fill=MUTED, anchor="ma")
        return frame
    # 6: "Wait — what?"
    if t < s[6]:
        e = pop_in(t, s[5], 0.3)
        d.text((960, 420), "WAIT —", font=font(96, True), fill=TEXT, anchor="ma")
        if e > 0:
            d.text((960, 540), "WHAT?", font=font(int(150 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 7: "Yes."
    if t < s[7]:
        e = pop_in(t, s[6], 0.25)
        d.text((960, 480), "YES.", font=font(int(170 * e), True), fill=GREEN, anchor="mm")
        return frame
    # 8: "Since 1980, the market has fallen 14% inside the year, on average
    # — and still ended the year higher in 35 out of 46 years."
    if t < s[8]:
        lt = t - s[7]
        d.text((960, 170), "SINCE 1980 — YEAR-END RESULTS", font=font(44, True), fill=TEXT, anchor="ma")
        d.text((960, 230), "46 YEARS · EACH SQUARE = ONE YEAR", font=font(30, True), fill=MUTED, anchor="ma")
        # 46 squares, 35 green up / 11 red down — a COUNT visual, not a
        # time series (no invented year-by-year sequence)
        n_show = int(clamp01(lt / 6.0) * 46)
        ups = 0
        for k in range(n_show):
            row, col = divmod(k, 23)
            x0 = 120 + col * 74
            y0 = 330 + row * 120
            up = k < 35
            ups += 1 if up else 0
            colr = GREEN if up else RED
            d.rounded_rectangle([x0, y0, x0 + 58, y0 + 88], radius=10,
                                fill=colr if up else (120, 20, 30), outline=colr, width=3)
            d.text((x0 + 29, y0 + 42), "▲" if up else "▼", font=font(28, True),
                   fill=BLACK if up else WHITE, anchor="mm")
        if lt > 6.0:
            e = pop_in(t, s[7] + 6.0, 0.4)
            glow_text(frame, 960, 640, "35 OF 46 YEARS UP", font(int(84 * e), True), GREEN)
            d.text((960, 800), "DESPITE THAT ~14% DIP INSIDE THE YEAR",
                   font=font(36, True), fill=MUTED, anchor="ma")
        return frame
    # 9: "That's the first surprise: the drops are normal."
    if t < s[9]:
        e = pop_in(t, s[8], 0.4)
        card(d, 460, 380, 1460, 640, AMBER, width=5)
        d.text((960, 440), "SURPRISE #1", font=font(52, True), fill=AMBER, anchor="ma")
        d.text((960, 540), "THE DROPS ARE NORMAL", font=font(44, True), fill=TEXT, anchor="ma")
        return frame
    # 10: "They're the price of admission, not a sign that something's broken."
    if t < s[10]:
        lt = t - s[9]
        # ticket stub
        e = pop_in(t, s[9], 0.45)
        if e > 0:
            _ticket(d, 960, 480, 700, 260, "PRICE OF ADMISSION", GOLD,
                    sub="ONE TICKET · EVERY YEAR")
        if lt > 2.0:
            e2 = pop_in(t, s[9] + 2.0, 0.4)
            d.ellipse([830, 700, 1090, 880], outline=GREEN, width=5)
            d.text((960, 786), "✓", font=font(90, True), fill=GREEN, anchor="mm")
            d.text((960, 930), "NOT A SIGN SOMETHING'S BROKEN", font=font(36, True), fill=GREEN, anchor="ma")
        return frame
    # 11: "Now here's the second surprise."
    if t < s[11]:
        e = pop_in(t, s[10], 0.4)
        card(d, 560, 400, 1360, 620, AMBER, width=5)
        d.text((960, 470), "SURPRISE #2", font=font(60, True), fill=AMBER, anchor="ma")
        d.text((960, 550), "NOW HERE'S THE…", font=font(36, True), fill=TEXT, anchor="ma")
        return frame
    # 12: "Stretch it out, and the picture flips."
    if t < s[12]:
        lt = t - s[11]
        # red short chart on the left flips to a green long chart
        flip = smooth(clamp01(lt / 2.0))
        if flip < 0.5:
            p = smooth(clamp01(lt / 1.2))
            area_chart(frame, RED_PTS, 760, p, (70, 12, 24), BG, RED_BR, glow=True)
            d.text((960, 200), "SHORT TERM", font=font(48, True), fill=RED, anchor="ma")
        else:
            p = smooth(clamp01((lt - 1.2) / 1.2))
            area_chart(frame, LONG_PTS, 760, p, (16, 70, 48), BG, GREEN_BR, glow=True)
            d.text((960, 200), "LONG TERM", font=font(48, True), fill=GREEN, anchor="ma")
        if lt > 2.2:
            d.text((960, 830), "STRETCH IT OUT — THE PICTURE FLIPS",
                   font=font(44, True), fill=TEXT, anchor="ma")
        return frame
    # 13: "Since 1928 — that's almost a hundred years — the stock market has
    # averaged about 10% a year, with dividends reinvested."
    if t < s[13]:
        lt = t - s[12]
        d.text((960, 170), "SINCE 1928 — ALMOST 100 YEARS", font=font(44, True), fill=TEXT, anchor="ma")
        d.text((960, 225), "STYLISED TREND · WITH DIVIDENDS REINVESTED", font=font(26, True), fill=MUTED, anchor="ma")
        p = smooth(clamp01(lt / 4.5))
        area_chart(frame, LONG_PTS, 780, p, (16, 70, 48), BG, GREEN_BR, glow=True)
        if lt > 2.0:
            val = 10 * ease_out_cubic(clamp01((lt - 2.0) / 3.0))
            glow_text(frame, 960, 300, f"+{val:.0f}% A YEAR (AVG)", font(110, True), GREEN)
        return frame
    # 14: "Through wars, recessions, crashes, pandemics — all of it — about
    # 10% a year."
    if t < s[14]:
        lt = t - s[13]
        d.text((960, 170), "THROUGH IT ALL — ABOUT 10% A YEAR", font=font(44, True), fill=TEXT, anchor="ma")
        area_chart(frame, LONG_PTS, 780, 1.0, (16, 70, 48), BG, GREEN_BR, glow=True)
        events = [("WAR", 420), ("RECESSION", 760), ("CRASH", 1100), ("PANDEMIC", 1440)]
        for k, (label, x) in enumerate(events):
            st = 0.5 + k * 1.0
            if lt > st:
                e = pop_in(t, s[13] + st, 0.35)
                pill(d, x, 880, label, AMBER)
                d.line([x, 850, x, 780], fill=AMBER, width=3)
        glow_text(frame, 960, 300, "+10% A YEAR (AVG)", font(100, True), GREEN)
        return frame
    # 15: "But — and this is the important bit — almost no single year
    # actually gives you 10%."
    if t < s[15]:
        lt = t - s[14]
        d.text((960, 170), "BUT ALMOST NO SINGLE YEAR GIVES YOU 10%", font=font(44, True), fill=TEXT, anchor="ma")
        d.text((960, 225), "EACH BAR = ONE YEAR · ILLUSTRATIVE SPREAD, NOT YEAR-BY-YEAR DATA",
               font=font(24, True), fill=MUTED, anchor="ma")
        # dashed +10% average line
        for x in range(120, 1840, 40):
            d.line([x, 470, x + 22, 470], fill=GOLD, width=4)
        d.text((1700, 420), "+10% AVG", font=font(28, True), fill=GOLD, anchor="ma")
        # scattered year bars, some far above, some far below the line
        bars = [(-0.9, 200), (0.75, 320), (-0.55, 440), (0.95, 560), (-0.8, 680),
                (0.5, 800), (-0.65, 920), (0.85, 1040), (-0.95, 1160), (0.6, 1280),
                (-0.7, 1400), (0.9, 1520)]
        for k, (frac, x0) in enumerate(bars):
            st = 0.4 + k * 0.35
            if lt > st:
                e = ease_out_cubic(clamp01((lt - st) / 0.5))
                top = 470 - int(200 * frac * e) if frac > 0 else 470
                bot = 470 if frac > 0 else 470 - int(200 * frac * e)
                colr = GREEN if frac > 0 else RED
                d.rectangle([x0, top, x0 + 70, bot], fill=colr, outline=colr)
        if lt > 5.0:
            d.text((960, 830), "ALMOST NO YEAR LANDS ON THE LINE",
                   font=font(44, True), fill=AMBER, anchor="ma")
        return frame
    # 16: "The best year ever was 1954: up nearly 53%."
    if t < s[16]:
        lt = t - s[15]
        d.text((960, 170), "THE BEST YEAR EVER", font=font(48, True), fill=TEXT, anchor="ma")
        e = ease_out_cubic(clamp01(lt / 1.6))
        hgt = int(480 * e)
        d.rectangle([720, 800 - hgt, 1200, 800], fill=(16, 120, 60), outline=GREEN, width=4)
        val = int(53 * e)
        glow_text(frame, 960, 300, f"+{val}%", font(150, True), GREEN)
        d.text((960, 830), "1954", font=font(56, True), fill=TEXT, anchor="ma")
        _ground(d)
        return frame
    # 17: "The worst was 1931: down 44%."
    if t < s[17]:
        lt = t - s[16]
        d.text((960, 170), "THE WORST WAS 1931", font=font(48, True), fill=TEXT, anchor="ma")
        d.rectangle([560, 800 - 480, 880, 800], fill=(16, 120, 60), outline=GREEN, width=4)
        d.text((720, 830), "1954  +53%", font=font(36, True), fill=GREEN, anchor="ma")
        e = ease_out_cubic(clamp01(lt / 1.0))
        hgt = int(430 * e)
        d.rectangle([1040, 800 - hgt, 1360, 800], fill=(120, 20, 30), outline=RED, width=4)
        val = int(44 * e)
        glow_text(frame, 1200, 300, f"−{val}%", font(130, True), RED)
        d.text((1200, 830), "1931", font=font(56, True), fill=TEXT, anchor="ma")
        _ground(d)
        return frame
    # 18: "Saying stocks return 10% a year is like saying the average
    # rollercoaster is 10% scary." — rollercoaster track + cart, the joke.
    if t < s[18]:
        lt = t - s[17]
        d.text((960, 170), "THE AVERAGE ROLLERCOASTER IS 10% SCARY", font=font(44, True), fill=TEXT, anchor="ma")
        pts, angles = _coaster_path()
        d.line(pts, fill=(120, 130, 145), width=6, joint="curve")
        # loop circle
        d.ellipse([790, 380, 1130, 720], outline=(120, 130, 145), width=6)
        # exit line: out of the loop's right side, down to the right
        d.line([(1130, 550), (1500, 800), (1840, 800)], fill=(120, 130, 145), width=6, joint="curve")
        # cart rides the approach into the loop
        u = clamp01(lt / 4.5)
        idx = int(u * (len(pts) - 1))
        cx, cy = pts[idx]
        ang = angles[idx]
        spr = _cart_sprite(ang)
        paste_sprite(frame, spr, cx, cy - 30)
        if lt > 3.5:
            pill(d, 960, 880, '"10% SCARY?"', AMBER)
        return frame
    # 19: "Technically true — completely useless when you're upside down."
    if t < s[19]:
        lt = t - s[18]
        d.text((960, 170), "TECHNICALLY TRUE —", font=font(48, True), fill=TEXT, anchor="ma")
        pts, angles = _coaster_path()
        d.line(pts, fill=(120, 130, 145), width=6, joint="curve")
        d.ellipse([790, 380, 1130, 720], outline=(120, 130, 145), width=6)
        d.line([(1130, 550), (1500, 800), (1840, 800)], fill=(120, 130, 145), width=6, joint="curve")
        # cart upside down at the top of the loop
        spr = _cart_sprite(180)
        paste_sprite(frame, spr, 960, 380 + 30)
        if lt > 1.2:
            e = pop_in(t, s[18] + 1.2, 0.4)
            d.text((960, 830), "COMPLETELY USELESS UPSIDE DOWN",
                   font=font(int(52 * e), True), fill=RED, anchor="ma")
        return frame
    # 20: "So the average is real, but you never actually experience the average."
    if t < s[20]:
        lt = t - s[19]
        d.text((960, 170), "THE AVERAGE IS REAL —", font=font(48, True), fill=TEXT, anchor="ma")
        for x in range(120, 1840, 40):
            d.line([x, 470, x + 22, 470], fill=GOLD, width=4)
        d.text((1700, 420), "+10% AVG", font=font(28, True), fill=GOLD, anchor="ma")
        bars = [(-0.9, 200), (0.75, 320), (-0.55, 440), (0.95, 560), (-0.8, 680),
                (0.5, 800), (-0.65, 920), (0.85, 1040), (-0.95, 1160), (0.6, 1280),
                (-0.7, 1400), (0.9, 1520)]
        for k, (frac, x0) in enumerate(bars):
            st = 0.3 + k * 0.25
            if lt > st:
                e = ease_out_cubic(clamp01((lt - st) / 0.4))
                top = 470 - int(200 * frac * e) if frac > 0 else 470
                bot = 470 if frac > 0 else 470 - int(200 * frac * e)
                colr = GREEN if frac > 0 else RED
                d.rectangle([x0, top, x0 + 70, bot], fill=colr, outline=colr)
        if lt > 3.5:
            # zoom target: one single bar, circled
            d.ellipse([980, 130, 1150, 300], outline=AMBER, width=5)
            d.text((960, 830), "YOU NEVER EXPERIENCE THE AVERAGE",
                   font=font(44, True), fill=AMBER, anchor="ma")
        return frame
    # 21: "You experience the ride."
    lt = t - s[20]
    d.text((960, 170), "YOU EXPERIENCE", font=font(56, True), fill=TEXT, anchor="ma")
    pts, angles = _coaster_path()
    d.line(pts, fill=(120, 130, 145), width=6, joint="curve")
    d.ellipse([790, 380, 1130, 720], outline=(120, 130, 145), width=6)
    d.line([(1130, 550), (1500, 800), (1840, 800)], fill=(120, 130, 145), width=6, joint="curve")
    u = clamp01(lt / 1.4)
    idx = int(u * (len(pts) - 1))
    cx, cy = pts[idx]
    spr = _cart_sprite(angles[idx])
    paste_sprite(frame, spr, cx, cy - 30)
    e = pop_in(t, s[20] + 0.4, 0.4)
    d.text((960, 830), "THE RIDE.", font=font(int(72 * e), True), fill=RED, anchor="ma")
    return frame


def _coaster_path():
    """Rollercoaster approach path into the loop: points + tangent angles.
    Path runs left->right along the ground, up the lift hill, into the loop."""
    pts = []
    # approach: gentle rise from the left
    for k in range(0, 21):
        x = 80 + k * 30
        y = 880 - int(120 * (k / 20.0))
        pts.append((x, y))
    # lift hill up to the loop entry — ends exactly at the loop's left
    # point (790, 550) so the track reads as one continuous line
    for k in range(1, 21):
        x = 680 + k * 5
        y = 760 - int(210 * (k / 20.0))
        pts.append((x, y))
    angles = []
    for (ax, ay), (bx, by) in zip(pts, pts[1:] + [pts[-1]]):
        angles.append(math.degrees(math.atan2(by - ay, bx - ax)))
    return pts, angles


def _cart_sprite(angle_deg):
    """Small rollercoaster cart (rounded body + 2 wheels), rotated to the
    track tangent. No figure inside — the cart is empty."""
    def draw_cart(d, w, h):
        d.rounded_rectangle([10, 8, w - 10, h - 26], radius=12,
                            outline=RED, width=4)
        d.line([20, h - 26, w - 20, h - 26], fill=RED, width=4)
        for wx in (34, w - 34):
            d.ellipse([wx - 12, h - 26, wx + 12, h - 2], outline=WHITE, width=4)
    ov = Image.new("RGBA", (150, 90), (0, 0, 0, 0))
    dd = ImageDraw.Draw(ov)
    draw_cart(dd, 150, 90)
    return ov.rotate(-angle_deg, resample=Image.BICUBIC, expand=True)

# ---------------------------------------------------------------- SEG 2 basket (local 0:00-62.47)
def scene_basket(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[2]
    seg_header(d, "ONE COMPANY vs HUNDREDS — INDEX FUNDS")
    # 1: "Now, part two of the fear: what if I pick the wrong one?"
    if t < s[1]:
        faded_text_c(frame, 960, 200, "PART TWO OF THE FEAR", font(48, True), RED, t, s[0], 0.5)
        e = pop_in(t, s[0] + 0.8, 0.45)
        if e > 0:
            card(d, 460, 380, 1460, 640, AMBER, width=5)
            d.text((960, 450), "WHAT IF I PICK", font=font(52, True), fill=TEXT, anchor="ma")
            d.text((960, 540), "THE WRONG ONE?", font=font(52, True), fill=AMBER, anchor="ma")
        return frame
    # 2: "Fair question — because if you put all your money in ONE company,
    # and that company goes bust, you can lose everything."
    if t < s[2]:
        lt = t - s[1]
        faded_text_c(frame, 960, 200, "ALL YOUR MONEY IN ONE COMPANY…", font(44, True), TEXT, t, s[1], 0.5)
        # money piles into the one card, then it cracks and falls to zero
        if lt < 4.5:
            e = pop_in(t, s[1] + 0.4, 0.45)
            if e > 0:
                card(d, 660, 380, 1260, 620, WHITE, width=5)
                d.text((960, 440), "ONE COMPANY", font=font(52, True), fill=TEXT, anchor="ma")
                d.text((960, 540), "$ $ $", font=font(56, True), fill=GREEN, anchor="ma")
        else:
            drop = ease_out_cubic(clamp01((lt - 4.5) / 1.5))
            cy = 380 + int(220 * drop)
            spr = rot_sprite(620, 260, lambda dd, w, h: _one_company_card(dd, w, h), 12 * drop)
            paste_sprite(frame, spr, 960, cy + 120)
            d.text((960, 780), "GOES BUST — YOU CAN LOSE EVERYTHING",
                   font=font(40, True), fill=RED, anchor="ma")
        return frame
    # 3: "It has happened."
    if t < s[3]:
        e = pop_in(t, s[2], 0.3)
        d.text((960, 420), "IT HAS", font=font(72, True), fill=TEXT, anchor="ma")
        if e > 0:
            d.text((960, 540), "HAPPENED.", font=font(int(110 * e), True), fill=RED, anchor="ma")
        return frame
    # 4: "Big names, gone."
    if t < s[4]:
        faded_text_c(frame, 960, 200, "BIG NAMES,", font(56, True), TEXT, t, s[3], 0.5)
        for k, name in enumerate(("COMPANY A", "COMPANY B", "COMPANY C")):
            st = s[3] + k * 0.3
            if t > st:
                e = pop_in(t, st, 0.3)
                cx = 560 + k * 400
                a = int(255 * max(0.0, 1 - (t - st) / 0.9))
                card(d, cx - 150, 400, cx + 150, 560, MUTED, width=4)
                d.text((cx, 470), name, font=font(32, True), fill=MUTED, anchor="mm")
                if t > st + 0.4:
                    stamp_x(d, cx, 480, 60)
        if t > s[3] + 0.7:
            d.text((960, 700), "GONE.", font=font(72, True), fill=RED, anchor="ma")
        return frame
    # 5: "That is not a small risk."
    if t < s[5]:
        d.text((960, 420), "THAT IS NOT", font=font(64, True), fill=TEXT, anchor="ma")
        e = pop_in(t, s[4] + 0.5, 0.4)
        d.text((960, 540), "A SMALL RISK.", font=font(int(72 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 6: "That is a huge risk."
    if t < s[6]:
        e = pop_in(t, s[5], 0.3)
        d.text((960, 420), "THAT IS A", font=font(64, True), fill=TEXT, anchor="ma")
        if e > 0:
            d.text((960, 540), "HUGE RISK.", font=font(int(110 * e), True), fill=RED, anchor="ma")
        return frame
    # 7: "But here's the trick — you don't have to buy one company."
    if t < s[7]:
        lt = t - s[6]
        # the one card splits into many small cards
        n = int(clamp01(lt / 2.5) * 12) + 1
        for k in range(n):
            row, col = divmod(k, 6)
            cx = 420 + col * 220
            cy = 420 + row * 150
            e = pop_in(t, s[6] + k * 0.15, 0.3)
            if e > 0:
                w = int(80 * e)
                d.rounded_rectangle([cx - w, cy - 50, cx + w, cy + 50], radius=12,
                                    outline=CYAN, width=3)
        if lt > 2.5:
            d.text((960, 780), "YOU DON'T HAVE TO BUY ONE",
                   font=font(48, True), fill=GREEN, anchor="ma")
        return frame
    # 8: "An index fund buys hundreds of them at once."
    if t < s[8]:
        lt = t - s[7]
        faded_text_c(frame, 960, 200, "AN INDEX FUND BUYS HUNDREDS AT ONCE", font(44, True), TEXT, t, s[7], 0.5)
        _basket(d, 960, 640, 700, 260)
        n = int(clamp01(lt / 2.0) * 40)
        for k in range(n):
            row, col = divmod(k, 10)
            cx = 700 + col * 58
            cy = 520 + row * 46
            d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=CYAN, width=3)
        if lt > 2.2:
            d.text((960, 830), "HUNDREDS OF COMPANIES — IN ONE BASKET",
                   font=font(40, True), fill=CYAN, anchor="ma")
        return frame
    # 9: "The S&P 500 is 500 of the biggest companies in America, all in
    # one basket."
    if t < s[9]:
        lt = t - s[8]
        _basket(d, 960, 640, 700, 260)
        for k in range(40):
            row, col = divmod(k, 10)
            cx = 700 + col * 58
            cy = 520 + row * 46
            d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=CYAN, width=3)
        val = int(500 * ease_out_cubic(clamp01(lt / 2.5)))
        glow_text(frame, 960, 300, f"{val}", font(150, True), CYAN)
        d.text((960, 830), "S&P 500 — 500 OF THE BIGGEST COMPANIES IN AMERICA",
               font=font(36, True), fill=TEXT, anchor="ma")
        return frame
    # 10: "Buy the index, and you own a tiny slice of all 500."
    if t < s[10]:
        lt = t - s[9]
        faded_text_c(frame, 960, 200, "YOU OWN A TINY SLICE OF ALL 500", font(44, True), TEXT, t, s[9], 0.5)
        # basket as a pie of 500 slices: draw a circle split into slices,
        # one slice highlighted gold
        cx, cy, r = 960, 600, 210
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CYAN, width=5)
        for k in range(24):
            a = k * math.pi / 12
            d.line([cx, cy, cx + int(r * math.cos(a)), cy + int(r * math.sin(a))],
                   fill=(30, 60, 90), width=2)
        if lt > 0.8:
            e = pop_in(t, s[9] + 0.8, 0.4)
            d.pieslice([cx - r, cy - r, cx + r, cy + r], start=-90, end=-75,
                       fill=GOLD)
            d.text((cx, cy - r - 60), "YOUR SLICE × 500", font=font(40, True), fill=GOLD, anchor="ma")
        return frame
    # 11: "So if one company goes bust?"
    if t < s[11]:
        cx, cy, r = 960, 600, 210
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=CYAN, width=5)
        for k in range(24):
            a = k * math.pi / 12
            d.line([cx, cy, cx + int(r * math.cos(a)), cy + int(r * math.sin(a))],
                   fill=(30, 60, 90), width=2)
        # one slice turns red and cracks
        lt = t - s[10]
        d.pieslice([cx - r, cy - r, cx + r, cy + r], start=-90, end=-75, fill=RED)
        if lt > 0.5:
            stamp_x(d, cx + 40, cy - 190, 40)
        d.text((960, 880), "SO IF ONE COMPANY GOES BUST?", font=font(48, True), fill=TEXT, anchor="ma")
        return frame
    # 12: "That's one out of 500 — about 0.2% of your money."
    if t < s[12]:
        lt = t - s[11]
        cx, cy, r = 960, 600, 210
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=MUTED, width=4)
        d.pieslice([cx - r, cy - r, cx + r, cy + r], start=-90, end=-75, fill=RED)
        e = pop_in(t, s[11] + 0.5, 0.45)
        if e > 0:
            glow_text(frame, 960, 200, "1 OF 500 = 0.2%", font(int(110 * e), True), GREEN)
        if lt > 2.0:
            d.text((960, 880), "THAT'S ABOUT 0.2% OF YOUR MONEY",
                   font=font(40, True), fill=TEXT, anchor="ma")
            d.text((960, 950), "SIMPLE ARITHMETIC — 1 ÷ 500", font=font(28, True), fill=MUTED, anchor="ma")
        return frame
    # 13: "It stings."
    if t < s[13]:
        e = pop_in(t, s[12], 0.3)
        d.text((960, 480), "IT STINGS.", font=font(int(96 * e), True), fill=AMBER, anchor="mm")
        d.text((960, 620), "OUCH", font=font(48, True), fill=RED, anchor="ma")
        return frame
    # 14: "It doesn't sink you."
    if t < s[14]:
        _basket(d, 960, 600, 700, 260)
        for k in range(40):
            row, col = divmod(k, 10)
            cx = 700 + col * 58
            cy = 480 + row * 46
            d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=CYAN, width=3)
        # one red dot among the blue — the basket stays afloat
        d.ellipse([940, 500, 968, 528], fill=RED)
        d.ellipse([830, 700, 1090, 830], outline=GREEN, width=5)
        d.text((960, 760), "✓", font=font(72, True), fill=GREEN, anchor="mm")
        d.text((960, 900), "IT DOESN'T SINK YOU", font=font(48, True), fill=GREEN, anchor="ma")
        return frame
    # 15: "Think of it like eggs."
    if t < s[15]:
        e = pop_in(t, s[14], 0.45)
        if e > 0:
            _egg(d, 760, 560, 70, 90)
            _basket(d, 1240, 600, 420, 200)
            for k in range(6):
                _egg(d, 1120 + (k % 3) * 120, 520 + (k // 3) * 60, 26, 34)
        d.text((960, 820), "THINK OF IT LIKE EGGS", font=font(52, True), fill=TEXT, anchor="ma")
        return frame
    # 16: "One egg, dropped — breakfast ruined."
    if t < s[16]:
        lt = t - s[15]
        d.text((960, 200), "ONE EGG, DROPPED —", font=font(48, True), fill=TEXT, anchor="ma")
        drop = ease_out_cubic(clamp01(lt / 0.9))
        ey = 420 + int(420 * drop)
        if drop < 1.0:
            _egg(d, 960, ey, 60, 78)
        else:
            _egg(d, 960, 840, 60, 78, cracked=True)
            if lt > 1.2:
                d.text((960, 940), "BREAKFAST RUINED", font=font(48, True), fill=RED, anchor="ma")
        return frame
    # 17: "A basket of 500 eggs, one breaks — you still have breakfast."
    if t < s[17]:
        lt = t - s[16]
        d.text((960, 200), "A BASKET OF 500 EGGS —", font=font(44, True), fill=TEXT, anchor="ma")
        _basket(d, 960, 640, 760, 260)
        for k in range(40):
            row, col = divmod(k, 10)
            cx = 680 + col * 62
            cy = 520 + row * 48
            cracked = (k == 17)
            _egg(d, cx, cy, 20, 26, cracked=cracked,
                 outline=RED if cracked else WHITE, yolk=False)
        if lt > 2.0:
            e = pop_in(t, s[16] + 2.0, 0.4)
            d.text((960, 830), "ONE BREAKS — YOU STILL HAVE BREAKFAST",
                   font=font(int(44 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 18: "Same money."
    if t < s[18]:
        e = pop_in(t, s[17], 0.35)
        # balance scale, higher up; labels under the pans; big text below
        d.line([960, 260, 960, 380], fill=MUTED, width=6)
        d.line([700, 300, 1220, 300], fill=MUTED, width=6)
        d.ellipse([640, 300, 760, 380], outline=CYAN, width=4)
        d.ellipse([1160, 300, 1280, 380], outline=CYAN, width=4)
        d.text((700, 410), "1 EGG", font=font(32, True), fill=CYAN, anchor="ma")
        d.text((1220, 410), "500 EGGS", font=font(32, True), fill=CYAN, anchor="ma")
        d.text((960, 560), "SAME MONEY.", font=font(int(96 * e), True), fill=TEXT, anchor="mm")
        return frame
    # 19: "Completely different risk."
    if t < s[19]:
        e = pop_in(t, s[18], 0.35)
        d.text((960, 480), "COMPLETELY", font=font(int(84 * e), True), fill=TEXT, anchor="mm")
        d.text((960, 600), "DIFFERENT RISK.", font=font(int(84 * e), True), fill=GREEN, anchor="mm")
        return frame
    # 20: "That's the whole idea of an index fund: you're not betting on
    # one horse."
    if t < s[20]:
        lt = t - s[19]
        faded_text_c(frame, 960, 200, "THE WHOLE IDEA OF AN INDEX FUND", font(44, True), TEXT, t, s[19], 0.5)
        e = pop_in(t, s[19] + 0.6, 0.45)
        if e > 0:
            _ticket(d, 960, 520, 640, 300, "ONE HORSE", RED, sub="BETTING SLIP · 1 HORSE")
        if lt > 2.4:
            stamp_x(d, 960, 520, 130)
            d.text((960, 780), "YOU'RE NOT BETTING ON ONE HORSE",
                   font=font(44, True), fill=RED, anchor="ma")
        return frame
    # 21: "You're betting on the whole racecourse."
    if t < s[21]:
        lt = t - s[20]
        faded_text_c(frame, 960, 200, "YOU'RE BETTING ON THE WHOLE RACECOURSE", font(44, True), TEXT, t, s[20], 0.5)
        # oval track with many dots (horses) running around it
        cx, cy, rx, ry = 960, 580, 560, 220
        d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=GREEN, width=6)
        d.ellipse([cx - rx + 60, cy - ry + 60, cx + rx - 60, cy + ry - 60],
                  outline=(30, 60, 90), width=3)
        for k in range(8):
            a = (lt * 0.5 + k * math.pi / 4) % (2 * math.pi)
            hx = cx + int(rx * math.cos(a))
            hy = cy + int(ry * math.sin(a))
            d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=GOLD, outline=BLACK, width=2)
        return frame
    # 22: "And the racecourse has been running for a hundred years."
    lt = t - s[21]
    cx, cy, rx, ry = 960, 580, 560, 220
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], outline=GREEN, width=6)
    d.ellipse([cx - rx + 60, cy - ry + 60, cx + rx - 60, cy + ry - 60],
              outline=(30, 60, 90), width=3)
    for k in range(8):
        a = (lt * 0.5 + k * math.pi / 4) % (2 * math.pi)
        hx = cx + int(rx * math.cos(a))
        hy = cy + int(ry * math.sin(a))
        d.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=GOLD, outline=BLACK, width=2)
    if lt > 0.8:
        e = pop_in(t, s[21] + 0.8, 0.4)
        d.text((960, 200), "RUNNING FOR 100 YEARS", font=font(int(56 * e), True), fill=TEXT, anchor="ma")
        d.text((960, 880), "1928  ————  TODAY", font=font(40, True), fill=MUTED, anchor="ma")
    return frame


def _one_company_card(dd, w, h):
    dd.rounded_rectangle([4, 4, w - 4, h - 4], radius=18,
                         fill=(15, 27, 45), outline=WHITE, width=5)
    dd.text((w // 2, h // 2 - 50), "ONE COMPANY", font=font(52, True), fill=TEXT, anchor="mm")
    dd.text((w // 2, h // 2 + 40), "$ $ $", font=font(56, True), fill=GREEN, anchor="mm")


# ---------------------------------------------------------------- SEG 3 time (local 0:00-73.30)
def scene_time(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[3]
    seg_header(d, "HOW TIME IN THE MARKET CHANGES THE RISK")
    # 1: "And then there's the biggest lever of all: time."
    if t < s[1]:
        lt = t - s[0]
        _clock(d, 960, 520, 190, lt, speed=1.0)
        e = pop_in(t, s[0] + 0.8, 0.45)
        if e > 0:
            d.text((960, 820), "THE BIGGEST LEVER OF ALL: TIME",
                   font=font(int(52 * e), True), fill=TEXT, anchor="ma")
        return frame
    # 2: "Here's the number that changed how I think about risk."
    if t < s[2]:
        e = pop_in(t, s[1], 0.4)
        card(d, 460, 380, 1460, 640, GOLD, width=5)
        d.text((960, 460), "THE NUMBER THAT", font=font(48, True), fill=TEXT, anchor="ma")
        d.text((960, 540), "CHANGED EVERYTHING", font=font(48, True), fill=GOLD, anchor="ma")
        return frame
    # 3: "In any single year, the market goes up about 73% of the time."
    if t < s[3]:
        lt = t - s[2]
        d.text((960, 200), "IN ANY SINGLE YEAR", font=font(48, True), fill=TEXT, anchor="ma")
        # donut: 73% green
        cx, cy, r = 960, 580, 210
        frac = 0.73 * ease_out_cubic(clamp01(lt / 2.5))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 45, 68), width=28)
        if frac > 0:
            d.arc([cx - r, cy - r, cx + r, cy + r], start=-90,
                  end=-90 + 360 * frac, fill=GREEN, width=28)
        val = int(73 * ease_out_cubic(clamp01(lt / 2.5)))
        glow_text(frame, cx, 520, f"{val}%", font(130, True), GREEN)
        d.text((cx, 830), "OF YEARS GO UP", font=font(36, True), fill=TEXT, anchor="ma")
        return frame
    # 4: "Roughly three years out of four, you win."
    if t < s[4]:
        lt = t - s[3]
        d.text((960, 200), "ROUGHLY THREE YEARS OUT OF FOUR", font=font(48, True), fill=TEXT, anchor="ma")
        for k in range(4):
            st = 0.4 + k * 0.5
            if lt > st:
                e = pop_in(t, s[3] + st, 0.35)
                x0 = 420 + k * 280
                win = k < 3
                colr = GREEN if win else RED
                d.rounded_rectangle([x0, 420, x0 + 200, 620], radius=18,
                                    outline=colr, width=4,
                                    fill=colr if win else (120, 20, 30))
                d.text((x0 + 100, 515), "✓" if win else "✕", font=font(72, True),
                       fill=BLACK if win else WHITE, anchor="mm")
                d.text((x0 + 100, 660), f"YEAR {k + 1}", font=font(30, True), fill=MUTED, anchor="ma")
        if lt > 2.2:
            d.text((960, 780), "YOU WIN", font=font(64, True), fill=GREEN, anchor="ma")
        return frame
    # 5: "But stretch your holding period to 20 years — and in almost a
    # hundred years of records, there has never been a single 20-year
    # stretch where the market lost money."
    if t < s[5]:
        lt = t - s[4]
        d.text((960, 200), "STRETCH IT TO 20 YEARS…", font=font(48, True), fill=TEXT, anchor="ma")
        # timeline 1926 -> today with sliding 20-year windows, all green
        d.line([200, 620, 1720, 620], fill=MUTED, width=4)
        d.text((200, 660), "1926", font=font(30, True), fill=MUTED, anchor="ma")
        d.text((1720, 660), "TODAY", font=font(30, True), fill=MUTED, anchor="ma")
        win_x = 200 + int(clamp01(lt / 6.0) * 900)
        # green ticks accumulate along the timeline behind the window
        for tx in range(200, win_x, 120):
            d.ellipse([tx - 10, 610, tx + 10, 630], fill=GREEN)
        d.rounded_rectangle([win_x, 560, win_x + 620, 680], radius=16,
                            outline=GREEN, width=5)
        d.text((win_x + 310, 615), "20 YEARS", font=font(36, True), fill=GREEN, anchor="mm")
        if lt > 5.0:
            e = pop_in(t, s[4] + 5.0, 0.4)
            d.text((960, 800), "NEVER A SINGLE 20-YEAR STRETCH THAT LOST MONEY",
                   font=font(int(44 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 6: "Not one."
    if t < s[6]:
        e = pop_in(t, s[5], 0.25)
        d.text((960, 480), "NOT ONE.", font=font(int(150 * e), True), fill=GREEN, anchor="mm")
        return frame
    # 7: "The worst 20-year stretch still made about 2 to 3% a year."
    if t < s[7]:
        lt = t - s[6]
        d.text((960, 200), "THE WORST 20-YEAR STRETCH", font=font(48, True), fill=TEXT, anchor="ma")
        e = ease_out_cubic(clamp01(lt / 1.5))
        hgt = int(120 * e)
        d.rectangle([720, 800 - hgt, 1200, 800], fill=(16, 120, 60), outline=GREEN, width=4)
        val = 3 * e
        glow_text(frame, 960, 380, f"+{val:.1f}% / YEAR", font(110, True), GREEN)
        d.text((960, 850), "STILL MADE ABOUT 2–3% A YEAR", font=font(40, True), fill=TEXT, anchor="ma")
        _ground(d)
        return frame
    # 8: "The best made almost 18% a year."
    if t < s[8]:
        lt = t - s[7]
        d.text((960, 200), "THE BEST 20-YEAR STRETCH", font=font(48, True), fill=TEXT, anchor="ma")
        d.rectangle([560, 800 - 120, 880, 800], fill=(16, 120, 60), outline=GREEN, width=4)
        d.text((720, 850), "WORST  +2–3%", font=font(32, True), fill=GREEN, anchor="ma")
        e = ease_out_cubic(clamp01(lt / 1.5))
        hgt = int(480 * e)
        d.rectangle([1040, 800 - hgt, 1360, 800], fill=(16, 120, 60), outline=GREEN, width=4)
        val = 18 * e
        glow_text(frame, 1200, 300, f"+{val:.0f}% / YEAR", font(100, True), GREEN)
        d.text((1200, 850), "BEST  ~18%", font=font(32, True), fill=GREEN, anchor="ma")
        _ground(d)
        return frame
    # 9: "Now — that does not mean the wait is comfortable."
    if t < s[9]:
        lt = t - s[8]
        wob = 8 * math.sin((t - s[8]) * 8)
        _clock(d, 960 + int(wob), 520, 170, lt, speed=2.0, col=AMBER)
        e = pop_in(t, s[8] + 0.8, 0.4)
        d.text((960, 800), "THE WAIT IS NOT COMFORTABLE", font=font(int(52 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 10: "After the 2008 crash, the market fell 57% — and it took about
    # five and a half years just to get back to where it started."
    if t < s[10]:
        lt = t - s[9]
        d.text((960, 170), "AFTER THE 2008 CRASH", font=font(48, True), fill=TEXT, anchor="ma")
        d.text((960, 225), "S&P 500 · STYLISED CHART", font=font(26, True), fill=MUTED, anchor="ma")
        # peak -> trough -> back to peak, in sync with the narration:
        # fall first (0-3.5s), then the slow climb (3.5-7.5s)
        p = smooth(clamp01(lt / 7.5))
        area_chart(frame, CRASH08_PTS, 780, p, (70, 12, 24), BG, RED_BR, glow=True)
        if lt > 1.0:
            fall = ease_out_cubic(clamp01((lt - 1.0) / 2.0))
            glow_text(frame, 960, 300, f"−{int(57 * fall)}%", font(120, True), RED)
        d.text((300, 830), "OCT 2007 PEAK", font=font(28, True), fill=MUTED, anchor="ma")
        d.text((960, 830), "MAR 2009  −57%", font=font(28, True), fill=RED, anchor="ma")
        d.text((1620, 830), "MAR 2013", font=font(28, True), fill=MUTED, anchor="ma")
        if lt > 6.5:
            e = pop_in(t, s[9] + 6.5, 0.4)
            d.text((960, 900), "~5.5 YEARS TO GET BACK TO THE PEAK",
                   font=font(int(40 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 11: "After the COVID crash in 2020, it fell 34% in about a month —
    # and it was back at new highs in five months."
    if t < s[11]:
        lt = t - s[10]
        d.text((960, 170), "AFTER THE COVID CRASH IN 2020", font=font(48, True), fill=TEXT, anchor="ma")
        d.text((960, 225), "S&P 500 · STYLISED CHART", font=font(26, True), fill=MUTED, anchor="ma")
        p = smooth(clamp01(lt / 6.0))
        area_chart(frame, CRASH20_PTS, 780, p, (70, 12, 24), BG, RED_BR, glow=True)
        if lt > 1.0:
            fall = ease_out_cubic(clamp01((lt - 1.0) / 2.0))
            glow_text(frame, 960, 300, f"−{int(34 * fall)}%", font(120, True), RED)
        d.text((300, 830), "FEB 2020", font=font(28, True), fill=MUTED, anchor="ma")
        d.text((960, 830), "−34% IN ~A MONTH", font=font(28, True), fill=RED, anchor="ma")
        d.text((1620, 830), "AUG 2020", font=font(28, True), fill=MUTED, anchor="ma")
        if lt > 5.5:
            e = pop_in(t, s[10] + 5.5, 0.4)
            d.text((960, 900), "BACK AT NEW HIGHS IN ~5 MONTHS",
                   font=font(int(40 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 12: "Same market."
    if t < s[12]:
        # both crash charts side by side, mini
        d.text((960, 200), "SAME MARKET.", font=font(64, True), fill=TEXT, anchor="ma")
        d.line([(480, 420), (600, 560), (720, 640), (840, 480), (900, 400)],
               fill=RED, width=5, joint="curve")
        d.text((700, 700), "2008:  −57%  ·  5.5 YEARS", font=font(32, True), fill=RED, anchor="ma")
        d.line([(1080, 420), (1180, 620), (1280, 640), (1380, 460), (1440, 400)],
               fill=RED, width=5, joint="curve")
        d.text((1260, 700), "2020:  −34%  ·  5 MONTHS", font=font(32, True), fill=RED, anchor="ma")
        return frame
    # 13: "One wait was five months."
    if t < s[13]:
        e = pop_in(t, s[12], 0.4)
        card(d, 660, 380, 1260, 620, GREEN, width=5)
        d.text((960, 460), "ONE WAIT WAS", font=font(44, True), fill=TEXT, anchor="ma")
        d.text((960, 550), "FIVE MONTHS", font=font(int(56 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 14: "The other was five years."
    if t < s[14]:
        e = pop_in(t, s[13], 0.4)
        card(d, 660, 380, 1260, 620, AMBER, width=5)
        d.text((960, 460), "THE OTHER WAS", font=font(44, True), fill=TEXT, anchor="ma")
        d.text((960, 550), "FIVE YEARS", font=font(int(56 * e), True), fill=AMBER, anchor="ma")
        return frame
    # 15: "You can't know which one you're getting."
    if t < s[15]:
        e = pop_in(t, s[14], 0.4)
        d.text((960, 420), "YOU CAN'T KNOW", font=font(64, True), fill=TEXT, anchor="ma")
        d.text((960, 540), "WHICH ONE YOU'RE GETTING.", font=font(int(56 * e), True), fill=AMBER, anchor="ma")
        d.text((960, 680), "?", font=font(120, True), fill=AMBER, anchor="ma")
        return frame
    # 16: "That's the real risk."
    if t < s[16]:
        e = pop_in(t, s[15], 0.35)
        card(d, 560, 400, 1360, 620, RED, width=5)
        d.text((960, 470), "THAT'S THE", font=font(52, True), fill=TEXT, anchor="ma")
        d.text((960, 550), "REAL RISK.", font=font(int(64 * e), True), fill=RED, anchor="ma")
        return frame
    # 17: "Not that the market never recovers — it always has, so far."
    if t < s[17]:
        lt = t - s[16]
        d.text((960, 200), "NOT THAT THE MARKET NEVER RECOVERS", font=font(44, True), fill=TEXT, anchor="ma")
        p = smooth(clamp01(lt / 2.5))
        area_chart(frame, LONG_PTS, 780, p, (16, 70, 48), BG, GREEN_BR, glow=True)
        if lt > 2.0:
            e = pop_in(t, s[16] + 2.0, 0.4)
            d.text((960, 830), "IT ALWAYS HAS — SO FAR", font=font(int(48 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 18: "The risk is that you need the money before it does."
    if t < s[18]:
        lt = t - s[17]
        # calendar card vs the recovery line
        d.text((960, 200), "THE RISK IS…", font=font(48, True), fill=TEXT, anchor="ma")
        p = smooth(clamp01(lt / 2.5))
        area_chart(frame, LONG_PTS, 780, p, (16, 70, 48), BG, GREEN_BR, glow=True)
        if lt > 1.5:
            e = pop_in(t, s[17] + 1.5, 0.4)
            card(d, 700, 300, 1220, 520, RED, width=5)
            d.text((960, 370), "YOU NEED", font=font(40, True), fill=TEXT, anchor="ma")
            d.text((960, 440), "THE MONEY", font=font(int(52 * e), True), fill=RED, anchor="ma")
            d.text((960, 490), "BEFORE IT DOES", font=font(30, True), fill=MUTED, anchor="ma")
        return frame
    # 19: "So the question isn't really 'are stocks risky?' The question is
    # 'when do I need this money?'"
    lt = t - s[18]
    e = pop_in(t, s[18], 0.45)
    if e > 0:
        card(d, 460, 360, 1460, 660, GOLD, width=5)
        d.text((960, 430), "WHEN DO I NEED", font=font(56, True), fill=TEXT, anchor="ma")
        d.text((960, 520), "THIS MONEY?", font=font(int(64 * e), True), fill=GOLD, anchor="ma")
    if lt > 2.5:
        d.text((960, 760), "THAT'S THE REAL QUESTION", font=font(40, True), fill=MUTED, anchor="ma")
    return frame

# ---------------------------------------------------------------- SEG 4 close (local 0:00-46.25)
def scene_close(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[4]
    seg_header(d, "SO — IS IT TOO RISKY FOR YOU?")
    # 1: "So — is investing in stocks too risky for beginners?"
    if t < s[1]:
        e = pop_in(t, s[0], 0.45)
        if e > 0:
            card(d, 460, 360, 1460, 660, RED, width=5)
            d.text((960, 430), "IS INVESTING IN STOCKS", font=font(48, True), fill=TEXT, anchor="ma")
            d.text((960, 520), "TOO RISKY?", font=font(int(72 * e), True), fill=RED, anchor="ma")
            d.text((960, 610), "FOR BEGINNERS", font=font(36, True), fill=MUTED, anchor="ma")
        return frame
    # 2: "Here's my honest answer."
    if t < s[2]:
        e = pop_in(t, s[1], 0.4)
        d.text((960, 420), "HERE'S MY", font=font(64, True), fill=TEXT, anchor="ma")
        d.text((960, 540), "HONEST ANSWER.", font=font(int(72 * e), True), fill=GOLD, anchor="ma")
        return frame
    # 3: "If you need this money next year — for rent, for a deposit, for
    # an emergency — yes."
    if t < s[3]:
        lt = t - s[2]
        faded_text_c(frame, 960, 200, "IF YOU NEED THIS MONEY NEXT YEAR…", font(44, True), TEXT, t, s[2], 0.5)
        chips = [("RENT", 560), ("DEPOSIT", 960), ("EMERGENCY", 1360)]
        for k, (txt, cx) in enumerate(chips):
            st = s[2] + 0.6 + k * 0.7
            if t > st:
                e = pop_in(t, st, 0.4)
                w = int(150 * e)
                d.rounded_rectangle([cx - w, 400, cx + w, 500], radius=24,
                                    outline=RED, width=4)
                if e > 0.7:
                    d.text((cx, 446), txt, font=font(32, True), fill=RED, anchor="mm")
        if lt > 3.5:
            e = pop_in(t, s[2] + 3.5, 0.4)
            d.text((960, 640), "YES.", font=font(int(130 * e), True), fill=RED, anchor="ma")
        return frame
    # 4: "Too risky."
    if t < s[4]:
        e = pop_in(t, s[3], 0.3)
        d.text((960, 480), "TOO RISKY.", font=font(int(130 * e), True), fill=RED, anchor="mm")
        return frame
    # 5: "Don't put it in stocks."
    if t < s[5]:
        lt = t - s[4]
        e = pop_in(t, s[4], 0.4)
        if e > 0:
            card(d, 460, 380, 1460, 620, RED, width=5)
            d.text((960, 460), "DON'T PUT IT", font=font(52, True), fill=TEXT, anchor="ma")
            d.text((960, 540), "IN STOCKS.", font=font(52, True), fill=RED, anchor="ma")
        if lt > 0.8:
            stamp_x(d, 960, 760, 60)
        return frame
    # 6: "But if this is money you can leave alone for ten, twenty years —
    # and you own the whole basket, not one company — then history says
    # something very different."
    if t < s[6]:
        lt = t - s[5]
        faded_text_c(frame, 960, 200, "BUT IF YOU CAN LEAVE IT ALONE 10–20 YEARS…", font(40, True), TEXT, t, s[5], 0.5)
        # timeline 10 -> 20 years + the basket
        d.line([300, 560, 1620, 560], fill=MUTED, width=4)
        for k, (x, label) in enumerate(((300, "NOW"), (810, "10 YEARS"), (1620, "20 YEARS"))):
            d.ellipse([x - 14, 546, x + 14, 574], fill=GREEN if k else MUTED)
            d.text((x, 600), label, font=font(30, True), fill=TEXT, anchor="ma")
        _basket(d, 960, 780, 420, 140)
        for k in range(12):
            row, col = divmod(k, 6)
            d.ellipse([800 + col * 64 - 12, 730 + row * 40 - 12,
                       800 + col * 64 + 12, 730 + row * 40 + 12], outline=CYAN, width=3)
        if lt > 5.0:
            e = pop_in(t, s[5] + 5.0, 0.4)
            d.text((960, 920), "HISTORY SAYS SOMETHING VERY DIFFERENT",
                   font=font(int(40 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 7: "The risk doesn't disappear."
    if t < s[7]:
        lt = t - s[6]
        d.text((960, 200), "THE RISK DOESN'T DISAPPEAR.", font=font(48, True), fill=TEXT, anchor="ma")
        # risk bar stays visible
        d.rounded_rectangle([360, 480, 1560, 560], radius=20, outline=RED, width=4)
        d.rounded_rectangle([366, 486, 366 + int(1188 * ease_out_cubic(clamp01(lt / 0.8))), 554],
                            radius=14, fill=RED)
        d.text((960, 620), "STILL THERE", font=font(36, True), fill=RED, anchor="ma")
        return frame
    # 8: "It shrinks."
    if t < s[8]:
        lt = t - s[7]
        d.text((960, 200), "IT SHRINKS.", font=font(56, True), fill=GREEN, anchor="ma")
        # the same bar shrinks down
        frac = 1.0 - 0.85 * ease_out_cubic(clamp01(lt / 0.8))
        d.rounded_rectangle([360, 480, 1560, 560], radius=20, outline=MUTED, width=4)
        d.rounded_rectangle([366, 486, 366 + int(1188 * frac), 554], radius=14, fill=GREEN)
        return frame
    # 9: "Year by year, the odds tilt in your favour."
    if t < s[9]:
        lt = t - s[8]
        d.text((960, 200), "YEAR BY YEAR, THE ODDS TILT IN YOUR FAVOUR", font=font(40, True), fill=TEXT, anchor="ma")
        # odds dial: green share grows year by year
        cx, cy, r = 960, 580, 200
        frac = 0.27 + 0.68 * ease_out_cubic(clamp01(lt / 2.2))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(30, 45, 68), width=26)
        d.arc([cx - r, cy - r, cx + r, cy + r], start=-90, end=-90 + 360 * frac,
              fill=GREEN, width=26)
        d.text((cx, 560), f"{int(frac * 100)}%", font=font(96, True), fill=GREEN, anchor="mm")
        d.text((cx, 660), "IN YOUR FAVOUR", font=font(30, True), fill=MUTED, anchor="ma")
        return frame
    # 10: "And remember — this is education, not personal financial advice."
    if t < s[10]:
        e = pop_in(t, s[9], 0.45)
        if e > 0:
            card(d, 360, 380, 1560, 660, GOLD, width=5)
            d.text((960, 440), "REMEMBER —", font=font(44, True), fill=TEXT, anchor="ma")
            d.text((960, 520), "THIS IS EDUCATION,", font=font(52, True), fill=GOLD, anchor="ma")
            d.text((960, 600), "NOT PERSONAL FINANCIAL ADVICE", font=font(36, True), fill=TEXT, anchor="ma")
        return frame
    # 11: "Your situation is your own, so if you're unsure, talk to a
    # licensed adviser in your country."
    if t < s[11]:
        e = pop_in(t, s[10], 0.45)
        if e > 0:
            card(d, 460, 380, 1460, 640, CYAN, width=5)
            d.text((960, 450), "YOUR SITUATION IS YOUR OWN.", font=font(40, True), fill=TEXT, anchor="ma")
            d.text((960, 540), "IF YOU'RE UNSURE,", font=font(44, True), fill=CYAN, anchor="ma")
            d.text((960, 600), "TALK TO A LICENSED ADVISER", font=font(36, True), fill=TEXT, anchor="ma")
        return frame
    # 12: "Next up — the part you've been waiting for."
    if t < s[12]:
        e = pop_in(t, s[11], 0.4)
        d.text((960, 420), "NEXT UP —", font=font(64, True), fill=TEXT, anchor="ma")
        d.text((960, 540), "THE PART YOU'VE BEEN", font=font(int(56 * e), True), fill=GOLD, anchor="ma")
        d.text((960, 620), "WAITING FOR.", font=font(int(56 * e), True), fill=GOLD, anchor="ma")
        return frame
    # 13: "How do you actually start?"
    if t < s[13]:
        e = pop_in(t, s[12], 0.45)
        if e > 0:
            card(d, 460, 380, 1460, 640, GREEN, width=5)
            d.text((960, 460), "HOW DO YOU", font=font(52, True), fill=TEXT, anchor="ma")
            d.text((960, 550), "ACTUALLY START?", font=font(int(56 * e), True), fill=GREEN, anchor="ma")
        return frame
    # 14: "Which button do you press first?"
    if t < s[14]:
        lt = t - s[13]
        d.text((960, 200), "WHICH BUTTON DO YOU PRESS FIRST?", font=font(48, True), fill=TEXT, anchor="ma")
        # big green button, pulsing
        pulse = 1 + 0.03 * math.sin((t - s[13]) * 5)
        r = int(150 * pulse)
        d.ellipse([960 - r, 540 - r, 960 + r, 540 + r], fill=GREEN, outline=BLACK, width=6)
        d.text((960, 536), "START", font=font(64, True), fill=BLACK, anchor="mm")
        if lt > 1.0:
            d.text((960, 760), "?", font=font(72, True), fill=AMBER, anchor="ma")
        return frame
    # 15: "That's part three, and it's the simple one."
    if t < s[15]:
        e = pop_in(t, s[14], 0.4)
        card(d, 560, 400, 1360, 620, GREEN, width=5)
        d.text((960, 470), "THAT'S PART THREE", font=font(52, True), fill=GREEN, anchor="ma")
        d.text((960, 550), "AND IT'S THE SIMPLE ONE", font=font(36, True), fill=TEXT, anchor="ma")
        return frame
    # 16: "See you there."
    e = pop_in(t, s[15], 0.4)
    d.text((960, 420), "SEE YOU", font=font(72, True), fill=TEXT, anchor="ma")
    if e > 0:
        d.text((960, 540), "THERE.", font=font(int(110 * e), True), fill=GOLD, anchor="ma")
        d.text((960, 700), "PART 3 OF 4  ·  HOW TO START INVESTING", font=font(36, True), fill=MUTED, anchor="ma")
    return frame


# ---------------------------------------------------------------- camera zooms (global t)
# Segment starts: 0 / 47.434 / 146.324 / 209.046 / 282.592. Scales kept
# <=1.08 and headlines placed to survive the crop (see STATUS.md).
ZOOM_KEYS = [
    (0.0, 1.00, 960, 540),
    # hook beat 5: push into the "what if that happens to me?" bubble
    (11.22, 1.00, 960, 540), (14.00, 1.06, 960, 540), (16.24, 1.06, 960, 540),
    (21.27, 1.00, 960, 540),
    # SEG1 long-chart push (global 47.434 + 51.29 = 98.72)
    (98.72, 1.00, 960, 540), (104.00, 1.06, 960, 500), (110.00, 1.06, 960, 500),
    (113.00, 1.00, 960, 540),
    # SEG1 rollercoaster (global 47.434 + 80.67 = 128.10)
    (128.10, 1.00, 960, 540), (132.00, 1.05, 960, 540), (137.00, 1.05, 960, 540),
    (138.62, 1.00, 960, 540),
    # SEG2 egg basket (global 146.324 + 46.34 = 192.66)
    (192.66, 1.00, 960, 540), (195.50, 1.06, 960, 560), (198.00, 1.06, 960, 560),
    (199.50, 1.00, 960, 540),
    # SEG3 real-question zoom (global 209.046 + 67.53 = 276.58)
    (276.58, 1.00, 960, 540), (279.00, 1.08, 960, 500), (281.00, 1.08, 960, 500),
    (282.59, 1.00, 960, 540),
    # close end card (global 282.592 + 42.72 = 325.31)
    (325.31, 1.00, 960, 540), (327.50, 1.05, 960, 540),
    (328.84, 1.05, 960, 540),
]


def zoom_params(tg):
    keys = ZOOM_KEYS
    if tg <= keys[0][0]:
        return keys[0][1:]
    for i in range(len(keys) - 1):
        t0, z0, x0, y0 = keys[i]
        t1, z1, x1, y1 = keys[i + 1]
        if t0 <= tg <= t1:
            f = (tg - t0) / (t1 - t0) if t1 > t0 else 0.0
            f = f * f * (3 - 2 * f)
            return (z0 + (z1 - z0) * f, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f)
    return keys[-1][1:]


def zoom_crop(frame, cx, cy, scale):
    if scale <= 1.001:
        return frame
    cw, ch = W / scale, H / scale
    x0 = int(max(0, min(W - cw, cx - cw / 2)))
    y0 = int(max(0, min(H - ch, cy - ch / 2)))
    return frame.crop((x0, y0, int(x0 + cw), int(y0 + ch))).resize((W, H), Image.LANCZOS)


SCENES = [scene_hook, scene_hist, scene_basket, scene_time, scene_close]


def render_frame(tg):
    """One full frame at global time tg (with segment crossfade + zoom)."""
    k = 0
    for i in range(5):
        if tg >= STARTS[i]:
            k = i
    tl = tg - STARTS[k]
    frame = Image.new("RGB", (W, H), BG)
    frame = SCENES[k](frame, tl)
    return frame, k, tl


def main():
    out = OUT
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
        for j in range(5):
            if tg >= STARTS[j]:
                k = j
        tl = tg - STARTS[k]
        frame = Image.new("RGB", (W, H), BG)
        frame = SCENES[k](frame, tl)
        # 0.5 s video crossfade at each segment start (audio beat is
        # separate 0.25 s silence — same convention as v4)
        if k >= 1 and tl < 0.5 and prev_final is not None:
            frame = Image.blend(prev_final, frame, ease_out_cubic(tl / 0.5))
        if i + 1 >= n or (k < 4 and (i + 1) / FPS >= STARTS[k + 1]):
            prev_final = frame.copy()
        z, cx, cy = zoom_params(tg)
        frame = zoom_crop(frame, cx, cy, z)
        p.stdin.write(frame.tobytes())
        if (i + 1) % 600 == 0:
            print(f"  frame {i+1}/{n} {time.time()-t0:.1f}s", flush=True)
    p.stdin.close()
    p.wait()
    assert p.returncode == 0, "ffmpeg failed"
    print(f"rendered {n} frames ({TOTAL:.2f}s) in {time.time()-t0:.1f}s -> {out}", flush=True)


def sample(sample_times, outdir):
    """Render single frames at given global times, for pre-render checks."""
    os.makedirs(outdir, exist_ok=True)
    for tg in sample_times:
        frame, k, tl = render_frame(tg)
        z, cx, cy = zoom_params(tg)
        frame = zoom_crop(frame, cx, cy, z)
        p = f"{outdir}/s{tg:07.2f}.png"
        frame.save(p)
        print(f"  {tg:7.2f}s seg{k} local {tl:6.2f} zoom {z:.2f} -> {p}", flush=True)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sample":
        times = [float(x) for x in sys.argv[2:]]
        sample(times, f"{BUILD}/samples")
    else:
        main()
