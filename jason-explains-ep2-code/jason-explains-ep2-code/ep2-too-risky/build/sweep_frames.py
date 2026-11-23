"""Sweep render_frame over the whole Ep2 timeline at 0.1 s steps, catching
any exception (e.g. zero-size fonts). Run: python3 sweep_frames.py"""
import sys
sys.path.insert(0, '.')
import render_ep2 as E

bad = []
t = 0.0
n = 0
while t <= 328.84:
    try:
        E.render_frame(t)
    except Exception as ex:
        bad.append((round(t, 2), type(ex).__name__, str(ex)))
        print('FAIL', round(t, 2), type(ex).__name__, ex, flush=True)
    n += 1
    t += 0.1
print('sweep done', n, 'frames, failures:', len(bad), flush=True)
for b in bad:
    print(b)
