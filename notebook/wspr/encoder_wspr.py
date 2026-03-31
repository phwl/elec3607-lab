#!/usr/bin/env python3
"""
wspr_encoder.py -- Generate a WSPR transmission as a 12000 Hz WAV file.

WSPR (Weak Signal Propagation Reporter) encodes a callsign, 4-character
Maidenhead grid locator and transmit power into 162 4-FSK symbols transmitted
over ~110.6 seconds.  The four tones are spaced 12000/8192 ≈ 1.4648 Hz apart.

Usage:
    python wspr_encoder.py CALLSIGN GRID POWER [options]

Positional arguments:
    CALLSIGN   Amateur callsign, e.g. VK2XX or G4JNT
    GRID       4-character Maidenhead locator, e.g. QF56 or IO91
    POWER      Transmit power in dBm (0-60, prefer multiples ending in 0/3/7)

Options:
    --freq  FLOAT   Audio carrier frequency in Hz for tone-0 [default: 1500]
    --out   FILE    Output WAV filename [default: wspr_<call>_<grid>_<pwr>.wav]
    --rate  INT     WAV sample rate in Hz [default: 12000]
    --pad   FLOAT   Silence padding in seconds at start and end [default: 1.0]
    --amp   FLOAT   Peak amplitude 0.0-1.0 [default: 0.8]

Examples:
    python wspr_encoder.py VK2XX QF56 37
    python wspr_encoder.py G4JNT IO91 10 --freq 1500 --out beacon.wav
    python wspr_encoder.py K1ABC FN20 23 --rate 48000 --pad 2.0
"""

import sys
import argparse
import wave
import math
import numpy as np

# ---------------------------------------------------------------------------
# WSPR protocol constants
# ---------------------------------------------------------------------------
WSPR_SAMPLE_RATE = 12000          # standard processing rate
WSPR_SYM_SAMP    = 8192           # samples per symbol at 12000 Hz
WSPR_SYMBOLS     = 162            # total symbols per transmission
WSPR_TONE_SEP    = WSPR_SAMPLE_RATE / WSPR_SYM_SAMP   # ≈ 1.4648 Hz
WSPR_DURATION    = WSPR_SYMBOLS * WSPR_SYM_SAMP / WSPR_SAMPLE_RATE  # ≈ 110.6 s

# Convolutional encoder polynomials  (rate-1/2, constraint length K=32)
POLY1 = 0xF2D05351
POLY2 = 0xE4613C47

# 162-bit pseudo-random sync vector  (verified against WSJT-X source)
SYNC_VECTOR = [
    1,1,0,0,0,0,0,0,1,0,0,0,1,1,1,0,0,0,1,0,0,1,0,1,1,1,1,0,0,0,0,0,
    0,0,1,0,0,1,0,1,0,0,0,0,0,0,1,0,1,1,0,0,1,1,0,1,0,0,0,1,1,0,1,0,
    0,0,0,1,1,0,1,0,1,0,1,0,1,0,0,1,0,0,1,0,1,1,0,0,0,1,1,0,1,0,1,0,
    0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,1,1,0,1,1,0,0,1,1,0,1,0,0,0,1,1,1,
    0,0,0,0,0,1,0,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1,1,0,0,0,1,1,0,
    0,0
]
assert len(SYNC_VECTOR) == WSPR_SYMBOLS

_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ '

# ---------------------------------------------------------------------------
# Source encoder
# ---------------------------------------------------------------------------
def _encode_callsign(call: str) -> int:
    """Pack a callsign into a 28-bit integer."""
    call = call.upper().strip()
    # 1-letter prefix (G4JNT → ' G4JNT'): 2nd char is digit, prepend space
    # 2-letter prefix (VK2XX, K1ABC): pad right with spaces
    if len(call) >= 2 and call[1].isdigit():
        call = (' ' + call).ljust(6)[:6]
    else:
        call = call.ljust(6)[:6]
    n = _CHARS.index(call[0])
    n = n * 36 + _CHARS.index(call[1])
    n = n * 10 + _CHARS.index(call[2])
    n = n * 27 + (_CHARS.index(call[3]) - 10)
    n = n * 27 + (_CHARS.index(call[4]) - 10)
    n = n * 27 + (_CHARS.index(call[5]) - 10)
    return n


def _encode_locator_power(loc: str, pwr: int) -> int:
    """Pack a 4-char Maidenhead locator and power (dBm) into a 22-bit integer."""
    loc = loc.upper()
    m  = (179 - 10 * (ord(loc[0]) - ord('A')) - int(loc[2])) * 180
    m += 10 * (ord(loc[1]) - ord('A')) + int(loc[3])
    return m * 128 + pwr + 64


def _pack_50_bits(n: int, m: int) -> list:
    """Combine 28-bit N and 22-bit M into an 81-bit list (50 data + 31 zeros)."""
    combined = (n << 22) | m
    return [(combined >> i) & 1 for i in range(49, -1, -1)] + [0] * 31


# ---------------------------------------------------------------------------
# Convolutional encoder  (rate-1/2, K=32)
# ---------------------------------------------------------------------------
def _parity(x: int) -> int:
    x ^= x >> 16; x ^= x >> 8; x ^= x >> 4; x ^= x >> 2; x ^= x >> 1
    return x & 1


def _conv_encode(bits: list) -> list:
    """Encode 81 source bits → WSPR_SYMBOLS coded bits."""
    reg = 0
    out = []
    for b in bits:
        reg = ((reg << 1) | b) & 0xFFFFFFFF
        out.append(_parity(reg & POLY1))
        out.append(_parity(reg & POLY2))
    return out


# ---------------------------------------------------------------------------
# Interleaver  (bit-reversal permutation)
# ---------------------------------------------------------------------------
def _bit_reverse_8(i: int) -> int:
    return int(f'{i:08b}'[::-1], 2)


def _interleave(bits: list) -> list:
    dest = [0] * WSPR_SYMBOLS
    p = 0
    for i in range(256):
        j = _bit_reverse_8(i)
        if j < WSPR_SYMBOLS:
            dest[j] = bits[p]
            p += 1
            if p == WSPR_SYMBOLS:
                break
    return dest


# ---------------------------------------------------------------------------
# Public: generate the WSPR_SYMBOLS WSPR symbols
# ---------------------------------------------------------------------------
def encode_wspr(callsign: str, locator: str, power: int) -> list:
    """
    Encode a WSPR message and return WSPR_SYMBOLS symbols (each 0-3).

    Parameters
    ----------
    callsign : amateur callsign, e.g. 'VK2XX'
    locator  : 4-char Maidenhead grid, e.g. 'QF56'
    power    : transmit power in dBm (0-60)

    Returns
    -------
    List of WSPR_SYMBOLS integers in {0, 1, 2, 3}
    """
    n      = _encode_callsign(callsign)
    m      = _encode_locator_power(locator, power)
    bits   = _pack_50_bits(n, m)
    coded  = _conv_encode(bits)
    interl = _interleave(coded)
    return [sv + 2 * d for sv, d in zip(SYNC_VECTOR, interl)]


# ---------------------------------------------------------------------------
# Audio generation
# ---------------------------------------------------------------------------
def generate_audio(
        symbols:    list,
        base_freq:  float = 1500.0,
        sample_rate: int  = WSPR_SAMPLE_RATE,
        amplitude:  float = 0.8,
) -> np.ndarray:
    """
    Convert WSPR_SYMBOLS WSPR symbols into a continuous-phase FSK audio waveform.

    Continuous-phase FSK (CPFSK) is used so that tone transitions are smooth
    (no clicks or spectral splatter at symbol boundaries).  The instantaneous
    phase at the start of each symbol is the accumulated phase from all
    previous symbols.

    Parameters
    ----------
    symbols     : list of WSPR_SYMBOLS ints in {0,1,2,3}
    base_freq   : audio frequency of tone 0 in Hz
    sample_rate : output sample rate in Hz
    amplitude   : peak amplitude, 0.0-1.0

    Returns
    -------
    float32 numpy array of audio samples
    """
    # Samples per symbol at the output rate
    sps = int(round(sample_rate * WSPR_SYM_SAMP / WSPR_SAMPLE_RATE))

    # Tone frequencies for symbols 0..3
    tone_freqs = [base_freq + k * WSPR_TONE_SEP for k in range(4)]

    total = len(symbols) * sps
    audio = np.zeros(total, dtype=np.float64)
    phase = 0.0   # accumulated phase in radians (ensures CPFSK continuity)

    for i, sym in enumerate(symbols):
        f   = tone_freqs[sym]
        t   = np.arange(sps, dtype=np.float64) / sample_rate
        seg = np.sin(phase + 2.0 * math.pi * f * t)
        audio[i * sps : (i + 1) * sps] = seg
        # Advance phase to maintain continuity at symbol boundary
        phase += 2.0 * math.pi * f * sps / sample_rate
        phase  = phase % (2.0 * math.pi)   # keep in [0, 2π) to avoid float drift

    return (audio * amplitude).astype(np.float32)


def add_silence(audio: np.ndarray, pad_seconds: float,
                sample_rate: int) -> np.ndarray:
    """Prepend and append silence."""
    pad = np.zeros(int(pad_seconds * sample_rate), dtype=np.float32)
    return np.concatenate([pad, audio, pad])


# ---------------------------------------------------------------------------
# WAV output
# ---------------------------------------------------------------------------
def write_wav(path: str, audio: np.ndarray, sample_rate: int) -> None:
    """Write a mono 16-bit PCM WAV file."""
    pcm = np.clip(audio, -1.0, 1.0)
    pcm = (pcm * 32767.0).astype(np.int16)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)       # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm.tobytes())


# ---------------------------------------------------------------------------
# Input validation helpers
# ---------------------------------------------------------------------------
_VALID_POWER_DBM = {0, 3, 7, 10, 13, 17, 20, 23, 27, 30,
                    33, 37, 40, 43, 47, 50, 53, 57, 60}


def _validate_callsign(call: str) -> str:
    call = call.upper().strip()
    if not call:
        raise ValueError("Callsign cannot be empty")
    allowed = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/')
    if not all(c in allowed for c in call):
        raise ValueError(f"Invalid callsign characters in '{call}'")
    # Enforce encodable length
    padded = call
    if len(padded) >= 2 and padded[1].isdigit():
        padded = ' ' + padded
    if len(padded) > 6:
        raise ValueError(
            f"Callsign '{call}' is too long for a standard WSPR type-1 message "
            f"(max 5 chars for 2-letter prefix, max 4 chars for 1-letter prefix). "
            f"Compound callsigns require type-2 messages (not yet supported).")
    return call


def _validate_locator(loc: str) -> str:
    loc = loc.upper().strip()
    if len(loc) != 4:
        raise ValueError(f"Locator must be exactly 4 characters, got '{loc}'")
    if not (loc[0].isalpha() and loc[1].isalpha() and
            loc[2].isdigit()  and loc[3].isdigit()):
        raise ValueError(
            f"Locator must be two letters followed by two digits, e.g. 'IO91', got '{loc}'")
    if not ('A' <= loc[0] <= 'R' and 'A' <= loc[1] <= 'R'):
        raise ValueError(
            f"Locator field characters must be A-R, got '{loc}'")
    return loc


def _validate_power(pwr: int) -> int:
    if not (0 <= pwr <= 60):
        raise ValueError(f"Power must be 0-60 dBm, got {pwr}")
    if pwr not in _VALID_POWER_DBM:
        # Warn but allow; the decoder will label it as illegal
        print(f"Warning: {pwr} dBm is not a standard WSPR power level. "
              f"Standard values end in 0, 3, or 7 (e.g. 37, 30, 23). "
              f"Receivers will decode it but mark it 'illegal power'.",
              file=sys.stderr)
    return pwr


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> None:
    parser = argparse.ArgumentParser(
        description='Generate a WSPR transmission as a 12000 Hz WAV file.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python wspr_encoder.py VK2XX QF56 37
  python wspr_encoder.py G4JNT IO91 10 --freq 1500 --out beacon.wav
  python wspr_encoder.py K1ABC FN20 23 --rate 48000 --pad 2.0
  python wspr_encoder.py W1AW FN41 37 --freq 1550 --amp 0.5
""")

    parser.add_argument('callsign',
                        help='Amateur callsign (e.g. VK2XX, G4JNT, K1ABC)')
    parser.add_argument('grid',
                        help='4-character Maidenhead locator (e.g. QF56, IO91)')
    parser.add_argument('power', type=int,
                        help='Transmit power in dBm (0-60; prefer 0,3,7,10,13,…)')
    parser.add_argument('--freq', type=float, default=1500.0,
                        help='Audio frequency (Hz) for the lowest tone  [%(default)s]')
    parser.add_argument('--out', default=None,
                        help='Output WAV filename  [wspr_CALL_GRID_PWR.wav]')
    parser.add_argument('--rate', type=int, default=WSPR_SAMPLE_RATE,
                        help='WAV sample rate in Hz  [%(default)s]')
    parser.add_argument('--pad', type=float, default=1.0,
                        help='Silence padding in seconds at each end  [%(default)s]')
    parser.add_argument('--amp', type=float, default=0.8,
                        help='Peak amplitude 0.0-1.0  [%(default)s]')

    args = parser.parse_args()

    # --- Validate inputs ---
    try:
        callsign = _validate_callsign(args.callsign)
        locator  = _validate_locator(args.grid)
        power    = _validate_power(args.power)
    except ValueError as exc:
        parser.error(str(exc))

    if not (100.0 <= args.freq <= 5000.0):
        parser.error(f"--freq {args.freq} Hz is outside the sensible range 100-5000 Hz")

    if args.rate < 8000 or args.rate > 192000:
        parser.error(f"--rate {args.rate} Hz is outside the supported range 8000-192000 Hz")

    if not (0.0 < args.amp <= 1.0):
        parser.error(f"--amp must be in (0, 1], got {args.amp}")

    if args.pad < 0:
        parser.error("--pad must be >= 0")

    # Check highest tone doesn't exceed Nyquist
    highest_tone = args.freq + 3 * WSPR_TONE_SEP
    if highest_tone > args.rate / 2 - 100:
        parser.error(
            f"Highest tone ({highest_tone:.1f} Hz) is too close to the Nyquist "
            f"frequency ({args.rate//2} Hz) for sample rate {args.rate} Hz. "
            f"Lower --freq or raise --rate.")

    # --- Output filename ---
    if args.out is None:
        safe_call = callsign.replace('/', '-')
        args.out = f"wspr_{safe_call}_{locator}_{power}dBm.wav"

    # --- Encode ---
    print(f"Encoding  {callsign}  {locator}  {power} dBm")
    symbols = encode_wspr(callsign, locator, power)

    # Verify symbol count and range
    assert len(symbols) == WSPR_SYMBOLS, f"Expected 162 symbols, got {len(symbols)}"
    assert all(0 <= s <= 3 for s in symbols), "Symbol out of range 0-3"

    tone_bw_hz = 3 * WSPR_TONE_SEP
    print(f"  Tones    {args.freq:.2f} – {args.freq + tone_bw_hz:.2f} Hz  "
          f"(spacing {WSPR_TONE_SEP:.4f} Hz)")
    print(f"  Duration {WSPR_DURATION:.2f} s  +  {args.pad:.1f}s padding each end")

    # --- Generate audio ---
    audio = generate_audio(symbols,
                           base_freq=args.freq,
                           sample_rate=args.rate,
                           amplitude=args.amp)
    if args.pad > 0:
        audio = add_silence(audio, args.pad, args.rate)

    total_s = len(audio) / args.rate
    print(f"  Samples  {len(audio):,}  ({total_s:.2f} s)  @ {args.rate} Hz")

    # --- Write WAV ---
    write_wav(args.out, audio, args.rate)
    print(f"  Written  {args.out}")

    # --- Summary of symbols ---
    tone_counts = [symbols.count(k) for k in range(4)]
    print(f"\nSymbol distribution: "
          + "  ".join(f"tone{k}={tone_counts[k]}" for k in range(4)))
    print(f"First 20 symbols: {symbols[:20]}")


if __name__ == '__main__':
    main()
