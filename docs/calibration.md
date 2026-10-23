# Calibrating the chain

Converting a scope reading into a pressure needs exactly two numbers: the
transducer's sensitivity and the amplifier's gain. This is how both were
established, and why the usual two-point pressure calibration turned out to be
the worse option.

---

## The chain

```
P  ->  bridge  ->  V_raw  ->  [balance]  ->  pregain  ->  filter  ->  postgain  ->  V_out
```

```
V_raw = (FSO / P_FS) * (E / E_rated) * P  +  V_unbalance
V_out = G * (V_raw - V_balance)
```

| Term | Meaning |
|---|---|
| FSO | Full-scale output, 100 mV nominal at rated excitation |
| P_FS | Rated pressure range — a model option, not a constant |
| E | Excitation actually applied; E_rated = 10.0 VDC |
| V_unbalance | Residual bridge offset, ±5 mV typical |
| G | System gain, pregain × postgain |
| V_balance | DC injected at the amplifier input to null the output |

Two things in there are worth dwelling on. FSO is *nominal*, and unbalance is
*typical* and can be 5% of full-scale output on its own. Calculating pressure
from datasheet values alone carries both errors.

---

## Why not two known pressures

The standard method applies two pressures you know and fits a line. It needs a
pressure standard and plumbing.

It also has a span problem. Slope error scales as 1/(P₂ − P₁), so the quality of
the calibration depends entirely on how far apart the two points are:

| Second point | Span from ambient | Relative slope error |
|---|---|---|
| 1 m water column | 1.42 PSI | baseline |
| 4 atm gas fill | 44.5 PSI | 31× better |

A water manometer is an excellent *primary* standard — 1 PSI is 705.2 mm of water
at 25 °C, and reading the height to ±1 mm knows the pressure to ±0.0014 PSI,
which is 176× better than the sensor it is calibrating. But on a 500 PSI
transducer it only moves you 1.4 PSI from ambient, and that short span is what
limits the slope.

---

## What was done instead

The KSC-2's bridge-balance circuit is a programmable DC source injected at the
amplifier input, and its accuracy falls under the conditioner's NIST-traceable
calibration certificate. That makes it a usable reference for everything
downstream of the bridge.

**Procedure.** Balance at ambient and record the value. Step the balance voltage
by known amounts, both polarities, recording the mean output at each. Return to
the original balance.

**Results.** Six points, gain nominally 64, 20 mV/div on the readout:

| Balance (mV) | Δ (mV) | Output (mV) |
|---|---|---|
| −5.2441 | 0 | −0.16 |
| −4.9805 | +0.2636 | +16.54 |
| −4.7363 | +0.5078 | +32.23 |
| −4.2383 | +1.0058 | +64.05 |
| −5.7324 | −0.4883 | −31.62 |
| −6.2305 | −0.9864 | −63.38 |

```
G  = 63.987
c  = -0.123 mV
R2 = 0.999997
```

0.02% from nominal. The largest residual is 0.123 mV against a readout
quantization step of 0.625 mV, so **every point agrees to better than a fifth of
one display step.** Both polarities match, so there is no asymmetry in the chain.

### The quantization you will hit

Every balance value above is an exact multiple of 10/4096 = 2.4414 µV. There is a
12-bit DAC behind that field and it cannot land on round numbers. Record what the
GUI accepted, not what you typed — otherwise you introduce an error in the
independent variable, which is the one place least-squares assumes there is none.

### Ratios versus regression

Dividing each row by its own step gives 63.35, 63.78, 63.84, 64.43, 64.09 — a
1.7% spread that reads as nonlinearity.

It is not. The baseline measured −0.16 mV rather than exactly zero, and that
fixed error is 1% of the 16 mV step but 0.25% of the 64 mV one. The ratios are
biased most where the step is smallest.

A regression fits slope and intercept together, so the offset lands in the
intercept and the slope comes out clean. **Systematic offsets masquerade as
nonlinearity when you reduce by ratios**, and the tell is a spread that shrinks
monotonically as the step grows.

---

## Closing it with the certificate

The step test gives the gain. The transducer's calibration certificate gives the
sensitivity, measured on this serial number against a Mensor CPC6000:

```
CTL-312-500A, S/N 8779-12-195
Sensitivity: 0.203 mV/PSI A at 10.0 VDC excitation
```

0.203 rather than the 0.200 the nominal 100 mV FSO implies — the real full-scale
output is 101.5 mV, 1.5% above nominal. That correction is invisible without the
certificate.

```
slope = 63.99 x 0.203 = 12.99 mV/PSI
P = (V_out / 12.99 mV/PSI) + P_at_balance
```

No pressure standard, no plumbing, both terms traceable.

---

## An independent check

At ambient (~14.3 PSIA station pressure at Fermilab's elevation) the bridge
produces:

```
14.3 PSIA x 0.203 mV/PSI = 2.90 mV
```

Autobalance removed 5.2441 mV. The difference, 2.34 mV, must be the residual
bridge unbalance — and the certificate quotes ±5 mV typical. It lands inside.

Nothing forced that agreement. Two numbers from different sources landing
consistently is the cheapest confidence you will ever get.

---

## What changes when the chamber arrives

At the gain needed for the real test (2048, both stages at maximum), the static
4 atm signal would be 24.4 V against a ±10 V output. **Balance becomes
structural, not optional.** The measurement then reads:

```
V_out = 415.7 mV/PSI x (P - P_fill)
```

Change from the fill pressure, not absolute. Absolute comes back by adding the
fill pressure from the regulator gauge. That is normal practice — the slope
carries the physics.

**Re-measure G after any change of gain, coupling, or excitation.** The balance
LED clears itself on all three, which is the instrument telling you the same
thing.

---

## Error budget

For a 16.3 PSI swing on a 500 PSI transducer:

| Source | Magnitude | Share of swing |
|---|---|---|
| Gain, measured | ±0.02% | negligible |
| Sensitivity, certificate | — | small |
| Sensor accuracy, 0.1% FSO typical | ±0.50 PSI | 3.1% |
| Thermal zero shift, 10 °F lab drift | ±0.50 PSI | 3.1% |

The electronics are not the limit. The transducer is, and the dominant term is
thermal zero drift — which is why the instruction is to re-balance every session
rather than to chase another digit of gain accuracy.

A 500 PSI range on a 16 PSI swing is a coarse match. It was specced for the
eventual 10 atm target, where it uses 29% of range with 3× margin to the
overpressure limit. That is the right call for the project and a temporary
nuisance for the shakedown.
