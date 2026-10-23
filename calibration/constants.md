# Measured constants

Everything needed to turn a readout voltage into a pressure, with where each
number came from.

| Quantity | Value | Source |
|---|---|---|
| Transducer | Kulite CTL-312-500A | — |
| Serial | 8779-12-195 | Certificate |
| Range | 500 PSIA absolute | Certificate |
| Maximum pressure | 1000 PSIA | Certificate |
| **Sensitivity** | **0.203 mV/PSI** | Certificate, at 10.0 VDC, Mensor CPC6000, 4/6/2026 |
| Implied FSO | 101.5 mV | Derived — 1.5% above the 100 mV nominal |
| Zero balance output | ±5 mV typical | Certificate |
| Compensated range | −184 °C to 38 °C (89.15–311.15 K) | Certificate |
| Input impedance | 2064 Ω | Certificate (datasheet minimum 1000 Ω) |
| Output impedance | 1031 Ω | Certificate |
| Screen | B | Certificate |

| Quantity | Value | Source |
|---|---|---|
| Conditioner | Kulite KSC-2-C3, S/N 206192-011 | — |
| Conditioner calibration | 04-05-2024, due 11/5/26 | Precision Filters, ANSI/NCSL Z540-1-1994 |
| Excitation | 10.000 V bipolar | Set |
| Pregain × Postgain | 64 × 1.0 | Set |
| **System gain, measured** | **63.987** | Balance-step injection, R² = 0.999997 |
| Balance voltage at ambient | −5.2441 mV | Autobalance, 2026-10-23 |
| Residual bridge unbalance | ~2.34 mV | Derived; inside the ±5 mV typical |

## Working slope

```
slope = 63.987 x 0.203 mV/PSI = 12.99 mV/PSI
P     = (V_out / 12.99 mV/PSI) + P_at_balance
```

Excitation current: 10.0 V / 2064 Ω = 4.84 mA, which is 16% of the KSC-2's 30 mA
capability.

## Gain settings for other readouts

| Target | Gain | Swing for 16.34 PSI | Slope |
|---|---|---|---|
| Oscilloscope, ±10 V | 2048 (KSC-2 maximum) | 6.79 V | 415.7 mV/PSI |
| CAEN DT5725S, ±1 V into 50 Ω | 241 | 0.80 V | 49.0 mV/PSI |

At gain 2048 the unbalanced static signal at 4 atm would be 24.4 V. Balancing at
the fill pressure is required, not optional.

## This configuration only

The gain above belongs to this exact set of settings. Changing gain, coupling, or
excitation invalidates it — the KSC-2's balance LED clears on all three, which is
the instrument saying the same thing. Re-run the step test after any of them.

The sensitivity is valid only at 10.0 VDC excitation. Output is directly
proportional to excitation, so a different excitation voltage scales it.

## Still open

The transducer's compensated range bottoms at 89.15 K and the datasheet operating
range at 77.65 K. A proposed 50 K cold test sits below both — 39 K below
compensation, 28 K below operating. That needs a different sensor, a thermal
standoff, or an in-situ cold recalibration, and the decision should be made
before the chamber is machined for permanent ports.
