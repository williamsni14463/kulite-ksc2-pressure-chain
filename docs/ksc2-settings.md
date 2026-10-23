# KSC-2 settings reference

Every column in the KSC-2 GUI, what it does, and what it was set to for this
application. Sources are the KSC-2 specification sheet and Technical Notes Rev C.

The working configuration for a CTL-312-500A on a bench, as of 2026-10-23:

```
Excitation Type        Bipolar
Excitation Value       10.000 V
Sense                  Local
Coupling               DC
Shield                 Ground
Input Mode             Operate
Overload Mode          Latching
Pregain                64
Filter Type            Pulse (LP6P)
Filter Cutoff          500 Hz
Resonance Compensation Disabled
Postgain               1.0
Output Overload        9.5 V
Rear ground switch     Signal Ground, post empty
```

---

## Excitation

**Excitation Type.** Unipolar is a fixed 14 VDC for transducers with internal
amplifiers. Bipolar is programmable 0–12.5 V applied as ±half, so the bridge
centres on zero and the signal leads sit near ground, where the differential
amplifier rejects common mode best.

Kulite: *"significant errors in the range of 0.25% FSO commonly occur"* with
unipolar excitation on unamplified transducers. The CTL-312 is unamplified.
**Bipolar.**

**Excitation Value.** Programmable in 1.25 mV steps, ±0.1% of setting. Output is
*directly proportional* to this, so a 1% excitation error is a 1% span error.
**Set it to the rated 10.000 V** so the transducer's certificate stays valid.
Maximum is 12 V; there is nothing to gain by going there.

Setting it to 0.000 V is a deliberate diagnostic — the bridge goes dead and
anything still on the readout is wiring pickup.

**Sense.** The cable has resistance in series with the bridge, so the voltage at
the sensor is below what the KSC-2 sets. Sense leads measure at the far end and
let the supply compensate.

This transducer has a 4-conductor cable, so there are no sense leads and **Local**
is the only option. That turns out not to matter:

```
30 AWG copper, 40 in  ->  0.671 ohm for both excitation leads
input impedance        ->  2064 ohm (certificate; datasheet minimum is 1000)

room temp:  delivers 99.9675% of set excitation
at 89 K:    delivers 99.9929%
span change warm to cold: +0.025%
```

The transducer's own thermal sensitivity shift over that same trip is ±3.7%, so
the cable effect is 145× smaller. Not worth engineering around.

---

## Zeroing and coupling

**Autobalance.** Injects a DC at the amplifier input to drive the output to 0 V.
Range is ±32 mV/V at pregain ≥16, which at 10 V excitation is ±320 mV referred to
input. LED: green succeeded, yellow working, red failed.

Needs live excitation (it uses the bipolar supply) and **is disabled in AC
coupling.**

The LED clears whenever gain, coupling, or excitation changes, or on power cycle.
That is the instrument saying the balance is stale, not a fault.

**Pregain ≥16 matters here.** Balance resolution is 1 µV/V at pregain ≥16 and
16 µV/V below it — sixteen times coarser. Set the gain *before* balancing.

**Balance Voltage.** The value autobalance landed on, in mV referred to input.
**Record it every run.** If you balanced at a fill pressure you deliberately
discarded absolute pressure, and this value is how it comes back. It is also a
drift log: a balance voltage that walks between sessions is the sensor telling
you something.

The field is quantized to 10/4096 = 2.4414 µV steps, so it will not accept round
numbers.

**Coupling.** DC passes everything including the static pressure, and is required
for balancing, wiring checks, and calibration by discrete steps.

AC inserts a 0.25 Hz two-pole high-pass. At 1 Hz the amplitude error is 0.19% —
but the phase lead is 28°, which is **78 ms**. Against a 290 ms stroke that is a
27% timing error on the quantity being measured.

**Use DC and balance instead.** Balance buys the same dynamic range with no phase
error.

> **Kulite's caution, verbatim:** *"Removal of static component may allow for the
> inadvertent overpressure of the transducer."* AC-coupled, a calm trace says
> nothing about absolute pressure. Keep a mechanical gauge in sight.

**Shield.** Three configurations at pin 9:

| Setting | What it does |
|---|---|
| **Grounded** | Shield tied at the KSC-2 only, acting as a Faraday cage. Correct for low-frequency work. |
| Driven | Common-mode voltage on the shield; kills cable capacitance, extends bandwidth, does not reject near-field interference. |
| HF | Both ends grounded through 0.1 µF for magnetic interference above 1 MHz; the cap blocks low-frequency ground loops. |

Five shielding rules worth not breaking: never leave both ends unterminated;
never ground both ends except in the HF case; keep connections short, because a
long pigtail is added inductance; never tie shields together through a bulkhead;
never let a shield share a return path with a signal.

The last two bite in a cryostat, where everything is bolted to the same cold mass
and the jacket is a tempting return path.

---

## Gain

**Pregain** is ×1 to ×128 in binary steps, *before* the filter. Gain here
amplifies out-of-band energy too, so anything that can ring clips at this stage
and the filter then hides the evidence.

Kulite's rule: most of the gain in pregain for well-understood low-noise signals;
lower pregain for spectrally rich content or transducers that may reach
resonance.

This sensor's resonance is 240 kHz–1.4 MHz and nothing in a 1 Hz bellows cycle
excites it. ×64 leaves the pre-filter signal with a 24× margin to the 10.2 V trip,
which absorbs chamber acoustics comfortably.

**Postgain** is ×1/16 to ×16, *after* the filter, and continuous to 0.025%
resolution rather than binary. Gain here cannot cause pre-filter clipping, so it
is the safe place to trim. System gain ranges 0.0625 to 2048.

Sizing rule: `G = 8 V / (largest expected input)`, leaving 2 V of headroom.

---

## Overload detection

**Input Overload** is fixed at ±10.2 V, after pregain and before the filter. Not
adjustable, deliberately — it catches out-of-band clipping that the low-pass
would otherwise smooth into a plausible-looking waveform.

**If this lights, the data is wrong even though the trace looks clean.** Drop
pregain and move the gain to postgain.

**Output Overload** is programmable 0.1–10.2 V in 0.1 V steps, after postgain.
Set it just above the expected peak and it doubles as a pressure alarm — the only
automatic "something exceeded plan" indicator in the chain.

**Overload Mode.** Continuous lights only while over the limit; Latching stays
lit until reset. A transient that clips for 3 ms in a 1 Hz cycle is invisible in
continuous mode. **Latching.**

---

## Filtering

**Filter Type.** Two 6-pole responses:

| | Phase | Rolloff | Step response |
|---|---|---|---|
| **LP6F (flat)** | Linear to 50% of passband | Sharpest, stop band at 2.611×Fc | Rings and overshoots |
| **LP6P (pulse)** | Linear across the passband | Gentler, stop band at 5.192×Fc | Fast rise, minimal overshoot |

Flat for frequency-domain work, pulse for time-domain. This measurement compares
a pressure curve against a commanded motion profile, so the edges are the data.
**Pulse.**

**Filter Cutoff.** 500 Hz to 127.5 kHz in 500 Hz steps. 500 Hz is the floor.

Signal content here is DC to about 100 Hz. A 500 Hz LP6P passes all of it with
roughly 1 ms of group delay — negligible against a 290 ms stroke — and crushes
the sensor's 240 kHz resonance entirely.

Noise grows as √bandwidth, so running at 10 kHz instead of 500 Hz carries 4.5×
more noise for nothing.

**Resonance Compensation (REZCOMP, option C3).** Three ranges: recess tube
(10–2550 Hz), cavity (2.6–51.2 kHz), seismic (52–255 kHz). All are for extending
usable bandwidth past 20 kHz. Filtering at 500 Hz, this can only add phase error
to a band that is not being used. **Disabled.**

**Wideband** removes the anti-alias filter for a 500 kHz 3-pole Butterworth
response. No reason to use it here.

---

## Diagnostics

**Input Mode** switches an internal relay:

| Mode | What the amplifier sees |
|---|---|
| **Operate / Normal** | The transducer |
| **Cal** | The front CAL BNC, so a known DC can be injected to verify gain |
| **Short** | Amplifier input grounded, injected balance removed — shows the conditioner's own offset and noise |

Short then Cal during commissioning separates "the conditioner is adding
something" from "the transducer is producing something."

---

## Not in the GUI

**Ground Configuration switch, rear panel.** Two positions, and it decides
whether a single-ended readout works.

*Chassis Ground* is as-shipped: internal reference tied to chassis, earthed
through the supply. Correct when feeding a differential input.

*Signal Ground* with nothing on the post is for a single-ended input. The manual
names this case: *"the output signal is connected to a single ended A/D input,
possibly a single-ended oscilloscope. This is also known as bank isolation."*

A scope BNC shell is earthed through the scope's mains ground. Leaving the KSC-2
in Chassis Ground gives two earth points and a 60 Hz ground loop.

**CAL input BNC.** Isolated input that replaces the transducer when Input Mode is
Cal. With a 6½-digit DVM on both sides it measures true system gain rather than
assuming it. Calibrate channels individually unless they share the same pregain.

---

## Calibration status

The conditioner's own certificate matters more than it looks, because the gain
measurement in [calibration.md](calibration.md) uses the KSC-2's balance DAC as
its reference. That measurement is traceable only while the certificate is.

```
KSC-2-C3, S/N 206192-011
Calibrated 04-05-2024 by Precision Filters to ANSI/NCSL Z540-1-1994
In service 11/5/25, due 11/5/26
```

Note the 12-month interval was started from the in-service date rather than the
calibration date. Common and defensible for electronics that sat in a box, but it
is a local decision someone made, worth being able to explain.
