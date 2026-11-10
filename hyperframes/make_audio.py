#!/usr/bin/env python3
"""Procedural 15 s club-teaser audio bed for The Break Lounge (120 BPM, F minor).

Fully synthesised with numpy -- no sampled or licensed material.
    python3 -I make_audio.py out.wav
"""
import sys, wave
import numpy as np

SR = 48_000
DUR = 15.0
N = int(SR * DUR)
BEAT = 0.5  # 120 BPM
rng = np.random.default_rng(20261110)

low = np.zeros(N)           # mono low bus: kick, sub, drone, impacts
airL = np.zeros(N)          # stereo air bus: hats, whooshes, risers
airR = np.zeros(N)


def add(buf, t0, sig, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf):
        return
    if i < 0:
        sig, i = sig[-i:], 0
    n = min(len(sig), len(buf) - i)
    buf[i:i + n] += sig[:n] * gain


def sweep_phase(freqs):
    return 2 * np.pi * np.cumsum(freqs) / SR


def kick(amp=1.0, dur=0.42, click=0.32, f_top=165.0, f_end=47.0, tau=0.028, body=0.115):
    n = int(dur * SR); t = np.arange(n) / SR
    f = f_end + (f_top - f_end) * np.exp(-t / tau)
    sig = np.sin(sweep_phase(f)) * np.exp(-t / body)
    sig += rng.standard_normal(n) * np.exp(-t / 0.0035) * click
    return np.tanh(sig * 1.25) * amp


def hat(amp=0.2, dur=0.07, decay=0.013):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    x = np.diff(np.concatenate(([0.0], x)))          # crude high-pass
    x = np.diff(np.concatenate(([0.0], x)))
    return x * np.exp(-t / decay) * amp


def sub(freq, dur, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    e = np.minimum(1.0, t / 0.015) * np.exp(-t / (dur * 0.6))
    return (np.sin(2 * np.pi * freq * t) + 0.22 * np.sin(4 * np.pi * freq * t)) * e * amp


def drone(dur, freq=43.65, amp=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    lfo = 0.82 + 0.18 * np.sin(2 * np.pi * 0.19 * t)
    x = (0.62 * np.sin(2 * np.pi * freq * t)
         + 0.26 * np.sin(2 * np.pi * freq * 2 * t + 0.4)
         + 0.11 * np.sin(2 * np.pi * freq * 3 * t + 1.1)
         + 0.07 * np.sin(2 * np.pi * freq * 4.98 * t + 2.2))
    return x * lfo * amp


def riser(dur, amp=1.0, f0=170.0, f1=2900.0, shape=2.1):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    f = f0 * np.exp(p * np.log(f1 / f0))
    tone = np.sin(sweep_phase(f))
    noise = rng.standard_normal(n)
    noise = np.diff(np.concatenate(([0.0], noise)))
    trem = 0.75 + 0.25 * np.sin(2 * np.pi * (4 + 16 * p) * t)
    return (tone * 0.55 + noise * 0.45) * (p ** shape) * trem * amp


def whoosh(dur, amp=1.0, reverse=False, f0=350.0, f1=3200.0):
    n = int(dur * SR); t = np.arange(n) / SR; p = t / dur
    q = (1 - p) if reverse else p
    f = f0 + (f1 - f0) * q
    noise = rng.standard_normal(n)
    noise = np.diff(np.concatenate(([0.0], noise)))
    sig = noise * 0.6 + np.sin(sweep_phase(f)) * 0.22
    return sig * (np.sin(np.pi * p) ** 1.5) * amp


def impact(amp=1.0, dur=1.8):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 36 + 110 * np.exp(-t / 0.045)
    sig = np.sin(sweep_phase(f)) * np.exp(-t / 0.5)
    sig += np.sin(2 * np.pi * 73 * t) * np.exp(-t / 0.22) * 0.35
    sig += rng.standard_normal(n) * np.exp(-t / 0.05) * 0.28
    return np.tanh(sig * 1.15) * amp


def shimmer(dur, amp=1.0, base=698.46):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.zeros(n)
    for k, g in ((1, 1.0), (1.5, .55), (2, .4), (3, .25), (4.02, .16)):
        x += np.sin(2 * np.pi * base * k * t + k) * g
    return x * np.exp(-t / (dur * 0.42)) * amp


# ----------------------------------------------------------------- arrangement
# low drone, rising through the sections
add(low, 0.0, drone(6.2, amp=0.17))
add(low, 6.0, drone(3.8, amp=0.26))
add(low, 9.5, drone(3.0, amp=0.36))
add(low, 12.0, drone(3.0, amp=0.30))

# --- section A : muted "leak" pulse (0 - 6) ---------------------------------
for i in range(12):
    t = i * BEAT
    if t >= 6.0:
        break
    strong = (i % 2 == 0)
    add(low, t, kick(amp=0.46 if strong else 0.2, click=0.05, f_top=120, body=0.08))
for i in range(6):
    add(low, 1.0 + i * 1.0, sub(43.65, 0.55, amp=0.28))
# ticking "transmission" texture
for i in range(24):
    t = 0.25 + i * 0.25
    if t >= 6.0:
        break
    h = hat(amp=0.055 if i % 2 else 0.085, dur=0.04, decay=0.006)
    add(airL, t, h, 1.0 if i % 2 else 0.75)
    add(airR, t + 0.004, h, 0.75 if i % 2 else 1.0)

# --- section B : the beat lands (6 - 9.5) -----------------------------------
NOTES = [43.65, 43.65, 51.91, 43.65, 58.27, 43.65, 51.91, 65.41]
i = 0
t = 6.0
while t < 9.5:
    add(low, t, kick(amp=0.95))
    add(low, t, sub(NOTES[i % len(NOTES)], 0.46, amp=0.5))
    i += 1
    t += BEAT
t = 6.25
while t < 9.5:
    h = hat(amp=0.17)
    add(airL, t, h, 1.0); add(airR, t + 0.005, h, 0.7)
    t += BEAT

# --- drop : logo reveal (9.5 - 12) ------------------------------------------
add(low, 8.42, impact(amp=0.0))   # keeps rng stream stable if retuned
add(airL, 8.35, riser(1.15, amp=0.42), 1.0)
add(airR, 8.35, riser(1.15, amp=0.42), 1.0)
add(low, 9.5, impact(amp=0.95))
i = 0
t = 9.5
while t < 12.0:
    add(low, t, kick(amp=1.0))
    add(low, t, sub(NOTES[i % len(NOTES)], 0.46, amp=0.58))
    i += 1
    t += BEAT
t = 9.75
while t < 12.0:
    h = hat(amp=0.2)
    add(airL, t, h, 0.7); add(airR, t + 0.005, h, 1.0)
    t += BEAT

# --- COMING SOON hit (12) ----------------------------------------------------
add(airL, 11.2, whoosh(0.85, amp=0.42, reverse=True)); add(airR, 11.2, whoosh(0.85, amp=0.42, reverse=True))
add(low, 12.0, impact(amp=1.15, dur=2.2))
add(low, 12.5, kick(amp=0.72)); add(low, 13.0, kick(amp=0.62))
add(low, 12.0, sub(43.65, 1.4, amp=0.52))

# --- tail / end card (13.5 - 15) --------------------------------------------
add(low, 13.5, sub(43.65, 1.5, amp=0.44))
add(airL, 13.5, shimmer(1.5, amp=0.075)); add(airR, 13.52, shimmer(1.5, amp=0.075))
add(low, 13.5, kick(amp=0.5))

# --- cut whooshes on every scene change -------------------------------------
for t0, g in ((1.86, .34), (4.36, .3), (5.86, .36), (9.36, .34), (11.88, .3), (13.38, .28)):
    w = whoosh(0.46, amp=g)
    add(airL, t0, w, 1.0); add(airR, t0 + 0.006, w, 0.85)

# ----------------------------------------------------------------- master
def cheap_space(x, taps=((0.071, .16), (0.113, .11), (0.181, .07))):
    y = x.copy()
    for d, g in taps:
        k = int(d * SR)
        y[k:] += x[:-k] * g
    return y

airL = cheap_space(airL)
airR = cheap_space(airR)

L = low + airL
R = low + airR

fade_in = np.minimum(1.0, np.arange(N) / (0.05 * SR))
fade_out = np.minimum(1.0, (N - np.arange(N)) / (0.45 * SR))
env = fade_in * fade_out
L *= env
R *= env

peak = max(np.abs(L).max(), np.abs(R).max())
L = np.tanh(L / peak * 1.5) * 0.9
R = np.tanh(R / peak * 1.5) * 0.9

stereo = np.empty(N * 2, dtype=np.int16)
stereo[0::2] = np.int16(np.clip(L, -1, 1) * 32600)
stereo[1::2] = np.int16(np.clip(R, -1, 1) * 32600)

out = sys.argv[1] if len(sys.argv) > 1 else 'audio.wav'
with wave.open(out, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(stereo.tobytes())
print('wrote', out, '%.2fs' % DUR)
