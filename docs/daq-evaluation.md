# Choosing a readout

A CAEN DT5725S digitizer was available and the obvious question was whether to
use it. The answer is no for this measurement and yes for a later one, and the
reasoning generalises to any "we already own a fast instrument" situation.

---

## The board

| | |
|---|---|
| Channels | 8, single-ended, MCX |
| Resolution | 14-bit |
| Sample rate | 250 MS/s, fixed |
| Memory | 640 kS per channel |
| Input range | 2 Vpp or 0.5 Vpp, 50 Ω, DC coupled |
| Interfaces | USB 2.0 (30 MB/s), optical CONET (80 MB/s) |

Supplied with a DPP-SUP "super licence" unlocking every DPP firmware for that
board.

---

## The arithmetic that settles it

```
640,000 samples / 250,000,000 samples per second = 2.56 ms
```

That is how much time the board holds in one record. The stroke being measured
takes about 300 ms.

```
300 / 2.56 = 117x short
```

Equivalently, covering 300 ms at 250 MS/s would need 75 million samples and there
are 640,000.

### It cannot sample slower

Three reasons, stacking from practical to physical.

**No firmware setting.** No decimation or clock divider appears in the waveform
recording firmware. Some DPP firmwares have a decimation parameter, but it is for
the digital filter, limited to factors like ÷8, and DPP does active baseline
subtraction that would erase a slowly rising pressure signal.

Even ÷8 would give 20.5 ms. Covering 300 ms needs ÷117.

**The converter has a minimum clock rate.** A 250 MS/s 14-bit part is a pipelined
ADC: the sample moves down a chain of stages, each resolving a few bits and
handing a residue voltage to the next, held on a switched capacitor. Charge leaks
off capacitors. Clock it too slowly and the residue droops before the next stage
converts it, and the output is wrong rather than noisy. These parts carry a
specified *minimum* rate.

Covering 300 ms with 640 kS needs 2.13 MS/s, likely at or below the floor.

**It is a design choice.** A nuclear-physics digitizer optimises short records,
high trigger rate, low dead time, and 4 ns timestamps. Nobody buying one wants a
300 ms recording. A variable clock would cost money and degrade the timing that
is the product's reason to exist.

That is the difference from an oscilloscope. A scope's timebase knob *does*
change the sample rate, because a scope's job is "cover this window." The
digitizer's job is "catch this event."

---

## What continuous export would need

```
250 MS/s x 2 bytes = 500 MB/s per channel

USB 2.0  =  30 MB/s  ->  16.7x short
optical  =  80 MB/s  ->   6.25x short
```

Retriggering as fast as readout allows gives a dashed line, not a curve:

```
one full buffer = 1.28 MB
over USB: 42.7 ms readout + 2.56 ms capture = 5.7% duty
over 300 ms: 6.6 windows, 17 ms of the stroke seen
```

---

## The strobed scheme, which does work

Export rate is `(2 × RECORD_LENGTH + header) × trigger rate`. You do not have to
export 640,000 samples per trigger.

```
625 samples x 2 bytes + 32 header = 1,282 bytes per event
1,282 x 5,000 events/s            = 6.4 MB/s     (21% of USB 2.0)
```

| Record | Window | Trigger rate | MB/s | Points per 300 ms |
|---|---|---|---|---|
| 625 | 2.5 µs | 2 kHz | 2.56 | 600 |
| 625 | 2.5 µs | 5 kHz | 6.41 | 1,500 |
| 250 | 1.0 µs | 10 kHz | 5.32 | 3,000 |

The ADC never slows down. You sample for 2.5 µs and ignore the next 197.5 µs —
a 1.25% duty cycle, which drops the data rate by the same 80×.

And each point is better than a single sample. In 2.5 µs a 500 Hz signal moves
0.45° of phase, so the window is a frozen instant and all 625 samples can be
averaged:

```
noise falls by sqrt(625) = 25x
1 LSB = 122 uV  ->  effective 4.9 uV per point
```

Do not strobe at 1 kHz. The KSC-2's lowest filter setting is 500 Hz, so a 1 kHz
strobe puts Nyquist exactly on the filter corner and the skirt folds back into
the data as fake low-frequency wander. 2 kHz is the minimum with margin.

---

## Why it still is not the right answer

| Option | Points per stroke | Setup |
|---|---|---|
| DT5725S, strobed at 5 kHz | 1,500 | ~half a day plus post-processing |
| USB DAQ at 5 kS/s | 1,500 | plug in |
| Oscilloscope at 10 kS/s | 3,000 | already on the bench |

Line up what each measurement actually needs:

| Measurement | Needs | Fits in 2.56 ms? |
|---|---|---|
| Full expansion curve (DC–500 Hz) | 10 kS/s × 300 ms = 3,000 pts | no |
| Pressure edge shape | 50 kS/s × 10 ms = 500 pts | no |
| Chamber acoustic ring and decay | 20 kS/s × 50 ms = 1,000 pts | no |
| Sensor resonance, 240 kHz | 1 MS/s × 1 ms | yes |
| Bubble acoustic emission | 5 MS/s × 1 ms | yes |

Everything the warm shakedown needs is a few thousand samples spread over
hundreds of milliseconds. The digitizer is built for a few thousand samples
spread over one millisecond. **Same sample count, wrong timescale by 100×.**

A 500 Hz-limited signal needs 1 kS/s. Sampling it at 250 MS/s is 250,000×
Nyquist, and the entire memory goes into 2.56 ms of nothing.

---

## Electrical interface, if it is used anyway

**50 Ω fixed input, ±1 V maximum.** The KSC-2 outputs ±10 V and is rated for
±25 mA. Ohm's law on the mismatch:

```
10 V / 50 ohm = 200 mA   vs 25 mA rated   ->  8x over
```

Ten times the maximum input voltage and eight times the rated output current, at
the same time. **Set the system gain to roughly 241 and verify the output on a
DMM before an MCX cable touches the board.**

**The 10 Ω output into 50 Ω is a fixed 16.7% amplitude loss.** Harmless, but it
means calibrating with the digitizer connected, never with a scope and then
swapping.

**Inputs are MCX, not BNC.** Adapters needed.

**Resolution is a non-issue.** 2 Vpp over 14 bits is 122 µV per LSB, which at
gain 241 is 0.0012 PSI against a sensor accurate to ±0.50 PSI. Four hundred times
finer than the thing being measured.

**Use the waveform firmware, not DPP.** DPP tracks and subtracts the baseline,
which would read a rising pressure as drift and remove it.

---

## Where the board does belong

Bubble nucleation in a superheated liquid produces an acoustic emission lasting
microseconds. Discriminating those events by pulse shape is exactly what DPP-PSD
is for, and 4 ns timestamps across 8 channels is exactly what a multi-sensor
acoustic array needs.

The purchase was aimed at the physics, not at cycle monitoring. That is the right
instrument for the right measurement, arriving before the measurement does.
