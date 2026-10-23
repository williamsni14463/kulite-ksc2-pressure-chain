# Pressure Instrumentation — Kulite CTL-312 through a KSC-2 Conditioner

Commissioning and calibrating the pressure measurement chain for the MAMBA
bubble chamber prototype at Fermilab: a Kulite CTL-312-500A piezoresistive
transducer, a Kulite KSC-2 signal conditioner, and a readout.

```
bridge  ->  excitation + balance  ->  pregain  ->  6-pole filter  ->  postgain  ->  BNC  ->  readout
```

Nothing in that chain knows what pressure is. Every stage is a voltage stage.
Pressure comes back at the end, from two numbers you have to establish yourself.

---

## Calibrating an amplifier chain without a pressure standard

The usual approach to calibrating a pressure measurement is to apply two known
pressures and fit a line. That needs a pressure standard, which needs plumbing,
which needs the chamber, which was not ready.

There is a shortcut, and it turned out to be more accurate than the pressure
route would have been.

**The KSC-2's bridge-balance circuit is a programmable, NIST-traceable DC voltage
source injected at the amplifier input.** Step it by a known amount, measure how
far the output moves, and the ratio is the system gain of everything downstream
of the bridge — with no pressure involved at all.

Six points, both polarities:

| Balance voltage (mV) | Change (mV) | Measured output (mV) |
|---|---|---|
| −5.2441 | 0 | −0.16 |
| −4.9805 | +0.2636 | +16.54 |
| −4.7363 | +0.5078 | +32.23 |
| −4.2383 | +1.0058 | +64.05 |
| −5.7324 | −0.4883 | −31.62 |
| −6.2305 | −0.9864 | −63.38 |

Least-squares fit:

```
G  = 63.987        system gain
c  = -0.123 mV     baseline offset, absorbed
R2 = 0.999997
```

Against a nominal gain of 64, that is **0.02% off**. Largest residual is
0.123 mV, which is under a fifth of the readout's own quantization step — the
agreement is as tight as the instrument can display.

Combine that with the transducer's calibration certificate and the slope falls
out with no pressure standard anywhere:

```
slope = G x sensitivity
      = 63.99 x 0.203 mV/PSI
      = 12.99 mV/PSI

P = (V_out / 12.99 mV/PSI) + P_at_balance
```

Both terms are traceable: sensitivity from Kulite's certificate against a Mensor
CPC6000, gain from the step test underwritten by the conditioner's own
calibration.

Method and full reduction in [docs/calibration.md](docs/calibration.md).
[`scripts/fit_gain.py`](scripts/fit_gain.py) does the arithmetic.

### Why fit rather than divide

Dividing each row by its own step gives gains from 63.35 to 64.43 — a 1.7%
spread that looks like nonlinearity. It is not. The baseline read −0.16 mV
instead of exactly zero, and that fixed error is 1% of the smallest step but only
0.25% of the largest. A regression puts it in the intercept where it belongs and
leaves the slope clean.

Worth internalising generally. **A systematic offset masquerades as
nonlinearity when you reduce data by ratios.**

---

## What the hardware is

| | |
|---|---|
| Transducer | Kulite CTL-312-500A, S/N 8779-12-195 |
| Range | 500 PSIA absolute, 1000 PSIA maximum |
| Sensitivity | 0.203 mV/PSI at 10.0 VDC excitation (certificate) |
| Compensated range | −184 °C to 38 °C (89.15 K to 311.15 K) |
| Conditioner | Kulite KSC-2-C3, S/N 206192-011 |

Wire colours, from the certificate: RED +In, BLACK −In, GREEN +Out, WHITE −Out.

A consistency check that cost nothing: at ambient (~14.3 PSIA) the bridge
produces 14.3 × 0.203 = 2.90 mV of real pressure signal. Autobalance removed
5.2441 mV, leaving 2.34 mV of residual bridge unbalance — inside the ±5 mV the
certificate quotes. Two independent facts agreeing is worth more than either one
alone.

---

## Settings that matter and why

Every KSC-2 setting is documented in [docs/ksc2-settings.md](docs/ksc2-settings.md).
Four decisions carry most of the weight.

**Bipolar excitation, not unipolar.** Bipolar applies ±half across the bridge so
the signal leads sit near ground, which is where the differential amplifier
rejects common mode best. Kulite's own note: *"significant errors in the range of
0.25% FSO commonly occur"* with unipolar excitation on unamplified transducers.
The CTL-312 is unamplified.

**DC coupling plus balance, not AC coupling.** The obvious way to remove a large
static pressure and keep gain for the dynamics is AC coupling. The KSC-2's AC
corner is 0.25 Hz, two-pole — at 1 Hz the amplitude error is only 0.19%, but the
**phase lead is 28°, which is 78 ms**. Against a 290 ms stroke that is a 27%
timing error on exactly the quantity being measured.

Balance can null ±320 mV referred to input, far more than any static pressure in
this application. Balancing at the fill pressure buys the same dynamic range with
no phase error, and the balance value is recorded so the absolute can be added
back.

**LP6P (pulse) filter at 500 Hz.** Pulse mode has linear phase across the
passband — constant time delay, minimal overshoot on a step. Flat mode has a
sharper rolloff but linear phase only to 50% of the passband, which rings step
edges. This measurement is a pressure-versus-time curve compared against a
commanded motion profile, so the edges are the data.

**Latching overload detection.** A transient that clips for 3 ms during a 1 Hz
cycle is invisible in continuous mode. Latching catches it when nobody was
watching, which is the only mode that makes sense for a chamber in another room.

### One caution worth repeating verbatim

Kulite, on AC coupling: *"Removal of static component may allow for the
inadvertent overpressure of the transducer."*

AC-coupled, a trace sitting calmly mid-screen says nothing about absolute
pressure. Keep a mechanical gauge in sight whenever a channel is AC-coupled.

---

## A resonance no filter setting removes

The chamber is about 8.25 inches long. In air at 20 °C the half-wave acoustic
mode lands near 820 Hz and the quarter-wave near 410 Hz.

The KSC-2's lowest filter setting is 500 Hz. Both modes sit at or below it, so
the conditioner cannot remove them at any setting. Ringing at a few hundred hertz
on a pressure step is probably real chamber acoustics, not an artifact — and
arguably data worth keeping rather than suppressing.

---

## Choosing the readout

The conditioner outputs ±10 V on a BNC. What reads it is a separate question, and
the answer was not what the hardware on hand suggested.

[docs/daq-evaluation.md](docs/daq-evaluation.md) works through a CAEN DT5725S
digitizer that was already available: 8 channels, 14-bit, 250 MS/s, 640 kS of
memory per channel.

```
640,000 samples / 250,000,000 samples per second = 2.56 ms
```

The stroke is about 300 ms. The board holds 1/117th of it, and the clock cannot
be slowed — pipelined ADCs have a minimum sample rate below which the sample-hold
capacitors droop and the conversion is simply wrong.

A strobed scheme does work (625-sample bursts at 5 kHz gives 1,500 points per
stroke at 21% of USB 2.0 bandwidth, each point a 25× average). But a $200 USB
logger gives the same points with no setup, and the measurement needs about 3,000
samples total.

The digitizer is the right instrument for acoustic bubble nucleation in liquid,
where microsecond structure is the measurement. It is the wrong instrument for a
third-of-a-second pressure ramp. Same sample count, wrong timescale by 100×.

---

## Layout

```
docs/          Settings reference, calibration method, DAQ evaluation
scripts/       Readout and data reduction
calibration/   Measured constants and certificates
```
