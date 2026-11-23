# Jason Explains — Animation Pipeline README

**Date:** 22 November 2026
**Status:** Proven — built all four videos of Series 1, all published on YouTube.
**Channel:** Market Mechanics — https://www.youtube.com/channel/UCie64cxbT6qX8LYE8gmYYYw
**Playlist:** "Investing for Nervous Beginners" — https://www.youtube.com/playlist?list=PLCbHL8yd2ajM

Series 1 (all Public, 22 Nov 2026):

| Ep | Title | Length | Link |
|----|-------|--------|------|
| 1 | Don't Touch Stocks Until You Do These 3 Things | 5:06 | https://youtu.be/BkauqAqAQ80 |
| 2 | Is Investing in Stocks Too Risky for Beginners? | 5:29 | https://youtu.be/mbD8rRTJPZo |
| 3 | How to Start Investing in Stocks the Safe Way (Beginners) | 5:15 | https://youtu.be/As6D-mvo1PU |
| 4 | Markets Are Crashing – What Should Beginners Do? | 6:08 | https://youtu.be/l23r3q8Y8Io |

## 1. What this is — and what it is not

This is the code that turns a written narrative script into a finished animated
video in the Jason Explains style (dark, WhySector-style explainer animation:
glowing charts, big captions, simple vector objects, camera moves instead of
characters).

**It is NOT a one-click tool.** There is no single program where you paste a
script and a video comes out. Each episode was built from its own render script
(`render_ep2.py`, `render_ep3.py`, …), written for that episode. What is shared
and reusable is the method, the style sheet, the chart code, the caption system
and the assembler. The part that is still manual for every new episode is
**designing each sentence's animation** — the sentence-to-animation map — and
writing that episode's render script around it.

The companion package in Google Drive contains **Episode 2's code exactly as
built** (plus the two shared modules it imports). Episode 2 was chosen because
it has the shortest dependency chain of the four. See §5 for the full inventory.

## 2. How a video is made, end to end

```
script-jason.txt  →  TTS voiceover  →  sentence timing  →  beat map
→  PIL frame render  →  silent video  →  ffmpeg assembly
→  verification  →  upload to YouTube Studio
```

### Step 1 — Write the script (`script-jason.txt`)

- Plain text, ~750–1,100 words for a 5–7 minute video.
- Split into segments with `[SEG n]` markers (Ep2 has 5: hook, history, basket,
  time, close). Each segment becomes one voiceover file.
- Host is "Jason": charismatic, conversational, for smart retail investors.
  One short joke per episode, relevant to the point, then serious for the
  takeaway. Never joke about losing people's money or mock the viewer.
- The script ends with the next episode's question as a hook, and a spoken
  disclaimer: "this is education, not personal financial advice."
- Numbers in the script must be real and verified at build time (with sources
  recorded in `STATUS.md`). Illustrative examples must be labelled as examples
  on screen (e.g. "ILLUSTRATIVE EXAMPLE", "EXAMPLE — TYPICAL CARD RATE ~24%").

### Step 2 — Voiceover (`tts_epX.py` → `voice/*.mp3`)

- The TTS script splits `script-jason.txt` on the `[SEG n]` markers and
  synthesises one MP3 per segment.
- Voice: **Helio** (`avocado_v2:MAI_03`). Speed is set per segment for emotion
  — Ep2 used hook 110 (excited), history/numbers 92 (grave, slower for
  numbers), basket 100, time 98, close 104. Rough guide from the series:
  ~85–90 grave, ~110–115 excitement, ~100 default.
- `[pause]` markers in the script are passed through as-is: the TTS does not
  speak them (verified by test synth, 22 Nov 2026). Captions strip them
  separately.
- **The TTS command in these scripts is `/opt/hatch/bin/tts` — a tool that
  only exists on the Muse platform.** On any other machine the voiceover step
  must be replaced: either re-record the narration, or use another TTS voice
  and re-time everything (see §7).

### Step 3 — Sentence timing

- Sentence start times are **word-proportional estimates** computed from the
  segment MP3 durations (see `STARTS` / `SENT_STarts` in the render scripts),
  not measured word timestamps. Captions can therefore be off by a fraction of
  a second on long sentences. This is a known limitation, accepted for the
  whole series.
- Segment joins are **0.25 s silence beats** (`silence025.wav`), never an audio
  crossfade. (A half-second crossfade caused audible overlap/muffling in an
  earlier stock video — the PANW defect — so crossfades are banned.)

### Step 4 — The beat map (the manual part)

- Every sentence is mapped to one animation beat: a chart drawing itself, a
  counting number, objects appearing, a camera push/zoom/track. The map lives
  in the render script itself and in `STATUS.md` ("Sentence → animation map").
- **There is no stick figure anywhere in this series.** That was a deliberate
  decision (22 Nov 2026): an early version put a figure in every scene and it
  looked wrong. Figure beats were redesigned as camera movement over the
  object/animation itself — push-ins, tracking pans, zooms — the way the
  WhySector reference does it.
- Charts must match the reference treatment (§3): full-width glowing area
  chart, gradient fill, glowing head dot, number counting in sync. No vertical
  playhead/scrolling line.

### Step 5 — Frame rendering (`render_epX.py` → `*_v.mp4`)

- Pure Python + Pillow (PIL). Every frame is drawn programmatically:
  vector shapes, text, glows (layered translucent strokes), gradients.
- Output: silent video, 1920×1080, 30 fps, h264 (`*_v.mp4`).
- Render time is long: Ep1's rebuild took ~24 min for 9,170 frames on a
  shared 1.5-CPU VM; Ep4's took ~95 min while three episodes rendered in
  parallel. Do not parallelise heavy renders on a small VM, and note a VM
  restart kills a running render (it happened during Ep1's rebuild).
- Test frames first: `sweep_frames.py` renders sample frames across the
  timeline so layout defects are caught before the full render. Check pop-in
  beats at the **end** of the beat, not just the start — a chip-overlap defect
  in Ep4 was missed because the test frame predated the third chip popping in.

### Step 6 — Assembly (`assemble_epX.py` → final `.mp4`)

- ffmpeg joins the segment MP3s with the 0.25 s silence beats, burns in the
  captions from the `.ass` file, and applies loudness normalisation:
  **loudnorm I=-14 / TP=-1.5 / LRA=11**. Target: mean ≈ −16 dB, max peak below
  −1 dB. No crossfade anywhere.
- The finished file is named **exactly as the video title** — this is a hard
  rule for every upload.
- Captions: one event per sentence, burned in (ASS format, `*.ass`).

### Step 7 — Verification (before anything is uploaded)

Every finished video was checked and the numbers recorded in `STATUS.md`:

- `ffprobe`: duration, 1920×1080, 30 fps, h264 + AAC.
- `volumedetect`: mean loudness and max peak (loudnorm targets above).
- `silencedetect`: no silent stretch ≥ 1.0 s except a scripted `[pause]`.
- Join beats measure ≈ −91.0 dB (digital silence) with speech on both sides.
- Frames viewed across every section: captions present and matching, no
  figure/head/limb/humanoid shape in any frame, disclaimer on screen and
  spoken, charts match the reference treatment.
- The builder's own verdict plus honest gaps are in `STATUS.md` — read it,
  including the gaps, before reusing anything.

### Step 8 — Upload (YouTube Studio, browser)

- Upload as Unlisted first, with the exact title, `upload-description.txt` as
  the description, the tag list from `tags.txt` pasted into the **Tags field**,
  the custom thumbnail, "No, it's not Made for Kids", and added to the
  playlist.
- **Verify the Tags field in Studio after every upload** (re-open the Edit
  page and check the tags are actually there — an earlier stock video shipped
  with zero tags because the last tag sat uncommitted in the input box).
- End screens: Subscribe + the specific next episode, in the last 20 seconds.
- Pinned comment: posted only AFTER the video goes Public, then pinned.
- Public timing for Series 1 was all four at once, not staggered.

## 3. The style sheet (shared by all four episodes)

Defined in `render_pilot.py` (`R.*`), imported by every episode render script:

| Token | Value | Notes |
|-------|-------|-------|
| Canvas | 1920×1080, 30 fps | |
| BG | (8, 12, 22) — #080C16 | Dark navy, every scene |
| TEXT | (226, 232, 240) | Primary text |
| MUTED | (148, 163, 184) | Secondary text |
| RED | (242, 54, 69) | Falls, danger, "PANIC" |
| GREEN | (34, 197, 94) | Rises, "go" states |
| CYAN | (56, 189, 248) | Accents, links |
| AMBER | (245, 158, 11) | Warnings |
| GOLD | (252, 211, 77) | Highlights, stars |
| WHITE | (255, 255, 255) | |
| Font | DejaVu Sans / DejaVu Sans Bold | `/usr/share/fonts/truetype/dejavu/` |

- **Rule from the series (Shariq, 22 Nov 2026):** Manim draws *things*
  (physical objects — car, tyre, bed, cushion, jars, piggy bank — as clean
  geometric vector shapes); PIL draws *data* (charts, counting numbers, bars,
  captions, backgrounds/glows). In practice Episodes 1–4 ended up **PIL-only**:
  the PIL objects were already proven, and Manim would have added a visible
  seam for no gain. Manim was tested for a walking figure (10 s test clip,
  quality acceptable with fixes) and then dropped entirely when the figure
  was removed from the series.
- Charts: `area_chart` / `glow_line` / `glow_text` helpers, copied verbatim
  from the WhySector reference recreation (`render_recreation.py`). Full-width
  glowing line, gradient fill fading to the background, glowing head dot, big
  number counting in sync with the line.

## 4. Environment and dependencies

What the builders ran on (Muse cloud VM, 22 Nov 2026):

- **Python 3.12.3**, **Pillow 10.2.0**, **ffmpeg 8.1.2**
- Fonts: DejaVu Sans + DejaVu Sans Bold (system fonts, path above)
- TTS: `/opt/hatch/bin/tts speak --voice avocado_v2:MAI_03` (Muse-only)
- No LaTeX in the environment (so Manim's `DecimalNumber` does not work),
  no Manim needed for the final pipeline, no Playwright.
- **All paths in the code are hardcoded to `/home/hatch/...`.** To run
  elsewhere, the `BASE` / `sys.path.insert` lines at the top of each script
  must be changed to the new location. The `R.font()` helper also assumes the
  DejaVu paths above.

## 5. What is in the Drive package (Episode 2, as built)

```
jason-explains-ep2-code/
├── README.md                  ← this file
├── ep2-too-risky/
│   ├── script-jason.txt       ← 869-word narration script (5 segments)
│   ├── STATUS.md              ← verification numbers, sources, beat map, gaps
│   ├── upload-description.txt ← exact YouTube description (SEO + chapters)
│   ├── tags.txt               ← 15 tags for the Tags field
│   ├── pinned-comment.txt     ← comment posted after going Public
│   ├── voice/
│   │   ├── 00-hook.mp3  01-history.mp3  02-basket.mp3
│   │   └── 03-time.mp3  04-close.mp3   ← Helio voiceover segments
│   └── build/
│       ├── render_ep2.py      ← the episode renderer (PIL, per-sentence beats)
│       ├── assemble_ep2.py    ← ffmpeg assembly, captions, loudnorm
│       ├── tts_ep2.py         ← voiceover synthesis (Muse TTS)
│       ├── sweep_frames.py    ← test-frame sweep before full render
│       ├── ep2.ass            ← 91 caption events
│       ├── ep2.fc             ← ffmpeg concat list
│       ├── silence025.wav     ← 0.25 s silence beat between segments
│       ├── render_ep2.log / assemble_ep2.log / sweep.log
│       └── samples/           ← test frames from the verification sweep
└── shared/
    ├── render_pilot.py        ← style sheet, fonts, easing, chart + text
    │                            helpers (from whysector-pilot/build/)
    └── render_ep1.py          ← Episode 1 helpers reused by Ep2
                                 (from ep1-before-investing/build/)
```

**Not included (deliberately):** the rendered videos (`ep2_v.mp4` silent render
and the final 5:29 MP4 — the final video is live on YouTube), the thumbnail
(image, not code), `__pycache__`, and the full-frame verification dumps.
Everything needed to re-render the video from the script is in the package,
except the Muse-only TTS binary (§7).

**Why Episode 2:** its dependency chain is the shortest — it imports only
`render_pilot` and `render_ep1`. Episodes 3 and 4 additionally import
`render_v4`, and Episode 1's rebuild is generated by a patch script from the
v4 sources, so neither is as clean to lift as-is.

## 6. How to run Episode 2's code (as-is)

On a machine with Python 3 + Pillow + ffmpeg, after fixing the hardcoded
`/home/hatch/...` paths to the new location and placing `shared/` where the
`sys.path.insert` lines point:

```bash
# 1. Voiceover (only on the Muse platform — see §7)
python3 build/tts_ep2.py

# 2. Render every frame to silent video (slow — tens of minutes to hours)
python3 build/render_ep2.py

# 3. Assemble: voice + silence beats + captions + loudnorm → final MP4
python3 build/assemble_ep2.py
```

Then verify as in §2 Step 7 (ffprobe, volumedetect, silencedetect, view frames)
before uploading.

## 7. How to make a NEW episode from this code

1. Copy the Episode 2 folder. Write the new `script-jason.txt` (750–1,100
   words, `[SEG n]` markers, one joke, disclaimer, next-episode hook).
2. Record or synthesise the voiceover per segment. If not on the Muse
   platform, use another TTS voice or a human read, then re-derive the
   sentence start times from the new audio durations — the timing, captions
   and beats all hang off those durations.
3. Write the new render script: copy `render_ep2.py`, keep the shared helpers
   (`R.*` style, `area_chart` / `glow_line` / `glow_text`), and replace the
   sentence→animation map with beats for the new script. This is the real
   work — there is no automatic mapping from sentences to animations.
4. Sweep test frames, fix layout defects, render, assemble, verify (§2).
5. Upload per §2 Step 8.

## 8. Hard rules (do not break these)

- **No stick figure anywhere.** No figure/head/limb/humanoid shape in any
  frame, in any episode. (Decided 22 Nov 2026.)
- **Charts match the reference treatment.** Full-width glowing area chart,
  gradient fill, glowing head dot, number counting in sync. No vertical
  playhead line.
- **Loudnorm I=-14 / TP=-1.5 / LRA=11** on every final mix; verify mean and
  peak before delivery. **No audio crossfade** — 0.25 s silence beats only.
- **Uploaded file named exactly as the video title**, every time.
- **Verify the Tags field in Studio after every upload** (and the Tags line
  at the end of the description).
- No accompanying Shorts. No Singapore references, no specific broker or fund
  named, prices in USD, times in ET. Disclaimer spoken and on screen.
- Thumbnails for this series: the approved TTWO rich-illustrated style (same
  cartoon character — spiky brown hair, headset, teal shirt — sunset city
  skyline, coins, huge bold text, `JASON EXPLAINS` + `PART X OF 4` badges),
  NOT the flat-cartoon stock-video style and never realistic/3D.

## 9. Gotchas and lessons (paid for in full)

- **PIL `rounded_rectangle` crashes** when a pop-in-scaled rect is small
  relative to its fixed radius (`ValueError: y1 must be greater than or equal
  to y0`). Fix used: scale the radius with the pop-in
  (`radius=max(1, int(12*e))`).
- **Font size 0 crashes** when a pop-in starts exactly on a frame boundary
  (`font(int(140 * e))` with e=0). Fix used: clamp every pop-in-driven font
  size to `max(1, int(...))`.
- **Captions are estimates, not measured timestamps.** During a count-up the
  caption can read ahead of the number. Accepted for the series; do not
  promise word-perfect sync.
- **Manim needs LaTeX for numbers** (`DecimalNumber`) and LaTeX is absent
  here. Manim was tested for figures only and dropped with the figure.
- **The reference video's figures walk with articulated limbs** — the early
  style assessment wrongly said they didn't. PIL has no joints or rig; that is
  why figures were removed rather than drawn badly.
- **Verify pop-in beats at the end of the beat**, not the start (Ep4 chip
  overlap, §2 Step 5).
- **A VM restart kills a running render.** Long renders should be resumable
  or run where restarts don't interrupt them.
- **The `$10,000 → $9,000` sell-panel figures are illustrative**, from the
  reference recreation — labelled on screen, not a real portfolio.
- **YouTube's auto-title can drop parentheticals** (Ep3's "(Beginners)"
  was dropped from the filename and had to be corrected in Studio).

## 10. Lineage (how this code came to be)

- 19 Nov 2026: animation direction set — animate like Money, Modeled; Option A
  (30 fps PIL/matplotlib, ease-out) for every video, GSAP only for hero
  moments. Full-structure animated test approved.
- 21–22 Nov 2026: WhySector reference studied frame-by-frame; 90 s pilot built
  (cost ~2% of the weekly Muse budget); figure walk tested in Manim
  (acceptable with fixes).
- 22 Nov 2026: Jason Explains Series 1 commissioned. Ep1 built, then rebuilt
  after the figure was removed entirely and the chart rebuilt to the
  reference. Episodes 2–4 built in parallel from the same method. All four
  uploaded Unlisted, then flipped to Public together the same evening.
- The Macro Shock series this replaced is retired; its template and standing
  notes live under `~/workspace/youtube-pipeline/macro-shock/` and are not
  part of this pipeline.

## 11. Reference files (in the workspace, not in Drive)

- Series brief: `~/workspace/youtube-pipeline/jason-explains/SERIES-1-BRIEF.md`
- SEO package: `~/workspace/youtube-pipeline/jason-explains/SEO-SERIES-1.md`
- WhySector style assessment:
  `~/workspace/youtube-pipeline/seo-research/whysector-style-assessment.md`
- Money, Modeled assessment:
  `~/workspace/youtube-pipeline/seo-research/money-modeled-style-assessment.md`
- Reference recreation (chart code source):
  `~/workspace/youtube-pipeline/whysector-pilot/ref-recreation/`
