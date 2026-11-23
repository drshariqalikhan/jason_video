"""WhySector-style pilot renderer — Option A, 30 fps PIL, single pass.
Dark near-black navy, neon-outline flat vector art, own stick figures.
Frames piped straight to ffmpeg (no frame files on disk).
Work dir: ~/workspace/youtube-pipeline/whysector-pilot
"""
import json, math, os, re, subprocess, sys, time
from PIL import Image, ImageDraw, ImageFont

BASE = "/home/hatch/workspace/youtube-pipeline/whysector-pilot"
OUT = f"{BASE}/build"
W, H = 1920, 1080
FPS = 30

BG = (8, 12, 22)
PANEL = (15, 27, 45)
PANEL2 = (18, 34, 56)
TEXT = (226, 232, 240)
MUTED = (148, 163, 184)
AMBER = (245, 158, 11)
GOLD = (252, 211, 77)
GREEN = (34, 197, 94)
RED = (242, 54, 69)
CYAN = (56, 189, 248)
WHITE = (255, 255, 255)
BROWN = (146, 104, 62)
BROWN_D = (110, 76, 44)
YELLOW = (252, 211, 77)
APPLE_Y = (252, 211, 77)
APPLE_B = (186, 230, 253)

# measured mp3 durations (s) — ground truth from ffprobe (7 segments)
AUD = [6.840, 15.192, 17.496, 16.272, 13.080, 7.704, 15.576]
BEAT = 0.25  # silence beat after segments 0-5 (PANW rule, no acrossfade)
D = [a + (BEAT if i < 6 else 0.0) for i, a in enumerate(AUD)]
STARTS = []
_acc = 0.0
for d in D:
    STARTS.append(_acc)
    _acc += d
TOTAL = _acc
print("video durs:", [round(x, 3) for x in D], "starts:", [round(x, 3) for x in STARTS],
      "total:", round(TOTAL, 3), flush=True)

def font(sz, bold=False):
    p = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold \
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    return ImageFont.truetype(p, sz)

def ease_out_cubic(t):
    t = min(max(t, 0.0), 1.0)
    return 1 - pow(1 - t, 3)

def ease_in_out(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)

def clamp01(x):
    return min(max(x, 0.0), 1.0)

def split_sents(text):
    sents = [s.strip() for s in re.split(r"(?<=[.?!])\s+", text) if s.strip()]
    return [s for s in sents if re.search(r"[A-Za-z0-9]", s)]

def sent_starts(text, total):
    """word-proportional sentence start times inside a segment."""
    sents = split_sents(text)
    tot = sum(len(s.split()) for s in sents)
    out, acc = [], 0.0
    for s in sents:
        w = len(s.split())
        out.append(acc * total / tot)
        acc += w
    return sents, out

SCRIPT = open(f"{BASE}/script-jason.txt").read()
_parts = re.split(r"\[SEG (\d+)\]", SCRIPT)
SEGTEXT = {}
for i in range(1, len(_parts), 2):
    SEGTEXT[int(_parts[i])] = _parts[i + 1].strip()
SENTS, SST = {}, {}
for i in range(7):
    SENTS[i], SST[i] = sent_starts(SEGTEXT[i], AUD[i])
    print(f"seg{i} sents:", [(round(s, 2), t[:38]) for s, t in zip(SST[i], SENTS[i])], flush=True)

def draw_text(d, cx, y, text, f, fill, anchor="ma"):
    d.text((cx, y), text, font=f, fill=fill, anchor=anchor)

# ---------------------------------------------------------------- groups
def make_group(w, h, draw_fn):
    """Draw on transparent RGBA, return (rgb, alpha-mask)."""
    ov = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    draw_fn(d, w, h)
    return ov.convert("RGB"), ov.split()[3]

class Group:
    """Pre-rendered art that fades + rises in at `start`."""
    def __init__(self, rgb, alpha, box):
        self.rgb, self.alpha, self.box = rgb, alpha, box
        self._masks = {}
    def mask(self, e):
        q = round(e, 2)
        if q not in self._masks:
            self._masks[q] = self.alpha.point(lambda v: int(v * q)) if q < 1.0 else self.alpha
        return self._masks[q]
    def paste(self, frame, t, start, dur=0.5, rise=24):
        e = ease_out_cubic(clamp01((t - start) / dur))
        if e <= 0.0:
            return
        x0, y0, x1, y1 = self.box
        frame.paste(self.rgb, (x0, y0 + int(round((1 - e) * rise))), self.mask(e))

def stick(d, x, y, s, col, pose="stand", lw=None):
    """Stick figure, head top at (x, y), total height ~s. RGBA-aware draw."""
    lw = lw or max(3, int(s * 0.045))
    r = 0.16 * s
    d.ellipse([x - r, y - r, x + r, y + r], outline=col, width=lw)
    hy, by = y + r, y + 0.55 * s
    d.line([x, hy, x, by], fill=col, width=lw)
    sh = y + 0.28 * s
    if pose == "run":
        d.line([x, by, x - 0.20 * s, y + 0.82 * s, x - 0.05 * s, y + 1.0 * s],
               fill=col, width=lw, joint="curve")
        d.line([x, by, x + 0.22 * s, y + 0.80 * s, x + 0.28 * s, y + 0.98 * s],
               fill=col, width=lw, joint="curve")
        d.line([x, sh, x - 0.24 * s, sh + 0.10 * s], fill=col, width=lw)
        d.line([x, sh, x + 0.24 * s, sh - 0.08 * s], fill=col, width=lw)
    elif pose == "push":
        d.line([x, by, x - 0.16 * s, y + 1.0 * s], fill=col, width=lw)
        d.line([x, by, x + 0.20 * s, y + 0.82 * s, x + 0.30 * s, y + 1.0 * s],
               fill=col, width=lw, joint="curve")
        d.line([x, sh, x + 0.30 * s, sh + 0.06 * s], fill=col, width=lw)
        d.line([x, sh, x + 0.28 * s, sh + 0.16 * s], fill=col, width=lw)
    elif pose == "hold":
        d.line([x, by, x - 0.18 * s, y + 1.0 * s], fill=col, width=lw)
        d.line([x, by, x + 0.18 * s, y + 1.0 * s], fill=col, width=lw)
        d.line([x, sh, x - 0.22 * s, sh + 0.14 * s], fill=col, width=lw)
        d.line([x, sh, x + 0.22 * s, sh - 0.16 * s], fill=col, width=lw)
    else:  # stand
        d.line([x, by, x - 0.18 * s, y + 1.0 * s], fill=col, width=lw)
        d.line([x, by, x + 0.18 * s, y + 1.0 * s], fill=col, width=lw)
        d.line([x, sh, x - 0.22 * s, sh + 0.16 * s], fill=col, width=lw)
        d.line([x, sh, x + 0.22 * s, sh + 0.16 * s], fill=col, width=lw)

def glow_halo(d, x, y, r, col, alpha=90):
    """Soft filled glow (no rings): two large faint discs behind the figure."""
    for rr, a in ((r * 2.1, 10), (r * 1.5, 16)):
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=col + (a,))

def apple(d, cx, cy, r, body, leaf=True):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=body,
              outline=(0, 0, 0, 90), width=2)
    d.line([cx, cy - r, cx + 2, cy - r - 10], fill=(34, 120, 60, 255), width=3)
    if leaf:
        d.ellipse([cx + 4, cy - r - 12, cx + 18, cy - r - 2],
                  fill=(74, 180, 90, 255))

# ---------------------------------------------------------------- text helpers
def _paste_alpha(frame, tmp, x, y, e):
    bbox = tmp.getbbox()
    if not bbox:
        return
    crop = tmp.crop(bbox)
    alpha = crop.split()[3]
    if e < 1.0:
        alpha = alpha.point(lambda v: int(v * e))
    frame.paste(crop.convert("RGB"), (x + bbox[0], y + bbox[1]), alpha)

def faded_text(frame, x, y, text, f, fill, t, start, dur=0.5):
    """Left-anchored text fading in at `start`."""
    e = ease_out_cubic(clamp01((t - start) / dur))
    if e <= 0.0:
        return
    tmp = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((x, 0), text, font=f, fill=fill + (255,))
    _paste_alpha(frame, tmp, 0, y, e)

def faded_text_c(frame, cx, y, text, f, fill, t, start, dur=0.5):
    w = f.getlength(text)
    faded_text(frame, int(cx - w / 2), y, text, f, fill, t, start, dur)

def faded_rich(frame, cx, y, parts, f, t, start, dur=0.5):
    """parts=[(text, fill)] centred, fading in together."""
    e = ease_out_cubic(clamp01((t - start) / dur))
    if e <= 0.0:
        return
    tot = sum(f.getlength(p[0]) for p in parts)
    tmp = Image.new("RGBA", (W, 160), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    x = int((W - tot) / 2)
    for txt, fill in parts:
        d.text((x, 0), txt, font=f, fill=fill + (255,))
        x += int(f.getlength(txt))
    _paste_alpha(frame, tmp, 0, y, e)

def panel(d, x0, y0, x1, y1, outline=CYAN, width=2, fill=PANEL):
    d.rounded_rectangle([x0, y0, x1, y1], radius=14, fill=fill, outline=outline, width=width)

def title_tag(d, text):
    d.text((90, 58), text, font=font(28, True), fill=MUTED)

# ---------------------------------------------------------------- S0 hook
def scene0(frame, t):
    d = ImageDraw.Draw(frame)
    title_tag(d, "WHY IS THE MARKET CRASHING?")
    # you-figure watching the chart
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(ov)
    glow_halo(od, 470, 780, 34, CYAN, 70)
    stick(od, 470, 700, 190, CYAN + (255,), pose="stand")
    e = ease_out_cubic(clamp01(t / 0.5))
    frame.paste(ov.convert("RGB"), (0, 0), ov.split()[3].point(lambda v: int(v * e)))
    # falling chart draws on during sentence 0
    pts = [(560, 760), (700, 715), (850, 695), (1000, 745), (1150, 820), (1360, 885)]
    p = ease_out_cubic(clamp01(t / 2.5))
    segs = (len(pts) - 1) * p
    for k in range(len(pts) - 1):
        if segs <= k:
            break
        f = min(1.0, segs - k)
        x0, y0 = pts[k]
        x1, y1 = pts[k + 1]
        d.line([x0, y0, x0 + (x1 - x0) * f, y0 + (y1 - y0) * f], fill=RED, width=6)
    if p > 0.05:
        d.text((560, 660), "MY PORTFOLIO", font=font(26, True), fill=MUTED)
    if p > 0.95:
        faded_text(frame, 1400, 830, "−10%", font(64, True), RED, t, 2.4, 0.4)
    faded_text_c(frame, 960, 330, "WHY IS THE MARKET", font(84, True), TEXT, t, SST[0][1], 0.6)
    faded_text_c(frame, 960, 440, "CRASHING?", font(84, True), TEXT, t, SST[0][1] + 0.4, 0.6)
    faded_text_c(frame, 960, 560, "Explained like you're five.", font(46), CYAN, t, SST[0][2], 0.6)
    # little lemon icon next to the subtitle
    if t > SST[0][2]:
        d2 = ImageDraw.Draw(frame)
        d2.ellipse([534, 559, 586, 611], fill=YELLOW)
        d2.ellipse([560, 552, 578, 566], fill=(74, 180, 90))
    return frame

# ---------------------------------------------------------------- S1 lemonade
def _stand_group():
    def draw(d, w, h):
        # glow FIRST: ImageDraw replaces pixels on RGBA, so a soft glow
        # drawn later would erase the sign text underneath it.
        glow_halo(d, 148, 150, 30, CYAN, 70)
        # awning stripes
        for i in range(6):
            x0 = 10 + i * 46
            col = (252, 211, 77, 255) if i % 2 == 0 else (255, 255, 255, 255)
            d.polygon([(x0, 20), (x0 + 46, 20), (x0 + 46, 60), (x0, 60)], fill=col)
        d.rectangle([10, 60, 286, 70], fill=(146, 104, 62, 255))
        # sign
        d.rounded_rectangle([82, 78, 214, 112], radius=8, fill=(15, 27, 45, 255),
                            outline=(252, 211, 77, 255), width=2)
        d.text((148, 84), "LEMONADE", font=font(18, True), fill=(252, 211, 77, 255), anchor="ma")
        # vendor (cyan glow figure) behind counter
        stick(d, 148, 130, 120, CYAN + (255,), pose="stand")
        # counter
        d.rectangle([20, 260, 276, 400], fill=BROWN + (255,))
        d.rectangle([20, 260, 276, 278], fill=BROWN_D + (255,))
        d.line([20, 330, 276, 330], fill=BROWN_D + (255,), width=3)
        # cups on counter
        for cx in (60, 110, 235):
            d.polygon([(cx - 12, 232), (cx + 12, 232), (cx + 8, 260), (cx - 8, 260)],
                      fill=(252, 211, 77, 255))
            d.line([cx, 232, cx, 218], fill=(255, 255, 255, 255), width=3)
    return make_group(296, 410, draw)

def _lemon_card_shell(x0, x1, title):
    def draw(d, w, h):
        panel(d, 0, 0, w - 1, h - 1)
        d.text((28, 26), title, font=font(26, True), fill=MUTED)
    return make_group(x1 - x0, 330, draw)

def _crowd_group():
    def draw(d, w, h):
        x = 20
        i = 0
        while x < w - 40:
            s = 95 + (i % 3) * 12
            stick(d, x, h - s - 8, s, WHITE + (255,), pose="hold" if i % 3 == 0 else "stand")
            if i % 3 == 0:
                d.ellipse([x + 14, h - s - 58, x + 34, h - s - 38], fill=YELLOW + (255,))
            x += 120
            i += 1
    return make_group(1800, 130, draw)

_STAND = Group(*_stand_group(), (830, 470, 1126, 880))
_CROWD = Group(*_crowd_group(), (60, 880, 1860, 1010))
_CARD_L = Group(*_lemon_card_shell(90, 620, "REALITY — THE STAND TODAY"), (90, 250, 620, 580))
_CARD_R = Group(*_lemon_card_shell(1300, 1830, "PRICE — BUSINESS VALUE"), (1300, 250, 1830, 580))

def scene1(frame, t):
    d = ImageDraw.Draw(frame)
    title_tag(d, "1 · THE LEMONADE STAND")
    s = SST[1]
    _STAND.paste(frame, t, s[0], 0.5, 24)
    # crowd: fade in, then gentle bob
    if t > s[2] + 0.6:
        bob = int(3 * math.sin(t * 2.2))
        frame.paste(_CROWD.rgb, (60, 880 + bob), _CROWD.alpha)
    else:
        _CROWD.paste(frame, t, s[2], 0.6, 0)
    _CARD_L.paste(frame, t, s[1], 0.5, 24)
    if t > s[1] + 0.3:
        faded_text(frame, 118, 380, "100 GLASSES / DAY", font(40, True), TEXT, t, s[1] + 0.3, 0.5)
    if t > s[1] + 1.0:
        faded_text(frame, 118, 450, "$100", font(64, True), AMBER, t, s[1] + 1.0, 0.5)
        faded_text(frame, 300, 478, "DAILY PROFIT", font(26, True), MUTED, t, s[1] + 1.0, 0.5)
    _CARD_R.paste(frame, t, s[2], 0.5, 24)
    # count-up $21,100 -> $100,000 over 2.5s from sentence 2
    cu0 = s[2] + 0.4
    if t > cu0:
        p = ease_out_cubic(clamp01((t - cu0) / 2.5))
        val = 21100 + (100000 - 21100) * p
        txt = f"${val:,.0f}"
        d.text((1565, 390), txt, font=font(76, True), fill=GREEN, anchor="ma")
    if t > s[4]:
        faded_text_c(frame, 1565, 500, "+900% MORE THAN IT'S WORTH", font(30, True), RED, t, s[4], 0.5)
    return frame

# ---------------------------------------------------------------- S2 cart
def _cart_group():
    def draw(d, w, h):
        # cyan figure pushing the cart (figure left, cart right)
        glow_halo(d, 95, 95, 30, CYAN, 70)
        stick(d, 95, 40, 170, CYAN + (255,), pose="push")
        # cart: handle + basket trapezoid + wheels
        d.line([150, 150, 210, 150], fill=WHITE + (255,), width=6)
        d.line([210, 150, 240, 250], fill=WHITE + (255,), width=6)
        d.polygon([(240, 150), (620, 150), (580, 260), (270, 260)],
                  outline=WHITE + (255,), width=5)
        d.line([280, 185, 600, 185], fill=WHITE + (255,), width=3)
        d.line([300, 220, 590, 220], fill=WHITE + (255,), width=3)
        # groceries
        d.rectangle([300, 95, 350, 150], fill=WHITE + (255,))          # milk carton
        d.rectangle([312, 82, 338, 95], fill=(56, 189, 248, 255))
        d.rectangle([380, 80, 440, 150], fill=(252, 211, 77, 255))     # cereal box
        d.ellipse([480, 110, 530, 150], fill=(242, 54, 69, 255))       # apple
        d.rectangle([545, 100, 600, 150], fill=(146, 104, 62, 255))    # bread box
        # wheels
        d.ellipse([290, 260, 330, 300], outline=WHITE + (255,), width=5)
        d.ellipse([530, 260, 570, 300], outline=WHITE + (255,), width=5)
    return make_group(700, 320, draw)

def _price_panel(x0, x1, title, sub):
    def draw(d, w, h):
        panel(d, 0, 0, w - 1, h - 1)
        d.text((28, 26), title, font=font(26, True), fill=MUTED)
        d.text((28, 66), sub, font=font(22), fill=MUTED)
    return make_group(x1 - x0, 320, draw)

_CART = _cart_group()
_PANEL_LAST = Group(*_price_panel(1120, 1470, "LAST YEAR", "SAME GROCERIES"), (1120, 300, 1470, 620))
_PANEL_THIS = Group(*_price_panel(1520, 1870, "THIS YEAR", "SAME GROCERIES"), (1520, 300, 1870, 620))

def scene2(frame, t):
    d = ImageDraw.Draw(frame)
    title_tag(d, "2 · THE GROCERY CART")
    s = SST[2]
    # cart slides in from the left during sentence 0
    if t > 0.0:
        e = ease_out_cubic(clamp01(t / 1.2))
        x = int(330 - 1100 * (1 - e))
        a = min(1.0, t / 0.4)
        alpha = _CART[1].point(lambda v: int(v * a)) if a < 1.0 else _CART[1]
        frame.paste(_CART[0], (x, 560), alpha)
    _PANEL_LAST.paste(frame, t, s[1], 0.5, 24)
    if t > s[1] + 0.3:
        faded_text(frame, 1148, 470, "$100.00", font(64, True), TEXT, t, s[1] + 0.3, 0.5)
    _PANEL_THIS.paste(frame, t, s[2], 0.5, 24)
    # count-up $100.00 -> $110.00 during "A hundred and ten."
    if t > s[3]:
        p = ease_out_cubic(clamp01((t - s[3]) / 1.5))
        val = 100 + 10 * p
        d.text((1695, 470), f"${val:.2f}", font=font(64, True), fill=RED, anchor="ma")
    if t > s[4]:
        faded_text_c(frame, 1695, 250, "+10%", font(40, True), RED, t, s[4], 0.4)
        faded_text_c(frame, 960, 900, "SAME GROCERIES. HIGHER PRICE.", font(40, True), TEXT, t, s[4], 0.5)
    if t > s[5]:
        faded_text_c(frame, 1695, 650, "INFLATION", font(34, True), RED, t, s[5], 0.5)
    if t > s[6]:
        faded_text_c(frame, 1495, 700, "HIGH RATES → STOCKS LOOK EXPENSIVE", font(30, True), MUTED, t, s[6], 0.5)
    return frame

# ---------------------------------------------------------------- S3 apples
def _basket_group():
    def draw(d, w, h):
        # trapezoid basket with slats
        d.polygon([(20, 40), (620, 40), (580, 240), (60, 240)], fill=BROWN + (255,))
        d.polygon([(20, 40), (620, 40), (600, 70), (40, 70)], fill=BROWN_D + (255,))
        for yy in (100, 150, 200):
            d.line([35, yy, 605, yy], fill=BROWN_D + (255,), width=4)
        # 6 light-blue apples inside
        for i, cx in enumerate((110, 205, 300, 395, 490, 575)):
            apple(d, cx, 130 + (i % 2) * 8, 40, APPLE_B + (255,))
    return make_group(640, 250, draw)

def _four_apples_group():
    def draw(d, w, h):
        for cx in (70, 200, 330, 460):
            apple(d, cx, 60, 52, APPLE_Y + (255,))
    return make_group(530, 120, draw)

_BASKET = Group(*_basket_group(), (640, 560, 1280, 810))
_FOUR = Group(*_four_apples_group(), (695, 360, 1225, 480))

def scene3(frame, t):
    d = ImageDraw.Draw(frame)
    title_tag(d, "3 · THE APPLE BASKET")
    s = SST[3]
    _BASKET.paste(frame, t, s[0], 0.5, 24)
    _FOUR.paste(frame, t, s[0] + 0.4, 0.5, 24)
    # basket value top centre (counts down $100 -> $92 during the fall sentence)
    fall0 = s[3] + 0.6
    if t > s[0] + 0.5:
        d.text((960, 110), "BASKET VALUE", font=font(30, True), fill=MUTED, anchor="ma")
    if t > s[0] + 0.5:
        if t < fall0:
            d.text((960, 150), "$100", font=font(110, True), fill=TEXT, anchor="ma")
        else:
            p = ease_out_cubic(clamp01((t - fall0) / 1.8))
            val = 100 - 8 * p
            d.text((960, 150), f"${val:.0f}", font=font(110, True), fill=RED, anchor="ma")
    # 4-apple label (counts $40 -> $32)
    if t > s[1]:
        if t < fall0:
            faded_text_c(frame, 960, 300, "4 APPLES = $40", font(40, True), AMBER, t, s[1], 0.5)
        else:
            p = ease_out_cubic(clamp01((t - fall0) / 1.8))
            val = 40 - 8 * p
            d.text((960, 300), f"4 APPLES = ${val:.0f}", font=font(40, True), fill=RED, anchor="ma")
    if t > s[2]:
        faded_text_c(frame, 960, 830, "6 APPLES = $60", font(40, True), TEXT, t, s[2], 0.5)
    if t > fall0 + 1.0:
        faded_text(frame, 1330, 170, "-20%", font(56, True), RED, t, fall0 + 1.0, 0.4)
    if t > s[4]:
        faded_text_c(frame, 960, 920, "A FEW BIG STOCKS DRAG THE WHOLE INDEX DOWN",
                     font(36, True), TEXT, t, s[4], 0.5)
    return frame

# ---------------------------------------------------------------- S4 smoke
def _room_group():
    def draw(d, w, h):
        d.rectangle([0, 0, w - 1, h - 1], fill=PANEL)
        d.line([0, h - 60, w, h - 60], fill=(56, 189, 248, 255), width=3)
        # EXIT door, right side
        d.rectangle([w - 150, 300, w - 30, h - 60], outline=RED + (255,), width=4)
        d.text((w - 90, 250), "EXIT", font=font(36, True), fill=RED + (255,), anchor="ma")
    return make_group(1740, 700, draw)

def _smoke_sprite():
    ov = Image.new("RGBA", (340, 220), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # soft radial blobs: 10 concentric filled ellipses, alpha rising inward
    for (cx, cy, r, a) in ((90, 150, 70, 55), (150, 110, 90, 48), (220, 140, 75, 50),
                           (180, 70, 60, 38), (260, 90, 55, 34)):
        for k in range(10, 0, -1):
            rr = r * k / 10
            aa = int(a * (1.15 - k / 10))
            d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], fill=(200, 210, 225, max(aa, 2)))
    return ov

_ROOM = Group(*_room_group(), (90, 180, 1830, 880))
_SMOKE = _smoke_sprite()

def _chip_group(text):
    f = font(28, True)
    w = 420  # fixed width so the paste box always matches
    def draw(d, ww, h):
        d.rounded_rectangle([0, 0, ww - 1, h - 1], radius=32,
                            outline=RED + (255,), width=3)
        d.text((ww // 2, 16), text, font=f, fill=RED + (255,), anchor="ma")
    return make_group(w, 64, draw)

_CHIP1 = Group(*_chip_group("▼ PRICE FALLS"), (270, 920, 690, 984))
_CHIP2 = Group(*_chip_group("INVESTORS SELL"), (750, 920, 1170, 984))
_CHIP3 = Group(*_chip_group("▼ PRICE FALLS FURTHER"), (1230, 920, 1650, 984))

def scene4(frame, t):
    d = ImageDraw.Draw(frame)
    s = SST[4]
    faded_text(frame, 90, 80, "WHERE IS THE SMOKE?", font(54, True), TEXT, t, s[0], 0.6)
    _ROOM.paste(frame, t, s[0], 0.5, 24)
    # smoke drifts, alpha breathes
    if t > s[0] + 0.3:
        a = 0.55 + 0.25 * math.sin(t * 1.1)
        dx = int(12 * math.sin(t * 0.45))
        alpha = _SMOKE.split()[3].point(lambda v: int(v * a))
        frame.paste(_SMOKE.convert("RGB"), (200 + dx, 230), alpha)
    # crowd runs toward the exit (drawn per-frame so figures fade at the door)
    if t > s[1]:
        slide = 520 * ease_in_out(clamp01((t - s[1]) / 9.0))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        for i in range(22):
            bx = 700 + (i % 11) * 72
            by = 430 + (i // 11) * 190 + (i % 3) * 14
            x = bx + slide
            y = by + 4 * math.sin(t * 3.0 + i * 1.3)
            al = 255 if x < 1620 else max(0, int(255 - (x - 1620) * 2))
            if al <= 0:
                continue
            stick(od, int(x), int(y), 120, WHITE + (al,), pose="run")
        frame.paste(ov.convert("RGB"), (0, 0), ov.split()[3])
    _CHIP1.paste(frame, t, s[2], 0.4, 0)
    _CHIP2.paste(frame, t, s[2] + 0.9, 0.4, 0)
    _CHIP3.paste(frame, t, s[2] + 1.8, 0.4, 0)
    return frame

# ---------------------------------------------------------------- S5 dominoes
def _domino_tile():
    ov = Image.new("RGBA", (320, 320), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    # standing domino with its BOTTOM-RIGHT corner at tile centre (160,160):
    # rotating about that corner lays it flat on the floor line.
    d.rounded_rectangle([116, 10, 160, 160], radius=6, fill=(18, 34, 56, 255),
                        outline=RED + (255,), width=4)
    d.ellipse([132, 78, 144, 90], fill=RED + (255,))
    return ov

_DOMINO = _domino_tile()
_DOM_X = [240, 400, 560, 720, 880, 1040]
_DOM_FLOOR = 780

def scene5(frame, t):
    d = ImageDraw.Draw(frame)
    title_tag(d, "5 · DOMINOES — CONTAGION")
    s = SST[5]
    d.line([100, _DOM_FLOOR, 1820, _DOM_FLOOR], fill=MUTED, width=3)
    fall0 = s[0] + 0.3
    for k, px in enumerate(_DOM_X):
        st = fall0 + k * 0.55
        if t < st:
            ang = 0.0
        else:
            u = clamp01((t - st) / 0.6)
            ang = -80.0 * u * u  # falls right, accelerating
        tile = _DOMINO.rotate(ang, resample=Image.BICUBIC)
        frame.paste(tile.convert("RGB"), (px - 160, _DOM_FLOOR - 160),
                    tile.split()[3])
    if t > fall0 + 2 * 0.55:
        faded_text_c(frame, 480, 850, "TECH FUNDS", font(26, True), RED, t, fall0 + 1.1, 0.4)
    if t > fall0 + 4 * 0.55:
        faded_text_c(frame, 800, 850, "MARKET INDEXES", font(26, True), RED, t, fall0 + 2.2, 0.4)
    # three standing bars: not everything falls
    if t > s[2]:
        e = ease_out_cubic(clamp01((t - s[2]) / 0.5))
        for j, (bx, bh) in enumerate(((1300, 120), (1380, 180), (1460, 150))):
            h = int(bh * e)
            d.rectangle([bx, _DOM_FLOOR - h, bx + 44, _DOM_FLOOR],
                        outline=CYAN, width=3)
        faded_text_c(frame, 1380, 850, "NOT EVERYTHING FALLS", font(26, True), CYAN, t, s[2], 0.5)
    return frame

# ---------------------------------------------------------------- S6 factory
def _factory_group():
    def draw(d, w, h):
        # neon outline factory: sawtooth roof, chimney, 3 windows
        d.polygon([(40, 380), (40, 200), (140, 200), (140, 140), (220, 200),
                   (300, 140), (380, 200), (460, 200), (460, 380)],
                  outline=CYAN + (255,), width=5)
        d.rectangle([380, 60, 430, 200], outline=CYAN + (255,), width=5)
        for wx in (90, 210, 330):
            d.rectangle([wx, 270, wx + 60, 330], outline=CYAN + (255,), width=4)
        d.text((250, 400), "THE FACTORY", font=font(28, True), fill=MUTED + (255,), anchor="ma")
    return make_group(500, 440, draw)

def _gold_bar():
    def draw(d, w, h):
        d.rounded_rectangle([0, 0, w - 1, h - 1], radius=8, fill=GOLD + (255,))
        d.text((w // 2, 8), "$1M", font=font(26, True), fill=(0, 0, 0, 255), anchor="ma")
    return make_group(340, 46, draw)

_FACTORY = Group(*_factory_group(), (180, 380, 680, 820))
_BAR = _gold_bar()

def scene6(frame, t):
    d = ImageDraw.Draw(frame)
    title_tag(d, "6 · THE FACTORY")
    s = SST[6]
    _FACTORY.paste(frame, t, s[0], 0.5, 24)
    # gold bars stack one by one during sentence 1; count-up follows
    bar0 = s[1] + 0.3
    nbars = 0
    for k in range(10):
        st = bar0 + k * 0.35
        if t < st:
            break
        nbars = k + 1
        e = ease_out_cubic(clamp01((t - st) / 0.3))
        y = 780 - k * 50
        alpha = _BAR[1].point(lambda v: int(v * e)) if e < 1.0 else _BAR[1]
        frame.paste(_BAR[0], (1030, y), alpha)
    if t > s[1]:
        d.text((1200, 200), "INITIAL INVESTMENT", font=font(30, True), fill=MUTED, anchor="ma")
        d.text((1200, 250), f"${nbars * 1000000:,}", font=font(60, True), fill=AMBER, anchor="ma")
    if t > s[1] + 3.0:
        e = ease_out_cubic(clamp01((t - (s[1] + 3.0)) / 0.5))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(ov)
        od.rectangle([1030, 860, 1090, 906], fill=GOLD + (255,))
        od.text((1060, 868), "$", font=font(28, True), fill=(0, 0, 0, 255), anchor="ma")
        frame.paste(ov.convert("RGB"), (0, 0), ov.split()[3].point(lambda v: int(v * e)))
        faded_text(frame, 1110, 868, "ANNUAL PROFIT   $100,000", font(34, True), GOLD, t, s[1] + 3.0, 0.5)
    if t > s[2]:
        faded_rich(frame, 960, 920,
                   [("IT WOULD TAKE ", TEXT), ("100 YEARS", AMBER), (" TO EARN IT BACK", TEXT)],
                   font(44, True), t, s[2], 0.5)
    if t > s[4]:
        faded_text_c(frame, 960, 120, "PRICES RAN AHEAD OF PROFITS.", font(40, True), TEXT, t, s[4], 0.5)
    return frame

# ---------------------------------------------------------------- main
SCENES = [scene0, scene1, scene2, scene3, scene4, scene5, scene6]

def main():
    out = f"{OUT}/pilot_v.mp4"
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
        while k < 6 and tg >= STARTS[k + 1]:
            k += 1
        tl = tg - STARTS[k]
        frame = Image.new("RGB", (W, H), BG)
        frame = SCENES[k](frame, tl)
        if k > 0 and tl < 0.5 and prev_final is not None:
            frame = Image.blend(prev_final, frame, ease_out_cubic(tl / 0.5))
        if i + 1 >= n or (k < 6 and (i + 1) / FPS >= STARTS[k + 1]):
            prev_final = frame.copy()
        p.stdin.write(frame.tobytes())
        if (i + 1) % 300 == 0:
            print(f"  frame {i+1}/{n} {time.time()-t0:.1f}s", flush=True)
    p.stdin.close()
    p.wait()
    assert p.returncode == 0, "ffmpeg failed"
    print(f"rendered {n} frames ({TOTAL:.2f}s) in {time.time()-t0:.1f}s -> {out}", flush=True)

if __name__ == "__main__":
    main()
