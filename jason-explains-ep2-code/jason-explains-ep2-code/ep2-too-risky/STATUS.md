# Jason Explains Ep2 — "Is Investing in Stocks Too Risky for Beginners?"
**Status:** BUILT — full episode, ready for Unlisted upload (NOT uploaded).
**Date:** 22 Nov 2026. **File:** `Is Investing in Stocks Too Risky for Beginners?.mp4`
(5:28.84, 1920×1080, 30 fps, h264 + AAC).
**Build:** `build/render_ep2.py` (single PIL pass), `build/assemble_ep2.py`,
`build/ep2.ass` / `build/ep2.fc` / `build/ep2_v.mp4`, `build/tts_ep2.py`.
**Script:** `script-jason.txt` — read as-is, words NOT changed.
**Word count:** 889 spoken words (122 + 225 + 182 + 216 + 144 per segment;
899 incl. `[SEG n]` markers). 91 sentences, every sentence gets its own
animation (map below).

## Voiceover (measured, ffprobe)
| Seg | File | Speed | Words | Duration |
|---|---|---|---|---|
| 0 hook | 00-hook.mp3 | 110 (excited) | 122 | 47.184 s |
| 1 history | 01-history.mp3 | 92 (grave, slower for numbers) | 225 | 98.640 s |
| 2 basket | 02-basket.mp3 | 100 | 182 | 62.472 s |
| 3 time | 03-time.mp3 | 98 | 216 | 73.296 s |
| 4 close | 04-close.mp3 | 104 | 144 | 46.248 s |
| **Total speech** | | | **889** | **327.840 s** |
| + 4 × 0.25 s silence beats | | | | + 1.000 s |
| **Total video** | | | | **328.840 s = 5:28.84 — inside 5–7 min, no padding/cutting** |

- Voice: Helio (avocado_v2:MAI_03), same as Ep1. `[pause]` markers in the
  script: verified 22 Nov with a test synth that the TTS does NOT speak
  them aloud (2.328 s with the marker vs 2.400 s without — no extra word,
  no added pause), so the script text was passed through as-is, exactly
  like Ep1's `tts_ep1.py`. Captions strip `[pause]` (see below).
- SEG 4's first TTS call failed once with a transient transport error
  (`privsep transport failed / Broken pipe`); the retry succeeded
  immediately. The other four segments succeeded first time.

## ⚠️ DESCRIPTION MISMATCH — RESOLVED by parent decision (22 Nov)
`upload-description.txt` was the SEO Video 2 description **verbatim** as
instructed, including this line:

> "One stick figure holding one company — versus a whole basket of them."

**The video contains NO stick figure** (FIGURE REMOVED rule, Shariq 22 Nov).
That line described a visual that does not exist in the video.
**Parent decision (22 Nov):** use "One company on its own — versus a whole basket of them." in `upload-description.txt` instead. Applied — this is a one-phrase deviation from the SEO package (the master SEO file has been corrected too).
Two smaller inconsistencies, same decision:
- The description's `Tags:` line lists the 13 SEO tags (261 chars); `tags.txt`
  (and the intended YouTube Tags field) lists 15 tags (307 chars) — the two
  extra tags `investing in your 20s` / `investing in your 30s` were added to
  tags.txt per the task + SEO doc, but the description was kept verbatim.
  Recommend adding the two tags to the description Tags line too at upload
  so the description Tags line matches the Tags field (skill rule: paste the
  full tag list into the description).
- The SEO doc's Video 2/3/4 descriptions and brief still say "stick-figure
  style" in places; the video follows the newer FIGURE REMOVED rule instead.

## Verified numbers used (exactly as in the script; sources)
- S&P 500 average annual total return since 1928 ≈ **10% compounded
  (9.98% CAGR)** — Motley Fool "What Is the Average Stock Market Return?"
  / Damodaran NYU Stern dataset.
- **72 of 98 calendar years positive ≈ 73%** — Damodaran dataset via
  historyofmarket.com. (Script says "about 73%".)
- Best year **1954 +52.6%** (script: "nearly 53%"); worst year **1931
  −43.8%** (script: "almost 44%"); **2008 −37.0%** (−36.55%); **2022
  −18.1%** (not mentioned in the script) — Damodaran via pennycalc.com /
  historyofmarket.com.
- Average intra-year drop **14.2% (1980–2025)**, year ended higher in
  **35 of 46 years** — J.P. Morgan Guide to the Markets, data as of
  Sep 30, 2026.
- Every 20-year rolling window positive since 1926; worst **≈+2.4% a year
  (1929–48, Damodaran calc)** to **+3.1% (ending 1948, Morningstar/
  Ibbotson)**; best **≈+17.9% a year (ending 1999)** — Morningstar/Ibbotson
  SBBI, Crestmont Research, Motley Fool. (Script: "about 2 to 3% a year"
  worst, "almost 18% a year" best.)
- **2008:** S&P 500 fell **57% peak-to-trough (Oct 2007–Mar 2009)**,
  regained peak **Mar 2013, ~5.5 years** — walnutinvest.com / finviz /
  moomoo (S&P Dow Jones Indices).
- **2020:** S&P 500 fell **34% in 33 days (Feb–Mar 2020)**, new high
  **Aug 2020, ~5 months** — same sources. (Script: "about a month".)
- **1 of 500 = 0.2%** — arithmetic, labelled "SIMPLE ARITHMETIC — 1 ÷ 500"
  on screen.

## Deliberate visual simplifications (labelled on screen)
- The 1931/2008/1954 bars, the long-run +10% area chart, the 2008/2020
  recovery charts and the scattered year bars are **stylised shapes, not
  plotted data** — labelled "STYLISED TREND / STYLISED CHART" or
  "ILLUSTRATIVE SPREAD, NOT YEAR-BY-YEAR DATA" on screen. Only the
  numbers on them are the verified figures above.
- The 46-squares visual (35 green up / 11 red down) is a **count**, not a
  time series — labelled "EACH SQUARE = ONE YEAR"; the squares are not in
  year order, so no invented year-by-year sequence is implied.
- The 0.2% pie wedge is drawn as a 15° slice so it is visible; a true
  0.2% wedge (0.72°) would be invisible. The number shown is exact.
- The "ONE STOCK ▼ −50%" card visualises the script's own example
  ("lost half their savings on one stock") — it is the sentence's content,
  not a real portfolio.
- The rollercoaster, eggs, basket, racecourse, clock and tickets are
  illustrative props for the script's own analogies, not data.

## Manim vs PIL — PIL for every shot (no Manim at all)
Same call as the approved v4 clip. Every Ep2 object (eggs, basket,
rollercoaster track + empty cart, clock, tickets, racecourse oval, dials,
bars, pie) is simple geometric flat-vector art that PIL draws cleanly;
the PIL equivalents are proven (v4's cushion/car/tyre, the recreation's
`area_chart` / `glow_line` / `glow_text`). Manim would add a render seam
with no visible gain, and Manim draws THINGS only (never a figure) per
the brief — so there is no Manim shot in this build: no Manim scenes, no
figure rig, no figure code of any kind, so no figure can appear.

| Shot group | Technique | Why |
|---|---|---|
| Hook headlines / cards / thought bubble / question cards | PIL | Text + cards; no object Manim would improve |
| Year bars (−44% / −37% / +53%), 46-squares count, ticket, scattered bars | PIL | Bars/counts are DATA — PIL per the brief |
| Long-run +10% area chart, dip chart, 2008/2020 recovery charts | PIL | Reference treatment, copied `area_chart`/`glow_line`/`glow_text` from the recreation via v4 |
| Rollercoaster track + empty cart (the joke) | PIL | Track is a polyline + circle; cart is a rotated rounded-rect sprite — simple geometry, no Manim gain |
| One-company card, basket + dots, pie slice, eggs, scale, horse ticket, racecourse oval | PIL | Simple geometric objects; PIL equivalents already exist |
| Clock, 73% donut, 20-year timeline, risk bars, odds dial, disclaimer/answer/Part 3 cards | PIL | Dials/bars/cards are DATA — PIL per the brief |

## Sentence → animation map (91 sentences; times are local segment times)
### SEG 0 hook — "WHY IT FEELS SO SCARY" (0.00–47.18)
| # | Time | Sentence | Animation |
|---|---|---|---|
| 1 | 0.00–3.87 | "So, you're thinking about investing in stocks — and honestly?" | Red headline cards flash in one by one ("MARKET CRASHES" / "STOCKS PLUNGE" / "SAVINGS WIPED OUT"); "HONESTLY?" pops |
| 2 | 3.87–5.03 | "It feels scary." | Big pulsing red "SCARY." + red edge flash |
| 3 | 5.03–6.57 | "Every headline is red." | Three red headline bars fill in |
| 4 | 6.57–11.22 | "Somebody on the internet just lost half their savings on one stock." | Phone post card ("lost HALF my savings on ONE stock"); "ONE STOCK ▼ −50%" card drops in |
| 5 | 11.22–16.24 | "And your brain is doing the maths: what if that happens to me?" | Thought bubble "WHAT IF THAT HAPPENS TO ME?"; camera pushes in |
| 6 | 16.24–21.27 | "Here's the thing nobody tells you: you're not wrong to feel that way." | Green ✓ + "YOU'RE NOT WRONG TO FEEL THAT WAY" |
| 7 | 21.27–22.43 | "Stocks ARE risky." | Big red "RISKY." stamp |
| 8 | 22.43–27.07 | "The question is — risky for who, and risky for how long?" | Two cards pop: "RISKY FOR WHO?" / "RISKY FOR HOW LONG?" |
| 9 | 27.07–30.94 | "Because the answer changes completely depending on those two things." | The two cards alternate glow; "THE ANSWER CHANGES COMPLETELY" |
| 10 | 30.94–35.97 | "And by the end of this video, you'll know exactly where you stand." | Dotted path draws; flag + "YOU'LL KNOW WHERE YOU STAND" |
| 11 | 35.97–40.61 | "Oh — and if you missed part one, go watch it first." | "MISSED PART ONE? GO WATCH IT FIRST" card + "PART 1 OF 4" |
| 12 | 40.61–45.64 | "We covered the three things to do before you touch a single stock." | Three chips pop: EMERGENCY FUND / DEBT PLAN / SIMPLE BUDGET |
| 13 | 45.64–47.18 | "This is part two." | "PART 2 OF 4 — TOO RISKY?" |

### SEG 1 history — "SHORT-TERM RISK vs LONG-TERM HISTORY" (47.43–146.07)
| # | Time | Sentence | Animation |
|---|---|---|---|
| 1 | 0.00–3.95 | "Let's start with the scary part, because it's real." | Red card "THE SCARY PART IS REAL" |
| 2 | 3.95–8.33 | "In a single year, the stock market can be brutal." | Red year bars start dropping in |
| 3 | 8.33–13.15 | "The worst year on record, 1931, the market fell almost 44%." | Giant red bar, "−44%" counts up, "1931" |
| 4 | 13.15–15.34 | "In 2008, it fell 37%." | Second red bar, "−37%" counts up, "2008" |
| 5 | 15.34–24.55 | "And even in a totally normal year, the market drops about 14% at some point — on average, every single year." | Reference-style red area chart dips −14% then recovers; "DROPS ~14% AT SOME POINT" |
| 6 | 24.55–26.30 | "Wait — what?" | Big "WAIT — WHAT?" |
| 7 | 26.30–26.74 | "Yes." | Green "YES." stamp |
| 8 | 26.74–37.70 | "Since 1980, the market has fallen 14% inside the year, on average — and still ended the year higher in 35 out of 46 years." | 46 squares fill in (35 green ▲ / 11 red ▼, count visual); "35 OF 46 YEARS UP" |
| 9 | 37.70–41.21 | "That's the first surprise: the drops are normal." | "SURPRISE #1: THE DROPS ARE NORMAL" card |
| 10 | 41.21–46.03 | "They're the price of admission, not a sign that something's broken." | Ticket stub "PRICE OF ADMISSION" + green ✓ "NOT A SIGN SOMETHING'S BROKEN" |
| 11 | 46.03–48.22 | "Now here's the second surprise." | "SURPRISE #2" card |
| 12 | 48.22–51.29 | "Stretch it out, and the picture flips." | Red short chart flips to the green long chart |
| 13 | 51.29–60.50 | "Since 1928 — that's almost a hundred years — the stock market has averaged about 10% a year, with dividends reinvested." | Full-width glowing green area chart draws (reference treatment); "+10% A YEAR (AVG)" counts up; "SINCE 1928" |
| 14 | 60.50–66.64 | "Through wars, recessions, crashes, pandemics — all of it — about 10% a year." | Event pills pop along the chart (WAR / RECESSION / CRASH / PANDEMIC); line keeps rising |
| 15 | 66.64–74.09 | "But — and this is the important bit — almost no single year actually gives you 10%." | Scattered year bars above/below a dashed "+10% AVG" line; "ALMOST NO YEAR LANDS ON THE LINE" |
| 16 | 74.09–78.04 | "The best year ever was 1954: up nearly 53%." | Giant green bar, "+53%" counts up, "1954" |
| 17 | 78.04–80.67 | "The worst was 1931: down 44%." | Green +53% bar stays; red −44% bar drops in beside it |
| 18 | 80.67–87.24 | "Saying stocks return 10% a year is like saying the average rollercoaster is 10% scary." | Rollercoaster track + empty cart rides up the lift hill into the loop; ""10% SCARY?"" pill (the joke) |
| 19 | 87.24–91.19 | "Technically true — completely useless when you're upside down." | Cart upside down at the top of the loop; "COMPLETELY USELESS UPSIDE DOWN" |
| 20 | 91.19–96.89 | "So the average is real, but you never actually experience the average." | Scattered bars again; one bar circled; "YOU NEVER EXPERIENCE THE AVERAGE" |
| 21 | 96.89–98.64 | "You experience the ride." | Cart speeds along the track; "THE RIDE." |

### SEG 2 basket — "ONE COMPANY vs HUNDREDS — INDEX FUNDS" (146.32–208.80)
| # | Time | Sentence | Animation |
|---|---|---|---|
| 1 | 0.00–4.46 | "Now, part two of the fear: what if I pick the wrong one?" | "PART TWO OF THE FEAR" + "WHAT IF I PICK THE WRONG ONE?" card |
| 2 | 4.46–12.01 | "Fair question — because if you put all your money in ONE company, and that company goes bust, you can lose everything." | "ONE COMPANY $$$ " card; money piles in, card cracks and falls; "GOES BUST — YOU CAN LOSE EVERYTHING" |
| 3 | 12.01–13.04 | "It has happened." | "IT HAS HAPPENED." |
| 4 | 13.04–14.07 | "Big names, gone." | Three company cards fade out, each ✕-stamped; "GONE." |
| 5 | 14.07–16.13 | "That is not a small risk." | "THAT IS NOT A SMALL RISK." |
| 6 | 16.13–17.85 | "That is a huge risk." | Big red "HUGE RISK." |
| 7 | 17.85–21.97 | "But here's the trick — you don't have to buy one company." | The one card splits into 12 small cards; "YOU DON'T HAVE TO BUY ONE" |
| 8 | 21.97–25.06 | "An index fund buys hundreds of them at once." | Basket fills with dots; "HUNDREDS OF COMPANIES — IN ONE BASKET" |
| 9 | 25.06–30.21 | "The S&P 500 is 500 of the biggest companies in America, all in one basket." | "500" counts up over the basket; "S&P 500 — 500 OF THE BIGGEST COMPANIES IN AMERICA" |
| 10 | 30.21–34.33 | "Buy the index, and you own a tiny slice of all 500." | Pie of 500 slices; one gold slice highlights; "YOUR SLICE × 500" |
| 11 | 34.33–36.38 | "So if one company goes bust?" | One slice turns red and cracks (✕) |
| 12 | 36.38–40.16 | "That's one out of 500 — about 0.2% of your money." | Big "1 OF 500 = 0.2%" + "SIMPLE ARITHMETIC — 1 ÷ 500" |
| 13 | 40.16–40.85 | "It stings." | "IT STINGS. OUCH" |
| 14 | 40.85–42.22 | "It doesn't sink you." | Basket stays afloat, one red dot among blue; green ✓ "IT DOESN'T SINK YOU" |
| 15 | 42.22–44.28 | "Think of it like eggs." | One egg + basket of eggs; "THINK OF IT LIKE EGGS" |
| 16 | 44.28–46.34 | "One egg, dropped — breakfast ruined." | Egg drops and cracks, yolk splat; "BREAKFAST RUINED" |
| 17 | 46.34–50.46 | "A basket of 500 eggs, one breaks — you still have breakfast." | Basket of 40 eggs, one cracked red; camera pushes in; "ONE BREAKS — YOU STILL HAVE BREAKFAST" |
| 18 | 50.46–51.14 | "Same money." | Balance scale: "1 EGG" vs "500 EGGS"; "SAME MONEY." |
| 19 | 51.14–52.17 | "Completely different risk." | "COMPLETELY DIFFERENT RISK." |
| 20 | 52.17–56.98 | "That's the whole idea of an index fund: you're not betting on one horse." | Betting slip "ONE HORSE", red ✕ stamps it |
| 21 | 56.98–59.04 | "You're betting on the whole racecourse." | Oval racecourse, 8 gold dots running around it |
| 22 | 59.04–62.47 | "And the racecourse has been running for a hundred years." | Track keeps running; "RUNNING FOR 100 YEARS / 1928 ———— TODAY" |

### SEG 3 time — "HOW TIME IN THE MARKET CHANGES THE RISK" (209.05–282.34)
| # | Time | Sentence | Animation |
|---|---|---|---|
| 1 | 0.00–3.05 | "And then there's the biggest lever of all: time." | Big clock, hands spinning; "THE BIGGEST LEVER OF ALL: TIME" |
| 2 | 3.05–6.45 | "Here's the number that changed how I think about risk." | Gold card "THE NUMBER THAT CHANGED EVERYTHING" |
| 3 | 6.45–10.86 | "In any single year, the market goes up about 73% of the time." | Donut fills to 73%; "73%" counts up; "OF YEARS GO UP" |
| 4 | 10.86–13.57 | "Roughly three years out of four, you win." | Four year blocks: 3 green ✓, 1 red ✕; "YOU WIN" |
| 5 | 13.57–23.75 | "But stretch your holding period to 20 years — and in almost a hundred years of records, there has never been a single 20-year stretch where the market lost money." | Timeline 1926→today; "20 YEARS" window slides along it, green ticks accumulate; "NEVER A SINGLE 20-YEAR STRETCH THAT LOST MONEY" |
| 6 | 23.75–24.43 | "Not one." | Big green "NOT ONE." |
| 7 | 24.43–28.50 | "The worst 20-year stretch still made about 2 to 3% a year." | Small green bar; "+3.0% / YEAR" counts; "STILL MADE ABOUT 2–3% A YEAR" |
| 8 | 28.50–30.88 | "The best made almost 18% a year." | Tall green bar beside the small one; "+18% / YEAR"; "BEST ~18%" |
| 9 | 30.88–34.61 | "Now — that does not mean the wait is comfortable." | Wobbling amber clock; "THE WAIT IS NOT COMFORTABLE" |
| 10 | 34.61–43.43 | "After the 2008 crash, the market fell 57% — and it took about five and a half years just to get back to where it started." | Reference-style red area chart: peak → −57% trough → slow climb back; "−57%" in sync; "OCT 2007 PEAK / MAR 2009 −57% / MAR 2013"; "~5.5 YEARS TO GET BACK TO THE PEAK" |
| 11 | 43.43–51.58 | "After the COVID crash in 2020, it fell 34% in about a month — and it was back at new highs in five months." | Red area chart: fast −34% dip, fast V recovery; "−34%" in sync; "FEB 2020 / −34% IN ~A MONTH / AUG 2020"; "BACK AT NEW HIGHS IN ~5 MONTHS" |
| 12 | 51.58–52.26 | "Same market." | Both crash shapes side by side, mini; "2008: −57% · 5.5 YEARS" / "2020: −34% · 5 MONTHS" |
| 13 | 52.26–53.95 | "One wait was five months." | Green card "ONE WAIT WAS FIVE MONTHS" |
| 14 | 53.95–55.65 | "The other was five years." | Amber card "THE OTHER WAS FIVE YEARS" |
| 15 | 55.65–58.03 | "You can't know which one you're getting." | "YOU CAN'T KNOW WHICH ONE YOU'RE GETTING." + big "?" |
| 16 | 58.03–59.72 | "That's the real risk." | Red card "THAT'S THE REAL RISK." |
| 17 | 59.72–63.79 | "Not that the market never recovers — it always has, so far." | Green area chart rises; "IT ALWAYS HAS — SO FAR" |
| 18 | 63.79–67.53 | "The risk is that you need the money before it does." | Green chart + red card "YOU NEED THE MONEY BEFORE IT DOES" |
| 19 | 67.53–73.30 | "So the question isn't really 'are stocks risky?' The question is 'when do I need this money?'" | Gold card "WHEN DO I NEED THIS MONEY?"; camera pushes in; "THAT'S THE REAL QUESTION" |

### SEG 4 close — "SO — IS IT TOO RISKY FOR YOU?" (282.59–328.84)
| # | Time | Sentence | Animation |
|---|---|---|---|
| 1 | 0.00–3.21 | "So — is investing in stocks too risky for beginners?" | Red card "IS INVESTING IN STOCKS TOO RISKY? FOR BEGINNERS" |
| 2 | 3.21–4.50 | "Here's my honest answer." | "HERE'S MY HONEST ANSWER." |
| 3 | 4.50–10.28 | "If you need this money next year — for rent, for a deposit, for an emergency — yes." | Chips pop: RENT / DEPOSIT / EMERGENCY; big red "YES." |
| 4 | 10.28–10.92 | "Too risky." | "TOO RISKY." |
| 5 | 10.92–12.53 | "Don't put it in stocks." | Red card "DON'T PUT IT IN STOCKS." + ✕ |
| 6 | 12.53–22.16 | "But if this is money you can leave alone for ten, twenty years — and you own the whole basket, not one company — then history says something very different." | Timeline NOW → 10 YEARS → 20 YEARS + basket; "HISTORY SAYS SOMETHING VERY DIFFERENT" |
| 7 | 22.16–23.45 | "The risk doesn't disappear." | Red risk bar stays full; "STILL THERE" |
| 8 | 23.45–24.09 | "It shrinks." | Same bar shrinks to ~15%, green; "IT SHRINKS." |
| 9 | 24.09–26.98 | "Year by year, the odds tilt in your favour." | Odds dial fills green year by year; "% IN YOUR FAVOUR" |
| 10 | 26.98–30.51 | "And remember — this is education, not personal financial advice." | Gold disclaimer card on screen: "THIS IS EDUCATION, NOT PERSONAL FINANCIAL ADVICE" (also spoken) |
| 11 | 30.51–35.97 | "Your situation is your own, so if you're unsure, talk to a licensed adviser in your country." | Cyan card "TALK TO A LICENSED ADVISER" |
| 12 | 35.97–39.18 | "Next up — the part you've been waiting for." | "NEXT UP — THE PART YOU'VE BEEN WAITING FOR." |
| 13 | 39.18–40.79 | "How do you actually start?" | Green card "HOW DO YOU ACTUALLY START?" |
| 14 | 40.79–42.72 | "Which button do you press first?" | Big pulsing green "START" button + "?" |
| 15 | 42.72–45.28 | "That's part three, and it's the simple one." | "THAT'S PART THREE AND IT'S THE SIMPLE ONE" |
| 16 | 45.28–46.25 | "See you there." | "SEE YOU THERE. / PART 3 OF 4 · HOW TO START INVESTING" |

## Explicit no-figure check (how it was checked)
1. **By construction:** `grep -niE "stick|figure|runner|draw_runner|gait|walk|hero|limb|torso|knee|ankle|manim|person|human" build/render_ep2.py`
   returns only: the docstring ("NO stick figure", "PIL vs Manim", "no figure
   can appear"), the word "figures" in "VERIFIED figures" (numbers), the
   comment "No figure inside — the cart is empty", and "PERSONAL FINANCIAL
   ADVICE" (the disclaimer text). There is no figure-drawing code anywhere
   — no limbs, no rig, no walk/run cycle, no Manim import. Nothing in the
   code can draw a figure.
2. **By viewing:** [N] frames extracted from the assembled clip across the
   whole 328.84 s (every section, at least one frame per sentence group —
   see `verify/`), all viewed. No stick figure, head-circle, limb, or
   humanoid shape appears in any viewed frame. The closest human-adjacent
   shapes are none — the closest are the egg, the basket, the cart and the
   clock. The thought bubble in the hook is an empty ellipse (no head
   inside it); the rollercoaster cart is empty.
3. **Pre-render samples:** 34 sample frames rendered and viewed before the
   full render (`build/samples/`), plus 9 re-rendered after fixes — see
   "Defects found in samples and fixed" below.

## Chart vs reference (side-by-side)
Compared the Ep2 chart frames against the recreation's frames in
`whysector-pilot/ref-recreation/verify/`:
- Same: full-width glowing line (glow 12 / core 4, blur 9); gradient fill
  fading to BG with no hard edge; glowing head dot (outer ring derived
  from the line colour, v4 fix kept); big glowing number counting in sync
  with the chart where the script has numbers (+10%, −57%, −34%, 73%).
- The Ep2 charts use the same `area_chart` / `glow_line` / `glow_text`
  code copied from the recreation via v4 (same widths, same eased draw).
- Deliberate difference: Ep2's chart point sets are stylised shapes
  (LONG_PTS / CRASH08_PTS / CRASH20_PTS / RED_PTS), not the recreation's
  portfolio points — the script's numbers are historical aggregates, not
  a portfolio value, so no portfolio panel was built.

## Defects found in pre-render samples and fixed (before the full render)
1. **"ONE STOCK ▼ −50%" text overflowed its card (9 s).** Card widened
   760–1160 → 700–1220, font 40 → 34. Verified in re-rendered `s0009.00`.
2. **Section header clipped by zooms (13.5 s bubble, 132/136 s coaster,
   197 s egg).** Zoom centres moved from (960,600/640/700) to (960,540)
   (bubble/coaster) and (960,560) (egg), scales ≤1.06. Verified in
   re-rendered `s0013.50`, `s0132.00`, `s0136.00`, `s0197.00` — header
   fully visible in all four.
3. **Rollercoaster track disconnected from the loop (132 s).** The lift
   hill ended at (780,600), 50 px below the loop's left point (790,550).
   Lift hill now ends exactly at (790,550), and an exit line was added
   from the loop's right side (1130,550) down to (1840,800) in all three
   coaster beats. Verified in re-rendered `s0132.00`.
4. **Basket weave lines stuck out past the slanted sides (176 s, 194 s).**
   `_basket` now computes the trapezoid half-width at each weave line.
   Verified in re-rendered `s0194.00`.
5. **"1 EGG" / "500 EGGS" labels collided with "SAME MONEY." (197 s).**
   Scale moved up (beam y 300, labels y 410), big text moved to y 560.
   Verified in re-rendered `s0197.00`.
6. **"OF YEARS GO UP" crossed the 73% donut's green arc (218 s).** Label
   moved below the donut (y 680 → 830). Verified in re-rendered `s0218.00`.
7. **20-year timeline beat was sparse (228 s).** Green ticks now
   accumulate along the timeline behind the sliding window, and the end
   line appears at 5.0 s instead of 6.0 s. Verified in re-rendered
   `s0228.00`.
8. **Big bar numbers wider than their bars (60 s).** Single bars widened
   760–1160 → 720–1200 (1931, 1954, worst-20y bars). Verified in
   re-rendered `s0060.00`.

## Defects found in the first full render and fixed (re-rendered 22 Nov)
9. **Scattered year bars painted over the headline and subtitle
   (120 s, 142 s).** In SEG 1 beats 15 and 20 the tallest green bars
   rose to y≈185, covering parts of "BUT ALMOST NO SINGLE YEAR GIVES
   YOU 10%", the "ILLUSTRATIVE SPREAD, NOT YEAR-BY-YEAR DATA"
   subtitle and "THE AVERAGE IS REAL —". Bar height scale 300 → 200
   in `render_ep2.py` (lines 702–703, 787–788); tallest bar now tops
   at y≈280, clear of the text. Verified in the final file:
   `verify/frames/final_f120.png`, `verify/frames/final_f142.png`.
10. **Render crashed at frame ~4200+ (22 Nov, first render).**
    `ValueError: font size must be greater than 0` — `pop_in` returned
    exactly 0.0 for frames before a pop's start (beat 21, "THE RIDE.",
    whose pop starts 0.4 s inside its beat), and a float-accumulation
    edge (t = 2.8000000000000003, "HONESTLY?") gave an ease of ~3e-15,
    still size 0. Fix: `pop_in` now floors its return at 0.05 (~2 px
    glyph, invisible on pre-pop frames). A sweep of `render_frame`
    over the whole timeline at 0.1 s steps (`build/sweep_frames.py`)
    then passed: 3289 frames, 0 failures.
11. **Glow blur speed.** The first render ran 0.5 fps through the
    chart beats (full-frame GaussianBlur in `glow_line`/`glow_text`).
    Both now blur a crop around the line/text (80 px padding, >> 3×
    the blur radius) — visually identical, ~5× faster on chart frames
    (2.57 → 0.49 s/frame at t=105). Verified by eye on re-rendered
    `s0105.00` / `s0250.00` (glow, gradient, head dot unchanged).
    Note: a runtime service restart killed one re-render mid-run at
    frame 2400; it was restarted from scratch and completed.

## Verification (final assembly, measured 22 Nov 2026)
- ffprobe: duration 328.833 s (5:28.83), 1920×1080, 30 fps, h264 +
  AAC, 16,481,452 bytes.
- Loudness (volumedetect): mean −16.8 dB, max peak −1.3 dB (target
  ~−16 dB mean, peak below −1 dB).
- Silence (silencedetect −50 dB, ≥1.0 s): exactly one stretch —
  71.809–72.961 s (1.152 s), the scripted `[pause]` before
  "Wait — what?", present in the source TTS
  (`voice/01-history.mp3`, 24.264–25.538 s local). No other silence
  ≥1.0 s in the file.
- Join beats (4 joins, windows at 47.0/47.5, 146.0/146.4, 208.8/209.2,
  282.3/282.7 s): pre-join means −67.3 / −69.7 / −91.0 / −70.4 dB
  (near-silence beats), post-join means −16.0 / −13.7 / −13.1 /
  −13.9 dB — speech present on both sides of every join.
- Captions: 91 events, `[pause]` stripped (asserted in assemble_ep2.py —
  the build fails if any caption still contains `[pause]`); every viewed
  frame has its caption present and matching. Captions are
  word-proportional sentence estimates, not measured word timestamps
  (same method as Ep1/v4).
- Disclaimer: spoken in SEG 4 sentence 10 AND on screen as a gold card
  (verified in `verify/frames/f310.png` at t=310 s).
- Chapters (real section starts): 0:00 / 0:47 / 2:26 / 3:29 / 4:43.
- Frames viewed from the final file: 23 across all 5 sections
  (`verify/frames/f002`–`f327`, incl. f222/f224/f142/f236), plus 3
  re-checks of the fixed beats (`final_f105`/`final_f120`/`final_f142`).
  No figure/head/limb/humanoid shape in any viewed frame; code grep
  also clean (see "No-figure check" above).
- Render time: 2073.8 s for the final re-render (9865 frames); the
  pre-fix render took 1948.5 s.

## Caveats (honest)
- Captions are word-proportional sentence estimates, not measured word
  timestamps (same method as Ep1 and the pilot).
- The 46-squares beat fills in over ~6 s; early frames show only a few
  squares (by design — they appear one by one).
- The "BACK AT NEW HIGHS IN ~5 MONTHS" line pops in over 0.4 s, so a
  frame caught in the first 0.05 s of the pop shows it tiny — in motion
  it reads full-size.
- The rollercoaster cart is an empty red outline cart; the loop is a
  simple circle, not a banked track. The joke lands on the words + the
  upside-down cart, not on track realism.
- Beat 5 of SEG 1 (the ~14% dip chart) and beat 12 (short→long flip) are
  stylised area shapes; the dip depth is illustrative, the −14% figure
  itself is the verified J.P. Morgan number.
- The "SAME MARKET" beat (SEG 3 #12) draws two mini crash shapes as
  plain red polylines (no glow/gradient) — deliberately simple, they are
  a comparison glyph, not charts.
- The 20-year "worst +2–3%" bar counts up to +3.0% (the top of the
  script's "2 to 3%" range); the on-screen label says "ABOUT 2–3% A YEAR".

## What Shariq needs to decide
1. **Description line:** RESOLVED 22 Nov — parent decided: "One company on its own — versus a whole basket of them." Applied to upload-description.txt; one-phrase deviation from the SEO package, recorded in the mismatch box above.
2. **Description Tags line:** add "investing in your 20s" and "investing
   in your 30s" so it matches tags.txt / the Tags field, or leave verbatim?
3. Approve the video for Unlisted upload. (Thumbnail is DONE — thumbnail.jpg in this folder, TTWO style, same character, "TOO RISKY?", JASON EXPLAINS + PART 2 OF 4 badges, 1280×720, verified by viewing against the TTWO reference. It was built as a separate task, not by the video builder.)
