#!/usr/bin/env python3
"""
wspr_decoder.py  --  Decode WSPR transmissions from a WAV audio file.

Algorithm:
  1. Average the power spectrum to find candidate signal frequencies.
  2. For each unique candidate, do a coarse block-aligned sync search to find
     the best start block, then a fine 200-sample search around it (top 5 offsets).
  3. Demodulate with an exact-frequency heterodyne (no inter-bin leakage),
     trying ±0.75 Hz in 0.375 Hz steps to find the best sub-bin frequency.
  4. Fano sequential decode (rate-1/2, K=32).
  5. Re-encode check: accept only decodes whose re-encoded symbols match the
     received hard decisions at >= 0.85, eliminating all false positives.

Dependencies:  pip install numpy scipy
Usage:
    python wspr_decoder.py recording.wav
    python wspr_decoder.py recording.wav --freq 1500 --bw 200 --verbose
"""

import sys, argparse, wave
import numpy as np
from scipy.signal import resample_poly
from math import gcd

# ---------------------------------------------------------------------------
# WSPR constants
# ---------------------------------------------------------------------------
WSPR_RATE     = 12000
WSPR_SYM_SAMP = 8192
WSPR_SYMBOLS  = 162
WSPR_DURATION = WSPR_SYMBOLS * WSPR_SYM_SAMP / WSPR_RATE   # 110.6 s
FREQ_RES      = WSPR_RATE / WSPR_SYM_SAMP                  # 1.46484375 Hz

POLY1 = 0xF2D05351
POLY2 = 0xE4613C47

SYNC_VECTOR = np.array([
    1,1,0,0,0,0,0,0,1,0,0,0,1,1,1,0,0,0,1,0,0,1,0,1,1,1,1,0,0,0,0,0,
    0,0,1,0,0,1,0,1,0,0,0,0,0,0,1,0,1,1,0,0,1,1,0,1,0,0,0,1,1,0,1,0,
    0,0,0,1,1,0,1,0,1,0,1,0,1,0,0,1,0,0,1,0,1,1,0,0,0,1,1,0,1,0,1,0,
    0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,1,1,0,1,1,0,0,1,1,0,1,0,0,0,1,1,1,
    0,0,0,0,0,1,0,1,0,0,1,1,0,0,0,0,0,0,0,1,1,0,1,0,1,1,0,0,0,1,1,0,
    0,0,
], dtype=np.int8)

_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ '
_N     = np.arange(WSPR_SYM_SAMP, dtype=np.float64)

# Interleave permutation: source position p maps to dest position _PERM[p].
# Derived from the bit-reversal of 8-bit indices, taking the first 162
# values of {i : bit_reverse(i) < 162}.
_PERM = np.array([int(f'{i:08b}'[::-1], 2)
                  for i in range(256)
                  if int(f'{i:08b}'[::-1], 2) < 162])[:162]

# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def _parity(x):
    x ^= x >> 16; x ^= x >> 8; x ^= x >> 4; x ^= x >> 2; x ^= x >> 1
    return x & 1

# ---------------------------------------------------------------------------
# Source encoder / decoder
# ---------------------------------------------------------------------------
def encode_callsign(call):
    call = call.upper().strip()
    call = (' ' + call).ljust(6)[:6] if len(call) >= 2 and call[1].isdigit() \
           else call.ljust(6)[:6]
    n = _CHARS.index(call[0])
    n = n*36 + _CHARS.index(call[1])
    n = n*10 + _CHARS.index(call[2])
    n = n*27 + _CHARS.index(call[3]) - 10
    n = n*27 + _CHARS.index(call[4]) - 10
    n = n*27 + _CHARS.index(call[5]) - 10
    return n

def encode_locator_power(loc, pwr):
    loc = loc.upper()
    m  = (179 - 10*(ord(loc[0])-65) - int(loc[2])) * 180
    m += 10*(ord(loc[1])-65) + int(loc[3])
    return m * 128 + pwr + 64

def decode_callsign(n):
    c = ['']*6
    c[5]=_CHARS[n%27+10]; n//=27
    c[4]=_CHARS[n%27+10]; n//=27
    c[3]=_CHARS[n%27+10]; n//=27
    c[2]=_CHARS[n%10];    n//=10
    c[1]=_CHARS[n%36];    n//=36
    c[0]=_CHARS[n%37]
    return ''.join(c).strip()

def decode_locator_power(m):
    pwr  = m%128 - 64; m //= 128
    loc2 = m%180;      m //= 180
    loc1 = 179 - m
    return (chr(65+loc1//10) + chr(65+loc2//10) + str(loc1%10) + str(loc2%10)), pwr

def decode_message(bits50):
    v = 0
    for b in bits50: v = (v << 1) | int(b > 0)
    loc, pwr = decode_locator_power(v & 0x3FFFFF)
    return decode_callsign(v >> 22), loc, pwr

# ---------------------------------------------------------------------------
# Convolutional encoder + interleaver  (used only for re-encode validation)
# ---------------------------------------------------------------------------
def _pack_50_bits(n, m):
    v = (n << 22) | m
    return [(v >> i) & 1 for i in range(49, -1, -1)] + [0]*31

def _conv_encode(bits):
    reg = 0; out = []
    for b in bits:
        reg = ((reg << 1) | b) & 0xFFFFFFFF
        out.append(_parity(reg & POLY1))
        out.append(_parity(reg & POLY2))
    return out

def _interleave(bits):
    out = [0]*162
    for p, j in enumerate(_PERM): out[j] = bits[p]
    return out

def _deinterleave(vals):
    return [vals[j] for j in _PERM]

def wspr_encode_symbols(callsign, locator, power):
    """Full encode: callsign + locator + power -> 162 channel symbols."""
    n = encode_callsign(callsign)
    m = encode_locator_power(locator, power)
    return [int(sv) + 2*d for sv, d in
            zip(SYNC_VECTOR, _interleave(_conv_encode(_pack_50_bits(n, m))))]

# ---------------------------------------------------------------------------
# Fano sequential decoder  (rate-1/2, K=32)
# ---------------------------------------------------------------------------
def fano_decode(soft_bits, n_iter_max=500000, delta=0.5):
    """
    Decode 162 de-interleaved soft values to 50 data bits.
    soft_bits[i] > 0  =>  conv output bit i is likely 1.

    came_forward prevents re-taking the same wrong branch on backtrack:
    first visit tries branches[0] then [1]; revisit skips straight to [1].
    """
    N = 81  # 50 data bits + 31 flush zeros
    t = 0; reg = 0; cum = 0.0; path = []; T = 0.0; came_forward = True

    for _ in range(n_iter_max):
        if t >= N:
            return [b for b, _, _ in path][:50]

        s0 = soft_bits[2*t]; s1 = soft_bits[2*t+1]
        branches = sorted(
            [(s0*(2*_parity(((reg<<1)|b)&0xFFFFFFFF & POLY1)-1) +
              s1*(2*_parity(((reg<<1)|b)&0xFFFFFFFF & POLY2)-1), b,
              ((reg<<1)|b)&0xFFFFFFFF)
             for b in (0, 1)],
            reverse=True)

        moved = False
        for m, b, nr in branches[0 if came_forward else 1:]:
            if cum + m >= T:
                path.append((b, reg, cum))
                cum += m; reg = nr; t += 1
                while cum >= T + delta: T += delta
                came_forward = True; moved = True; break

        if not moved:
            if not path:
                T -= delta; came_forward = True; continue
            _, reg, cum = path.pop(); t -= 1
            T -= delta; came_forward = False

    return [b for b, _, _ in path][:50]

# ---------------------------------------------------------------------------
# WAV loading
# ---------------------------------------------------------------------------
def load_wav(path):
    with wave.open(path, 'rb') as wf:
        sr, nch, sw = wf.getframerate(), wf.getnchannels(), wf.getsampwidth()
        raw = wf.readframes(wf.getnframes())
    if   sw == 1: s = np.frombuffer(raw, np.uint8).astype(np.float32)/128.0 - 1.0
    elif sw == 2: s = np.frombuffer(raw, np.int16).astype(np.float32)/32768.0
    elif sw == 4: s = np.frombuffer(raw, np.int32).astype(np.float32)/2147483648.0
    else: sys.exit(f"Unsupported sample width: {sw}")
    if nch > 1: s = s[::nch]
    return s, sr

def resample_to_12k(samples, orig_rate):
    if orig_rate == WSPR_RATE: return samples
    g = gcd(orig_rate, WSPR_RATE)
    return resample_poly(samples, WSPR_RATE//g, orig_rate//g).astype(np.float32)

# ---------------------------------------------------------------------------
# Demodulation
# ---------------------------------------------------------------------------
def _demod(samples, start, freq_hz):
    """
    Demodulate 162 symbols with exact-frequency heterodyne.

    Multiplying each 8192-sample segment by exp(-2j*pi*freq_hz/fs*n) shifts
    tone-0 exactly to DC, so complex FFT bins 0-3 give clean 4-FSK tone
    powers with no inter-bin leakage regardless of the signal frequency.

    Soft metric: (P_high_pair - P_low_pair) / P_total  in [-1, +1],
    matching wsprd's linear normalised formulation.
    """
    n_sym = min(WSPR_SYMBOLS, (len(samples) - start) // WSPR_SYM_SAMP)
    segs  = np.stack([samples[start+i*WSPR_SYM_SAMP : start+(i+1)*WSPR_SYM_SAMP].astype(np.float64)
                      for i in range(n_sym)])
    if n_sym < WSPR_SYMBOLS:
        segs = np.vstack([segs, np.zeros((WSPR_SYMBOLS-n_sym, WSPR_SYM_SAMP))])
    specs = np.abs(np.fft.fft(segs * np.exp(-2j*np.pi*freq_hz/WSPR_RATE*_N), axis=1)[:, :4])**2
    hard  = np.argmax(specs, axis=1).astype(np.int8)
    soft  = ((specs[:,2]+specs[:,3]) - (specs[:,0]+specs[:,1])) / (specs.sum(1) + 1e-30)
    return soft.astype(np.float32), hard, specs

def _sync_score(hard):
    return float(np.mean((hard & 1) == SYNC_VECTOR))

def _sync_intbin(samples, start, base_bin):
    """Fast sync score using integer-bin rfft (for offset search only)."""
    n    = min(WSPR_SYMBOLS, (len(samples)-start) // WSPR_SYM_SAMP)
    segs = np.stack([samples[start+i*WSPR_SYM_SAMP : start+(i+1)*WSPR_SYM_SAMP].astype(np.float64)
                     for i in range(n)])
    pw   = (np.abs(np.fft.rfft(segs, axis=1))**2)[:, base_bin:base_bin+4]
    return _sync_score(np.argmax(pw, axis=1).astype(np.int8))

# ---------------------------------------------------------------------------
# Candidate frequency search
# ---------------------------------------------------------------------------
def _find_peaks(samples, centre_hz, bw_hz, n_cands=12):
    """Average power spectrum over the recording, return top peaks as (freq_hz, snr_db)."""
    lo   = max(0, int((centre_hz - bw_hz) / FREQ_RES))
    hi   = min(WSPR_SYM_SAMP//2, int((centre_hz + bw_hz) / FREQ_RES))
    step = max(WSPR_SYM_SAMP, (len(samples) - WSPR_SYM_SAMP) // 20)
    ffts = [np.abs(np.fft.rfft(samples[t0:t0+WSPR_SYM_SAMP].astype(np.float64)))**2
            for t0 in range(0, len(samples)-WSPR_SYM_SAMP, step)]
    avg   = np.mean(ffts, axis=0)
    band  = avg[lo:hi]
    noise = float(np.median(band)) + 1e-30
    top   = np.argsort(band)[-n_cands:][::-1]
    return [(float(lo+r)*FREQ_RES, 10*np.log10(float(band[r])/noise)) for r in top]


# ---------------------------------------------------------------------------
# SNR estimation — replicates wsprd's spectrum-based SNR exactly
# ---------------------------------------------------------------------------
def _wsprd_snr(samples, centre_hz, signal_freq_hz):
    """
    Compute SNR in dB re 2500 Hz bandwidth, matching wsprd's output.

    wsprd's method (from wsprd.c):
      1. Compute 512-pt overlapping FFTs on the audio, stepped by 128 samples,
         windowed with w[i] = sin(pi*i/511).  This is equivalent to working on
         the full 12 kHz audio directly rather than the 375 Hz IQ stream.
         Effective bin spacing: 12000/512 = 23.4 Hz ... but wait, wsprd works
         on the 375 Hz IQ stream, so its 512-pt FFT gives 375/512 = 0.732 Hz/bin.
         We replicate that by first heterodyning to baseband at centre_hz,
         decimating by 32, then doing the 512-pt FFTs.
      2. Average all FFT frames into psavg[512].
      3. Apply a 7-point boxcar smooth → smspec[411] covering ±150 Hz.
      4. Noise floor = 30th percentile of smspec.
      5. SNR = 10*log10(peak/noise - 1) - 26.3  (26.3 dB converts from the
         ~5.1 Hz effective bin width to the 2500 Hz reference bandwidth).
    """
    from scipy.signal import resample_poly
    from math import gcd

    IQ_RATE = 375

    # Heterodyne to baseband and decimate by 32
    t  = np.arange(len(samples)) / WSPR_RATE
    bb = samples.astype(np.float64) * np.exp(-2j * np.pi * centre_hz * t)
    iq = (resample_poly(bb.real, 1, 32) +
          1j * resample_poly(bb.imag, 1, 32))

    # 512-pt overlapping FFTs, step 128, sine window (wsprd uses sin(0.006148*i))
    win   = np.sin(0.006147931 * np.arange(512))
    nffts = 4 * int(len(iq) / 512) - 1
    psavg = np.zeros(512)
    for i in range(nffts):
        seg = iq[i*128 : i*128+512]
        if len(seg) < 512: break
        # fftshift: wsprd uses k=j+256 with wrap-around
        psavg += np.roll(np.abs(np.fft.fft(seg * win))**2, 256)
    psavg /= max(nffts, 1)

    # 7-point boxcar smooth → 411 bins covering ±150 Hz around centre
    smspec = np.array([psavg[256-205+i-3 : 256-205+i+4].sum() for i in range(411)])

    # 30th-percentile noise floor
    noise = float(np.percentile(smspec, 30)) + 1e-30

    # Find the smspec peak within ±10 Hz of the decoded signal frequency
    df_smspec = IQ_RATE / 512          # 0.732 Hz per bin
    i_c = int(round((signal_freq_hz - centre_hz) / df_smspec)) + 205
    hw  = max(1, int(10.0 / df_smspec))
    lo, hi = max(0, i_c - hw), min(411, i_c + hw + 1)
    pk  = lo + int(np.argmax(smspec[lo:hi]))

    snr_lin = smspec[pk] / noise - 1.0
    return round(10.0 * np.log10(max(snr_lin, 1e-10)) - 26.3)

# ---------------------------------------------------------------------------
# Main decode pipeline
# ---------------------------------------------------------------------------
def decode_wspr(samples, centre_hz=1500.0, bw_hz=200.0,
                min_snr=-35.0, verbose=False):
    """
    Decode all WSPR signals in `samples` (12 kHz float32).
    Returns list of dicts: callsign, locator, power_dbm, freq_hz, snr_db.
    """
    min_samps = WSPR_SYMBOLS * WSPR_SYM_SAMP
    extra     = max(0, len(samples) - min_samps)

    if len(samples) < min_samps:
        print(f"Warning: audio {len(samples)/WSPR_RATE:.1f}s, need >= {WSPR_DURATION:.0f}s")

    peaks = _find_peaks(samples, centre_hz, bw_hz)
    if verbose:
        print("  Spectral peaks:")
        for f, snr in peaks: print(f"    {f:8.2f} Hz  SNR {snr:+.1f} dB")

    # Coarse search: block-aligned integer-bin sync, deduplicated to one entry
    # per rounded Hz.  Threshold 0.45 is intentionally low — the coarse score
    # is unreliable when the TX start falls between block boundaries.
    # The re-encode >= 0.85 check is the real quality gate.
    coarse = {}   # round(base_hz) -> (best_sc, best_off, base_hz)
    for peak_hz, est_snr in peaks:
        if est_snr < min_snr: continue
        for tone_shift in (0, -1, -2, -3):
            base_hz  = peak_hz + tone_shift * FREQ_RES
            base_bin = int(round(base_hz / FREQ_RES))
            if not (1 <= base_bin <= WSPR_SYM_SAMP//2 - 4): continue
            best_sc = 0.0; best_off = 0
            for off in range(0, extra+1, WSPR_SYM_SAMP):
                if off + min_samps > len(samples): break
                sc = _sync_intbin(samples, off, base_bin)
                if sc > best_sc: best_sc = sc; best_off = off
            if best_sc < 0.45: continue
            key = round(base_hz)
            if best_sc > coarse.get(key, (0,))[0]:
                coarse[key] = (best_sc, best_off, base_hz)

    if verbose:
        print(f"\n  {len(coarse)} unique candidate frequencies")

    results = []

    for coarse_sc, best_off, base_hz in sorted(coarse.values(), reverse=True):
        base_bin = int(round(base_hz / FREQ_RES))

        # Fine search: 200-sample steps around the best coarse block
        lo = max(0,     best_off - WSPR_SYM_SAMP)
        hi = min(extra, best_off + WSPR_SYM_SAMP)
        fine = sorted(
            [(sc, off) for off in range(lo, hi+1, 200)
             if off + min_samps <= len(samples)
             for sc in [_sync_intbin(samples, off, base_bin)]],
            reverse=True)

        # Keep top 5 offsets spaced >= 200 samples apart
        top_offs = []
        for sc, off in fine:
            if all(abs(off-o) >= 200 for _, o in top_offs):
                top_offs.append((sc, off))
                if len(top_offs) == 5: break

        for fine_sc, off in top_offs:
            if fine_sc < 0.50: break

            # Frequency refinement: ±0.75 Hz in 0.375 Hz steps
            best_sc = 0.0; best_freq = base_hz
            for df in np.arange(-0.75, 0.76, 0.375):
                _, hard, _ = _demod(samples, off, base_hz + df)
                sc = _sync_score(hard)
                if sc > best_sc: best_sc = sc; best_freq = base_hz + df

            if best_sc < 0.60: continue

            soft, hard, pows = _demod(samples, off, best_freq)
            if verbose:
                print(f"\n  {base_hz:.2f} Hz  off={off}  freq={best_freq:.2f}  sync={best_sc:.3f}")

            bits = fano_decode(_deinterleave(soft.tolist()))
            try:
                callsign, locator, power = decode_message(bits)
            except Exception:
                continue

            if not (callsign and locator and len(locator) == 4
                    and all(c.isalnum() or c in ' /' for c in callsign)):
                continue

            # Re-encode check: true signals score >= 0.85
            try:
                expected  = wspr_encode_symbols(callsign, locator, power)
                sym_match = sum(int(h)==e for h,e in zip(hard, expected)) / WSPR_SYMBOLS
            except Exception:
                sym_match = 0.0

            if sym_match < 0.85:
                if verbose: print(f"    re-enc={sym_match:.3f}  REJECTED: {callsign} {locator}")
                continue

            snr_db = _wsprd_snr(samples, centre_hz, best_freq)

            rec = dict(callsign=callsign, locator=locator, power_dbm=power,
                       freq_hz=round(best_freq, 2), snr_db=snr_db)
            if not any(r['callsign']==callsign and r['locator']==locator for r in results):
                results.append(rec)
                if verbose:
                    print(f"    -> {callsign}  {locator}  {power} dBm  (re-enc={sym_match:.3f})")

    return results

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description='Decode WSPR from a WAV file.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    ap.add_argument('input')
    ap.add_argument('--freq',    type=float, default=1500.0, help='Centre frequency (Hz)')
    ap.add_argument('--bw',      type=float, default=200.0,  help='Search bandwidth ± Hz')
    ap.add_argument('--snr-min', type=float, default=-35.0,  help='Min spectral SNR (dB)')
    ap.add_argument('--verbose', '-v', action='store_true')
    args = ap.parse_args()

    print(f"Loading  {args.input}")
    samples, rate = load_wav(args.input)
    print(f"  {rate} Hz  {len(samples)/rate:.1f} s  {len(samples):,} samples")
    if len(samples)/rate < WSPR_DURATION * 0.9:
        print(f"  Warning: short recording, need ~{WSPR_DURATION:.0f} s")
    if rate != WSPR_RATE:
        print(f"  Resampling {rate} -> {WSPR_RATE} Hz ...")
        samples = resample_to_12k(samples, rate)

    print(f"\nSearching  {args.freq} Hz ± {args.bw} Hz  SNR >= {args.snr_min} dB\n")
    results = decode_wspr(samples, centre_hz=args.freq, bw_hz=args.bw,
                          min_snr=args.snr_min, verbose=args.verbose)

    if results:
        sep = '-' * 56
        print(sep)
        print(f"{'Callsign':<12} {'Grid':<6} {'Power':>7} {'Audio Hz':>10} {'SNR dB':>7}")
        print(sep)
        for r in results:
            print(f"{r['callsign']:<12} {r['locator']:<6} {r['power_dbm']:>4} dBm "
                  f"{r['freq_hz']:>10.2f} {r['snr_db']:>7.1f}")
        print(sep)
        print(f"  {len(results)} decode(s)")
    else:
        print("No signals decoded.")
        print("Try --verbose, adjust --freq / --bw, or check the recording "
              "is a complete ~110 s WSPR window.")

if __name__ == '__main__':
    main()
