#!/usr/bin/env python3
"""Synthesises the lid sounds (sci-fi latches, hiss, servo, chirps) and writes them as OGG.

    python tools/make_sounds.py

Writes addons/lids/sounds/<set>_<open|close>.ogg for the sets case, med and pouch. Everything is made
here from noise and tones - no recorded material - so the mod carries no one else's audio. Needs numpy
and ffmpeg (with libvorbis) on the PATH.
"""
import os
import subprocess
import tempfile
import wave

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "addons", "lids", "sounds"))
SR = 48000
rng = np.random.default_rng(7)


def t_axis(sec):
    return np.arange(int(sec * SR)) / SR


def env(n, attack, decay, sustain=0.0):
    """Attack, then exponential decay to `sustain` (all in seconds/levels)."""
    t = np.arange(n) / SR
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    d = sustain + (1 - sustain) * np.exp(-np.maximum(t - attack, 0) / max(decay, 1e-4))
    return a * d


def bandpass(x, lo, hi):
    """Brick-wall band-pass in the frequency domain - fine for noise beds."""
    f = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    f[(freqs < lo) | (freqs > hi)] = 0
    return np.fft.irfft(f, len(x))


def place(buf, snd, at):
    i = int(at * SR)
    j = min(len(buf), i + len(snd))
    buf[i:j] += snd[: j - i]


def click(strength=1.0, ring=2600.0, length=0.05):
    """A latch: a sharp noise transient with a short metallic ring."""
    n = int(length * SR)
    t = np.arange(n) / SR
    noise = bandpass(rng.standard_normal(n), 1200, 9000) * env(n, 0.0005, 0.004)
    tone = np.sin(2 * np.pi * ring * t) * env(n, 0.0005, 0.012) * 0.5
    return strength * (noise * 0.8 + tone)


def thunk(freq=85.0, length=0.14, strength=1.0):
    """The lid coming to rest: a low, damped body knock."""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = freq * (1 + 0.6 * np.exp(-t / 0.01))
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * env(n, 0.001, 0.035)
    knock = bandpass(rng.standard_normal(n), 150, 1800) * env(n, 0.0005, 0.008) * 0.6
    return strength * (body + knock)


def hiss(length, lo=1800.0, hi=9000.0, attack=0.015, decay=0.18, sweep=True):
    """Pressure equalising: band-passed noise, its colour sliding down as the pressure drops."""
    n = int(length * SR)
    a = bandpass(rng.standard_normal(n), lo, hi)
    b = bandpass(rng.standard_normal(n), lo * 0.5, hi * 0.5)
    mix = np.linspace(0, 1, n) if sweep else np.zeros(n)
    return (a * (1 - mix) + b * mix) * env(n, attack, decay)


def servo(length, f0, f1, level=0.25):
    """A small servo: a buzzy tone sliding between two pitches, with a little wobble."""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = f0 + (f1 - f0) * (0.5 - 0.5 * np.cos(np.pi * t / length))
    f = f * (1 + 0.012 * np.sin(2 * np.pi * 23 * t))
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.45 * np.sin(2 * ph) + 0.25 * np.sign(np.sin(3 * ph)) * 0.3
    shape = np.sin(np.pi * np.clip(t / length, 0, 1)) ** 0.6
    return level * tone * shape


def chirp(length, f0, f1, level=0.35):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = f0 * (f1 / f0) ** (t / length)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return level * np.sin(ph) * env(n, 0.003, length * 0.5)


def beep(freq, length=0.07, level=0.22):
    n = int(length * SR)
    t = np.arange(n) / SR
    e = np.minimum(1, np.minimum(t / 0.004, (length - t) / 0.006))
    return level * np.sin(2 * np.pi * freq * t) * np.clip(e, 0, 1)


def case(opening):
    buf = np.zeros(int(1.05 * SR))
    if opening:
        place(buf, click(1.0, 2600), 0.0)
        place(buf, click(0.8, 3100), 0.045)
        place(buf, hiss(0.6), 0.06)
        place(buf, servo(0.55, 330, 610), 0.12)
        place(buf, thunk(95, strength=0.55), 0.7)
    else:
        place(buf, servo(0.5, 600, 320), 0.0)
        place(buf, thunk(80, strength=1.0), 0.52)
        place(buf, click(0.9, 2400), 0.56)
        place(buf, click(0.7, 2900), 0.6)
        place(buf, hiss(0.25, 2500, 9000, decay=0.06, sweep=False) * 0.5, 0.62)
    return buf


def med(opening):
    buf = case(opening)
    if opening:
        place(buf, beep(1320), 0.82)
        place(buf, beep(1760), 0.9)
    else:
        place(buf, beep(1760, level=0.16), 0.0)
        place(buf, beep(1320, level=0.16), 0.08)
    return buf


def pouch(opening):
    buf = np.zeros(int(0.5 * SR))
    if opening:
        place(buf, click(0.9, 1900, 0.04), 0.0)
        place(buf, chirp(0.08, 1100, 2600), 0.02)
        place(buf, hiss(0.18, 600, 4000, attack=0.01, decay=0.05) * 0.35, 0.03)
    else:
        place(buf, chirp(0.07, 2400, 1000), 0.0)
        place(buf, click(1.0, 1700, 0.04), 0.08)
        place(buf, thunk(140, 0.08, 0.4), 0.085)
    return buf


def write(name, x):
    # a touch of room, then normalise to -3 dBFS
    tail = np.zeros(int(0.25 * SR))
    x = np.concatenate([x, tail])
    room = np.zeros_like(x)
    for delay, gain in ((0.011, 0.25), (0.023, 0.16), (0.041, 0.1), (0.067, 0.06)):
        d = int(delay * SR)
        room[d:] += x[:-d] * gain
    x = x + room
    x = x / (np.abs(x).max() + 1e-9) * 0.7
    pcm = (x * 32767).astype(np.int16)
    os.makedirs(OUT, exist_ok=True)
    wav = os.path.join(tempfile.mkdtemp(), name + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    ogg = os.path.join(OUT, name + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-c:a", "libvorbis", "-q:a", "6", ogg],
                   check=True)
    print("wrote", os.path.relpath(ogg, os.path.join(HERE, "..")), "%.2f s" % (len(x) / SR))


if __name__ == "__main__":
    for set_name, fn in (("case", case), ("med", med), ("pouch", pouch)):
        write(set_name + "_open", fn(True))
        write(set_name + "_close", fn(False))
