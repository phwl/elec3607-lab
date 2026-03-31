#!/usr/bin/env python3
"""
wspr_decoder.py  --  Decode WSPR transmissions from a WAV audio file.

This decoder replicates wsprd's algorithm as closely as possible:
  1. Downsample the 12 kHz audio to a 375 Hz complex baseband IQ stream
     centred at 1500 Hz (matching wsprd's readwavfile() FFT shift).
  2. Find candidate frequencies from the averaged power spectrum.
  3. For each candidate, scan start-sample offsets at 32-sample resolution
     (= 1 IQ sample at 375 Hz, wsprd's finest time resolution) using the
     integer-bin sync scorer to find the best offsets.
  4. Demodulate using amplitude (not power) of the four 4-FSK tones, with
     sync-vector-weighted soft symbols, normalised by standard deviation
     × symfac=50 to span the uint8 [0,255] range — exact wsprd convention.
  5. Gate on minrms = 52*(50/64) matching wsprd's quality pre-filter.
  6. Fano sequential decode using the exact libfec algorithm:
       - metric_tables[2] from wsjt-x (log-likelihood, 6 dB SNR simulation)
       - bias = 0.45, delta = 60, maxcycles = 10000 per bit
       - Pre-computes all branch metrics before the search loop
       - Backtracking skips to the second branch at the parent node

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
WSPR_SYM_SAMP = 8192       # audio samples per symbol at 12 kHz
WSPR_SYMBOLS  = 162
WSPR_DURATION = WSPR_SYMBOLS * WSPR_SYM_SAMP / WSPR_RATE   # 110.6 s
FREQ_RES      = WSPR_RATE / WSPR_SYM_SAMP                  # 1.46484375 Hz

IQ_RATE    = 375           # IQ sample rate after 32× decimation
IQ_SYMLEN  = 256           # IQ samples per symbol  (= WSPR_SYM_SAMP / 32)
IQ_DF      = IQ_RATE / IQ_SYMLEN   # tone spacing Hz (= FREQ_RES)

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

# Interleave permutation: source position p -> destination index _PERM[p]
_PERM = np.array([int(f'{i:08b}'[::-1], 2)
                  for i in range(256)
                  if int(f'{i:08b}'[::-1], 2) < 162])[:162]

# ---------------------------------------------------------------------------
# metric_tables[2] from wsjt-x/lib/wsprd/metric_tables.c
# Computed by simulation for 4-FSK at 6 dB Es/No.
# mettab[0][i] = round(10 * (MT2[i]   - bias))   received sym for bit=0
# mettab[1][i] = round(10 * (MT2[255-i] - bias))  received sym for bit=1
# ---------------------------------------------------------------------------
_MT2 = [
    0.9999, 0.9998, 0.9998, 0.9998, 0.9998, 0.9998, 0.9997, 0.9997,
    0.9997, 0.9997, 0.9997, 0.9996, 0.9996, 0.9996, 0.9995, 0.9995,
    0.9994, 0.9994, 0.9994, 0.9993, 0.9993, 0.9992, 0.9991, 0.9991,
    0.999, 0.9989, 0.9988, 0.9988, 0.9988, 0.9986, 0.9985, 0.9984,
    0.9983, 0.9982, 0.998, 0.9979, 0.9977, 0.9976, 0.9974, 0.9971,
    0.9969, 0.9968, 0.9965, 0.9962, 0.996, 0.9957, 0.9953, 0.995,
    0.9947, 0.9941, 0.9937, 0.9933, 0.9928, 0.9922, 0.9917, 0.9911,
    0.9904, 0.9897, 0.989, 0.9882, 0.9874, 0.9863, 0.9855, 0.9843,
    0.9832, 0.9819, 0.9806, 0.9792, 0.9777, 0.976, 0.9743, 0.9724,
    0.9704, 0.9683, 0.9659, 0.9634, 0.9609, 0.9581, 0.955, 0.9516,
    0.9481, 0.9446, 0.9406, 0.9363, 0.9317, 0.927, 0.9218, 0.916,
    0.9103, 0.9038, 0.8972, 0.8898, 0.8822, 0.8739, 0.8647, 0.8554,
    0.8457, 0.8357, 0.8231, 0.8115, 0.7984, 0.7854, 0.7704, 0.7556,
    0.7391, 0.721, 0.7038, 0.684, 0.6633, 0.6408, 0.6174, 0.5939,
    0.5678, 0.541, 0.5137, 0.4836, 0.4524, 0.4193, 0.385, 0.3482,
    0.3132, 0.2733, 0.2315, 0.1891, 0.1435, 0.098, 0.0493, 0.0,
    -0.051, -0.1052, -0.1593, -0.2177, -0.2759, -0.3374, -0.4005, -0.4599,
    -0.5266, -0.5935, -0.6626, -0.7328, -0.8051, -0.8757, -0.9498, -1.0271,
    -1.1019, -1.1816, -1.2642, -1.3459, -1.4295, -1.5077, -1.5958, -1.6818,
    -1.7647, -1.8548, -1.9387, -2.0295, -2.1152, -2.2154, -2.3011, -2.3904,
    -2.482, -2.5786, -2.673, -2.7652, -2.8616, -2.9546, -3.0526, -3.1445,
    -3.2445, -3.3416, -3.4357, -3.5325, -3.6324, -3.7313, -3.8225, -3.9209,
    -4.0248, -4.1278, -4.2261, -4.3193, -4.422, -4.5262, -4.6214, -4.7242,
    -4.8234, -4.9245, -5.0298, -5.125, -5.2232, -5.3267, -5.4332, -5.5342,
    -5.6431, -5.727, -5.8401, -5.935, -6.0407, -6.1418, -6.2363, -6.3384,
    -6.4536, -6.5429, -6.6582, -6.7433, -6.8438, -6.9478, -7.0789, -7.1894,
    -7.2714, -7.3815, -7.481, -7.5575, -7.6852, -7.8071, -7.858, -7.9724,
    -8.1, -8.2207, -8.2867, -8.4017, -8.5287, -8.6347, -8.7082, -8.8319,
    -8.9448, -9.0355, -9.1885, -9.2095, -9.2863, -9.4186, -9.5064, -9.6386,
    -9.7207, -9.8286, -9.9453, -10.0701, -10.1735, -10.3001, -10.2858, -10.5427,
    -10.5982, -10.7361, -10.7042, -10.9212, -11.0097, -11.0469, -11.1155, -11.2812,
    -11.3472, -11.4988, -11.5327, -11.6692, -11.9376, -11.8606, -12.1372, -13.2539,
]
assert len(_MT2) == 256

_BIAS = 0.45
_METT = [[round(10*(_MT2[i]   - _BIAS)) for i in range(256)],   # bit=0
          [round(10*(_MT2[255-i] - _BIAS)) for i in range(256)]] # bit=1

# Pre-encoded (METT[o0][s0] + METT[o1][s1]) for all 4 combinations of (o0,o1)
# Index: [o0*2+o1][isym] — used in the Fano loop
_METT4 = [
    [_METT[0][s]+_METT[0][s] for s in range(256)],  # unused placeholder
]
# We'll compute the actual 4-way metric inside fano_decode per node.

SYMFAC   = 50
MINRMS   = 52.0 * (SYMFAC / 64.0)   # = 40.625, wsprd's quality gate

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
# Convolutional encoder + interleaver  (for re-encode validation only)
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
    n = encode_callsign(callsign)
    m = encode_locator_power(locator, power)
    return [int(sv) + 2*d for sv, d in
            zip(SYNC_VECTOR, _interleave(_conv_encode(_pack_50_bits(n, m))))]

# ---------------------------------------------------------------------------
# Fano sequential decoder — exact port of Phil Karn KA9Q's libfec/fano.c
# ---------------------------------------------------------------------------
def fano_decode(isyms, nbits=81, delta=60, maxcycles=10000):
    """
    Fano sequential decoder for rate-1/2 K=32 Layland-Lushbaugh code.

    isyms : 162 de-interleaved uint8 soft symbols (ints in [0,255]).
            128 = erasure, >128 = evidence for 1, <128 = evidence for 0.
    nbits : number of data+flush bits to decode (81 = 50 data + 31 zeros).
    delta : threshold step (60, matching wsprd).
    maxcycles : max threshold decrements per bit (10000, matching wsprd).

    Returns list of 50 decoded data bits (ints 0/1).
    """
    # Pre-compute all branch metrics for each symbol pair
    # metrics[t][k] = METT[k>>1][s0] + METT[k&1][s1]
    #   k=0: sent 00, k=1: sent 01, k=2: sent 10, k=3: sent 11
    mett0, mett1 = _METT[0], _METT[1]
    node_metrics = []
    for t in range(nbits):
        s0, s1 = isyms[2*t], isyms[2*t+1]
        node_metrics.append([
            mett0[s0]+mett0[s1],   # k=0: o0=0,o1=0
            mett0[s0]+mett1[s1],   # k=1: o0=0,o1=1
            mett1[s0]+mett0[s1],   # k=2: o0=1,o1=0
            mett1[s0]+mett1[s1],   # k=3: o0=1,o1=1
        ])

    # Node fields: encstate, gamma, tm[2], i
    # encstate: low bit encodes which branch was taken (0 or 1)
    # gamma:    cumulative metric to this node
    # tm:       [best_metric, other_metric] (sorted descending)
    # i:        current branch index (0=best tried first)

    # Initialise root node (encstate=0)
    enc = 0
    lsym = (_parity(enc & POLY1) << 1) | _parity(enc & POLY2)
    m0 = node_metrics[0][lsym]
    m1 = node_metrics[0][3 ^ lsym]   # complementary pair (both polys odd)
    if m0 >= m1:
        root = {'enc': enc,   'gamma': 0, 'tm': [m0, m1], 'i': 0}
    else:
        root = {'enc': enc+1, 'gamma': 0, 'tm': [m1, m0], 'i': 0}

    nodes = [None] * (nbits + 1)
    nodes[0] = root
    t = 0
    th = 0
    maxcycles = maxcycles * nbits

    for _ in range(maxcycles):
        nd = nodes[t]
        ngamma = nd['gamma'] + nd['tm'][nd['i']]

        if ngamma >= th:
            # Tighten threshold on first visit to this node
            if nd['gamma'] < th + delta:
                while ngamma >= th + delta:
                    th += delta

            # Advance to next node
            t += 1
            if t == nbits:
                break

            next_enc = nd['enc'] << 1
            nodes[t] = {'enc': next_enc, 'gamma': ngamma, 'tm': None, 'i': 0}

            nn = nodes[t]
            enc2 = nn['enc']
            lsym2 = (_parity(enc2 & POLY1) << 1) | _parity(enc2 & POLY2)

            if t >= nbits - 31:
                # Tail: only zero branch
                nn['tm'] = [node_metrics[t][lsym2], -10**9]
            else:
                m0n = node_metrics[t][lsym2]
                m1n = node_metrics[t][3 ^ lsym2]
                if m0n >= m1n:
                    nn['tm'] = [m0n, m1n]
                else:
                    nn['tm'] = [m1n, m0n]
                    nn['enc'] += 1

        else:
            # Threshold violated — backtrack
            while True:
                if t == 0 or nodes[t-1]['gamma'] < th:
                    # Cannot back up: relax threshold
                    th -= delta
                    if nodes[t]['i'] != 0:
                        nodes[t]['i'] = 0
                        nodes[t]['enc'] ^= 1
                    break
                # Back up one step
                t -= 1
                if t < nbits - 31 and nodes[t]['i'] != 1:
                    nodes[t]['i'] += 1
                    nodes[t]['enc'] ^= 1
                    break
                # else keep looking back

    # Extract decoded bytes from encstate at nodes[7], [15], [23], ...
    bits = []
    for byte_idx in range(nbits >> 3):
        nd = nodes[7 + byte_idx * 8]
        byte = (nd['enc'] & 0xFF) if nd is not None else 0
        for bp in range(7, -1, -1):
            bits.append((byte >> bp) & 1)
    return bits[:50]

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

def _resample(samples, orig_rate, target_rate):
    if orig_rate == target_rate: return samples
    g = gcd(orig_rate, target_rate)
    return resample_poly(samples, target_rate//g, orig_rate//g).astype(np.float32)

# ---------------------------------------------------------------------------
# Downsampling to complex baseband IQ at 375 Hz
# ---------------------------------------------------------------------------
def _to_iq(audio, centre_hz=1500.0):
    """
    Heterodyne audio to baseband at centre_hz, then decimate by 32 to 375 Hz.
    Equivalent to wsprd's readwavfile() FFT-shift downsampling.
    """
    t = np.arange(len(audio)) / WSPR_RATE
    bb = audio.astype(np.float64) * np.exp(-2j * np.pi * centre_hz * t)
    iq_r = resample_poly(bb.real, 1, 32)
    iq_i = resample_poly(bb.imag, 1, 32)
    return (iq_r + 1j * iq_i).astype(np.complex128)

# ---------------------------------------------------------------------------
# Demodulation
# ---------------------------------------------------------------------------
def _demod(iq, iq_start, audio_freq_hz, symfac=SYMFAC):
    """
    Demodulate 162 WSPR symbols from the 375-Hz complex IQ stream.

    Matches wsprd's sync_and_demodulate() mode=2:
    - Amplitude (not power) of each 4-FSK tone
    - Sync-vector-weighted soft values:
        sync=1 → fsymb = amp[3]-amp[1]  (high data pair minus low data pair)
        sync=0 → fsymb = amp[2]-amp[0]
    - Normalised by std dev then scaled by symfac=50, clamped to [-128,127]
    - Converted to uint8 by adding 128

    Returns (isyms uint8[162], hard int8[162], raw_fac float).
    """
    # Heterodyne to put tone-0 exactly at bin 0 of the 256-pt DFT
    f_het = (audio_freq_hz - 1500.0) - 1.5 * IQ_DF
    kern = np.exp(-2j * np.pi * f_het / IQ_RATE * np.arange(IQ_SYMLEN, dtype=np.float64))

    n_sym = min(WSPR_SYMBOLS, (len(iq) - iq_start) // IQ_SYMLEN)
    segs = np.stack([iq[iq_start+i*IQ_SYMLEN : iq_start+(i+1)*IQ_SYMLEN]
                     for i in range(n_sym)])
    if n_sym < WSPR_SYMBOLS:
        segs = np.vstack([segs, np.zeros((WSPR_SYMBOLS-n_sym, IQ_SYMLEN), dtype=complex)])

    amps = np.abs(np.fft.fft(segs * kern[None, :], axis=1)[:, :4])   # (162,4)
    hard = np.argmax(amps, axis=1).astype(np.int8)

    # Sync-weighted soft values (wsprd fsymb formula)
    fsymb = np.where(SYNC_VECTOR == 1, amps[:,3]-amps[:,1], amps[:,2]-amps[:,0])

    fsum  = fsymb.mean()
    fac   = float(np.sqrt(max((fsymb**2).mean() - fsum**2, 1e-30)))
    fsymb = np.clip(symfac * fsymb / fac, -128.0, 127.0)
    isyms = (fsymb + 128.0).astype(np.int32)
    return isyms, hard, fac

def _sync_score(hard):
    return float(np.mean((hard & 1) == SYNC_VECTOR))

def _sync_intbin_iq(iq, iq_start, audio_freq_hz):
    """Fast sync score from integer-bin DFT (for offset search)."""
    f_het = (audio_freq_hz - 1500.0) - 1.5 * IQ_DF
    kern = np.exp(-2j * np.pi * f_het / IQ_RATE * np.arange(IQ_SYMLEN, dtype=np.float64))
    n = min(WSPR_SYMBOLS, (len(iq) - iq_start) // IQ_SYMLEN)
    segs = np.stack([iq[iq_start+i*IQ_SYMLEN : iq_start+(i+1)*IQ_SYMLEN]
                     for i in range(n)])
    amps = np.abs(np.fft.fft(segs * kern[None, :], axis=1)[:, :4])
    return _sync_score(np.argmax(amps, axis=1).astype(np.int8))

# ---------------------------------------------------------------------------
# Candidate frequency search
# ---------------------------------------------------------------------------
def _find_peaks(audio, centre_hz, bw_hz, n_cands=12):
    """Average power spectrum of the audio, return top peaks as (freq_hz, snr_db)."""
    lo   = max(0, int((centre_hz - bw_hz) / FREQ_RES))
    hi   = min(WSPR_SYM_SAMP//2, int((centre_hz + bw_hz) / FREQ_RES))
    step = max(WSPR_SYM_SAMP, (len(audio) - WSPR_SYM_SAMP) // 20)
    ffts = [np.abs(np.fft.rfft(audio[t0:t0+WSPR_SYM_SAMP].astype(np.float64)))**2
            for t0 in range(0, len(audio)-WSPR_SYM_SAMP, step)]
    avg   = np.mean(ffts, axis=0)
    band  = avg[lo:hi]
    noise = float(np.median(band)) + 1e-30
    top   = np.argsort(band)[-n_cands:][::-1]
    return [(float(lo+r)*FREQ_RES, 10*np.log10(float(band[r])/noise)) for r in top]

# ---------------------------------------------------------------------------
# SNR estimation (replicates wsprd's spectrum-based SNR)
# ---------------------------------------------------------------------------
def _snr_spectrum(iq):
    """
    Replicate wsprd's SNR computation.
    Uses 512-pt overlapping FFTs on the 375 Hz IQ stream (same as wsprd's
    candidate search), averaged and 7-point smoothed, with noise floor at
    the 30th percentile.  Returns (smspec[411], noise_level, df_smspec).
    """
    nffts = 4 * int(len(iq) / 512) - 1
    w = np.sin(0.006147931 * np.arange(512))
    psavg = np.zeros(512)
    for i in range(nffts):
        seg = iq[i*128 : i*128+512]
        if len(seg) < 512: break
        psavg += np.roll(np.abs(np.fft.fft(seg * w))**2, 256)
    psavg /= max(nffts, 1)
    smspec = np.array([sum(psavg[256-205+i+j] for j in range(-3, 4))
                       for i in range(411)])
    noise = float(np.percentile(smspec, 30))
    return smspec, noise, IQ_RATE / 512   # df = 375/512 = 0.732 Hz

def _signal_snr(smspec, noise, df_smspec, audio_freq_hz, search_hz=10.0):
    """
    Return rounded SNR in dB (in 2500 Hz reference bandwidth) for a signal
    near audio_freq_hz, matching wsprd's output convention.
    Finds the smspec peak within ±search_hz of the signal frequency.
    """
    centre = 1500.0   # IQ baseband centre frequency
    i_c = int(round((audio_freq_hz - centre) / df_smspec)) + 205
    hw  = int(search_hz / df_smspec)
    lo, hi = max(0, i_c - hw), min(411, i_c + hw + 1)
    pk = lo + int(np.argmax(smspec[lo:hi]))
    snr_lin = smspec[pk] / (noise + 1e-30) - 1.0
    return round(10 * np.log10(max(snr_lin, 1e-10)) - 26.3)

# ---------------------------------------------------------------------------
# Main decode pipeline
# ---------------------------------------------------------------------------
def decode_wspr(audio, centre_hz=1500.0, bw_hz=200.0, min_snr=-35.0, verbose=False):
    """
    Decode all WSPR signals in `audio` (12 kHz float32).
    Returns list of dicts: callsign, locator, power_dbm, freq_hz, snr_db.
    """
    min_iq   = WSPR_SYMBOLS * IQ_SYMLEN
    min_samp = WSPR_SYMBOLS * WSPR_SYM_SAMP
    extra_iq = max(0, len(audio) // 32 - min_iq)

    if len(audio) < min_samp:
        print(f"Warning: audio {len(audio)/WSPR_RATE:.1f}s, need >= {WSPR_DURATION:.0f}s")

    # Downsample once
    iq    = _to_iq(audio, centre_hz)
    smspec, noise_level, df_smspec = _snr_spectrum(iq)
    peaks = _find_peaks(audio, centre_hz, bw_hz)

    if verbose:
        print("  Spectral peaks:")
        for f, snr in peaks: print(f"    {f:8.2f} Hz  SNR {snr:+.1f} dB")

    # Coarse block search → deduplicate to one best entry per rounded Hz
    coarse = {}   # round(base_hz) → (best_sc, best_iq_off, base_hz)
    for peak_hz, est_snr in peaks:
        if est_snr < min_snr: continue
        for tone_shift in (0, -1, -2, -3):
            base_hz = peak_hz + tone_shift * FREQ_RES
            if not (centre_hz - bw_hz <= base_hz <= centre_hz + bw_hz): continue
            best_sc = 0.0; best_off = 0
            for iq_off in range(0, extra_iq+1, IQ_SYMLEN):
                if iq_off + min_iq > len(iq): break
                sc = _sync_intbin_iq(iq, iq_off, base_hz)
                if sc > best_sc: best_sc = sc; best_off = iq_off
            if best_sc < 0.45: continue
            key = round(base_hz)
            if best_sc > coarse.get(key, (0,))[0]:
                coarse[key] = (best_sc, best_off, base_hz)

    if verbose:
        print(f"\n  {len(coarse)} unique candidate frequencies")

    results = []

    for coarse_sc, best_blk_off, base_hz in sorted(coarse.values(), reverse=True):
        # Fine IQ-sample offset search around the best block
        lo = max(0,         best_blk_off - 2*IQ_SYMLEN)
        hi = min(extra_iq,  best_blk_off + 2*IQ_SYMLEN)
        fine = sorted(
            [(sc, off)
             for off in range(lo, hi+1, 1)        # 1-IQ-sample = 32-audio-sample step
             if off + min_iq <= len(iq)
             for sc in [_sync_intbin_iq(iq, off, base_hz)]],
            reverse=True)

        # Keep top-5 offsets spaced >= 1 IQ sample apart
        top_offs = []
        for sc, off in fine:
            if all(abs(off-o) >= 1 for _, o in top_offs):
                top_offs.append((sc, off))
                if len(top_offs) == 5: break

        for fine_sc, iq_off in top_offs:
            if fine_sc < 0.50: break

            # Frequency refinement ±0.75 Hz in 0.375 Hz steps
            best_sc = 0.0; best_freq = base_hz
            for df in np.arange(-1.5, 1.51, 0.375):
                _, hard, _ = _demod(iq, iq_off, base_hz + df)
                sc = _sync_score(hard)
                if sc > best_sc: best_sc = sc; best_freq = base_hz + df

            if best_sc < 0.60: continue

            isyms, hard, fac = _demod(iq, iq_off, best_freq)

            # wsprd minrms quality gate: RMS of (isyms-128) must exceed threshold
            rms = float(np.sqrt(np.mean((isyms - 128.0)**2)))
            if rms < MINRMS:
                if verbose: print(f"    {base_hz:.2f} Hz off={iq_off} rms={rms:.1f} < {MINRMS:.1f} SKIP")
                continue

            if verbose:
                print(f"\n  {base_hz:.2f} Hz  iq_off={iq_off}  "
                      f"freq={best_freq:.2f} Hz  sync={best_sc:.3f}  rms={rms:.1f}")

            di   = _deinterleave(isyms.tolist())
            bits = fano_decode(di)

            try:
                callsign, locator, power = decode_message(bits)
            except Exception:
                continue

            if not (callsign and locator and len(locator) == 4
                    and all(c.isalnum() or c in ' /' for c in callsign)):
                continue

            # Re-encode check using hard decisions vs expected channel symbols
            try:
                expected  = wspr_encode_symbols(callsign, locator, power)
                sym_match = sum(int(h)==e for h,e in zip(hard,expected)) / WSPR_SYMBOLS
            except Exception:
                sym_match = 0.0

            if sym_match < 0.60:
                if verbose: print(f"    re-enc={sym_match:.3f}  REJECTED: {callsign} {locator}")
                continue

            snr_db = _signal_snr(smspec, noise_level, df_smspec, best_freq)

            rec = dict(callsign=callsign, locator=locator, power_dbm=power,
                       freq_hz=round(best_freq, 2), snr_db=snr_db)
            if not any(r['callsign']==callsign and r['locator']==locator for r in results):
                results.append(rec)
                if verbose:
                    print(f"    -> {callsign}  {locator}  {power} dBm  "
                          f"(re-enc={sym_match:.3f})")

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
    audio, rate = load_wav(args.input)
    print(f"  {rate} Hz  {len(audio)/rate:.1f} s  {len(audio):,} samples")
    if len(audio)/rate < WSPR_DURATION * 0.9:
        print(f"  Warning: short recording, need ~{WSPR_DURATION:.0f} s")
    if rate != WSPR_RATE:
        print(f"  Resampling {rate} -> {WSPR_RATE} Hz ...")
        audio = _resample(audio, rate, WSPR_RATE)

    print(f"\nSearching  {args.freq} Hz ± {args.bw} Hz  SNR >= {args.snr_min} dB\n")
    results = decode_wspr(audio, centre_hz=args.freq, bw_hz=args.bw,
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
