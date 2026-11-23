"""Assemble the full Ep2 video.
- Video: build/ep2_v.mp4 (PIL-only, captions NOT yet burned)
- Audio: 5 voice mp3s (00-hook 47.184s, 01-history 98.640s,
  02-basket 62.472s, 03-time 73.296s, 04-close 46.248s) joined with
  0.25 s silence beats between sections = 328.84 s total.
- Captions: 91 sentence events from render_ep2 (word-proportional
  sentence estimates, same method as Ep1/v4), [pause] stripped.
- loudnorm I=-14 / TP=-1.5 / LRA=11. No acrossfade.
Output: "Is Investing in Stocks Too Risky for Beginners?.mp4"
(episode folder, file name exactly the title).
"""
import os, subprocess, sys

BASE = "/home/hatch/workspace/youtube-pipeline/jason-explains/ep2-too-risky"
BUILD = f"{BASE}/build"
FINAL = f"{BASE}/Is Investing in Stocks Too Risky for Beginners?.mp4"
VID = f"{BUILD}/ep2_v.mp4"
SIL = f"{BUILD}/silence025.wav"
TOTAL = 328.84

VOICE = ["00-hook", "01-history", "02-basket", "03-time", "04-close"]

def run(cmd, **kw):
    r = subprocess.run(cmd, capture_output=True, text=True, **kw)
    if r.returncode != 0:
        print("FAILED:", " ".join(cmd), file=sys.stderr)
        print(r.stderr[-3000:], file=sys.stderr); sys.exit(1)
    return r

def ass_time(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

assert os.path.exists(VID), f"missing video {VID}"
assert os.path.exists(SIL), f"missing silence {SIL}"
for v in VOICE:
    assert os.path.exists(f"{BASE}/voice/{v}.mp3"), f"missing voice {v}"

sys.path.insert(0, BUILD)
import render_ep2 as R

events = []
for sec in range(5):
    for idx, (st, txt) in enumerate(zip(R.SST[sec], R.SENTS[sec])):
        en = R.SST[sec][idx + 1] if idx + 1 < len(R.SST[sec]) else R.AUD[sec]
        events.append((R.STARTS[sec] + st, R.STARTS[sec] + en, R.caption_text(txt)))
events.sort()
ass = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,DejaVu Sans,32,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,0,0,0,0,100,100,0,0,1,1,0,2,40,40,18,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
for st, en, c in events:
    assert "[pause]" not in c, f"[pause] leaked into caption: {c}"
    ass += f"Dialogue: 0,{ass_time(max(st, 0.0))},{ass_time(en)},Default,,0,0,0,,{c}\n"
with open(f"{BUILD}/ep2.ass", "w") as f:
    f.write(ass)
print("ASS events:", len(events), flush=True)
for st, en, c in events:
    print(f"  {st:6.2f}-{en:6.2f}  {c[:70]}")

# audio inputs: voice, silence, voice, silence, ... (4 beats)
inputs = []
for i, v in enumerate(VOICE):
    inputs.append((f"{BASE}/voice/{v}.mp3", "a"))
    if i < 4:
        inputs.append((SIL, "s"))
fc = f"[0:v]subtitles={BUILD}/ep2.ass,format=yuv420p[vout];\n"
for i in range(len(inputs)):
    fc += f"[{i + 1}:a]aresample=48000[a{i}];\n"
ac = "".join(f"[a{i}]" for i in range(len(inputs)))
fc += f"{ac}concat=n={len(inputs)}:v=0:a=1[aconc];\n"
fc += "[aconc]loudnorm=I=-14:TP=-1.5:LRA=11[aout]\n"
with open(f"{BUILD}/ep2.fc", "w") as f:
    f.write(fc)

if os.path.exists(FINAL):
    os.remove(FINAL)
cmd = ["ffmpeg", "-y", "-v", "error", "-i", VID]
for p, _ in inputs:
    cmd += ["-i", p]
cmd += ["-filter_complex_script", f"{BUILD}/ep2.fc",
        "-map", "[vout]", "-map", "[aout]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
        "-c:a", "aac", "-b:a", "192k", "-r", "30", "-shortest", FINAL]
run(cmd)
print("FINAL:", FINAL, flush=True)
r = run(["ffprobe", "-v", "error", "-show_entries",
         "format=duration,size", "-show_entries",
         "stream=codec_name,width,height,r_frame_rate",
         "-of", "default=noprint_wrappers=1", FINAL])
print(r.stdout)
print("DONE")
