"""Ep2 TTS: 5 segments, Helio (avocado_v2:MAI_03).
Speeds per task: SEG 0 hook 110 (excited), SEG 1 history/numbers 92
(grave, slower for numbers), SEG 2 basket 100, SEG 3 time 98,
SEG 4 close 104.
Note: script contains [pause] markers. Verified 22 Nov 2026 with a
test synth: "[pause]" is NOT spoken aloud by the TTS (test with the
marker was 2.328 s vs 2.400 s without — no extra word, no added
pause). So the script text is passed through as-is, exactly like
ep1's tts_ep1.py. Captions strip "[pause]" separately (captions_ep2).
"""
import re, subprocess, os, sys

BASE = "/home/hatch/workspace/youtube-pipeline/jason-explains/ep2-too-risky"
SRC = f"{BASE}/script-jason.txt"
OUT = f"{BASE}/voice"
os.makedirs(OUT, exist_ok=True)

SEGS = [
    (0, "00-hook", 110),
    (1, "01-history", 92),
    (2, "02-basket", 100),
    (3, "03-time", 98),
    (4, "04-close", 104),
]

text = open(SRC).read()
parts = re.split(r"\[SEG (\d+)\]", text)
body = {}
for i in range(1, len(parts), 2):
    body[int(parts[i])] = parts[i + 1].strip()

def synth(fname, txt, speed):
    txt = txt.strip()
    out = f"{OUT}/{fname}.mp3"
    print(f"{fname}: {len(txt.split())} words @ speed {speed}", flush=True)
    r = subprocess.run(["/opt/hatch/bin/tts", "speak", "--output", out,
                        "--voice", "avocado_v2:MAI_03", "--speed", str(speed),
                        "--text-stdin"],
                       input=txt.encode(), stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, timeout=300)
    print(r.stdout.decode()[:200], flush=True)
    if r.returncode != 0:
        print("FAILED", fname, r.stderr.decode()[:500], file=sys.stderr); sys.exit(1)

for num, fname, speed in SEGS:
    synth(fname, body[num], speed)

print("all ep2 tts done", flush=True)
