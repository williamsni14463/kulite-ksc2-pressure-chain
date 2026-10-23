#!/usr/bin/env python3
"""
fit_gain.py — measure the system gain of a bridge amplifier chain by injecting
known offsets with the conditioner's own balance circuit.

The KSC-2's bridge-balance DAC is a programmable DC source applied at the
amplifier input, and its accuracy is covered by the conditioner's NIST-traceable
calibration. Stepping it by a known amount and measuring the output gives the
gain of everything downstream of the bridge, without needing a pressure standard
or a second instrument.

Reduce by least squares, not by dividing each row. A fixed error in the zero
reference is a large fraction of a small step and a small fraction of a large
one, so per-point ratios show a spread that looks like nonlinearity and is not.
The fit puts that error in the intercept where it belongs.

Edit MEASUREMENTS with your own data and run:

    python3 fit_gain.py

Stdlib only.
"""

# --- transducer, from its calibration certificate ----------------------------
SENSITIVITY_MV_PER_PSI = 0.203      # CTL-312-500A S/N 8779-12-195 at 10.0 VDC
FULL_SCALE_PSI = 500.0
EXCITATION_V = 10.0

# --- (balance voltage in mV, measured mean output in mV) ---------------------
# First row is the baseline; the rest are steps away from it. Record the balance
# value the GUI actually accepted, not the one you typed. The field is quantized
# (12-bit over +/-10 mV = 2.4414 uV steps) so it will not land on round numbers.
MEASUREMENTS = [
    (-5.2441,  -0.16),
    (-4.9805,  16.54),
    (-4.7363,  32.23),
    (-4.2383,  64.05),
    (-5.7324, -31.62),
    (-6.2305, -63.38),
]


def linear_fit(xs, ys):
    """Least squares y = m*x + c. Returns (m, c, r_squared)."""
    n = len(xs)
    if n < 2:
        raise ValueError("need at least two points")
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    sxx = sum((x - mean_x) ** 2 for x in xs)
    sxy = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys))
    if sxx == 0:
        raise ValueError("all balance values identical")
    m = sxy / sxx
    c = mean_y - m * mean_x
    ss_res = sum((y - (m * x + c)) ** 2 for x, y in zip(xs, ys))
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    return m, c, (1 - ss_res / ss_tot if ss_tot else float("nan"))


def main():
    base_balance, base_output = MEASUREMENTS[0]
    d_balance = [b - base_balance for b, _ in MEASUREMENTS]
    d_output = [o - base_output for _, o in MEASUREMENTS]

    print("PER-POINT RATIOS  (shown to make the point that they mislead)")
    ratios = []
    for db, do in zip(d_balance, d_output):
        if db == 0:
            continue
        ratios.append(do / db)
        print(f"  {db:+8.4f} mV in  ->  {do:+8.2f} mV out   G = {do / db:6.2f}")
    spread = (max(ratios) - min(ratios)) / (sum(ratios) / len(ratios)) * 100
    print(f"  spread {min(ratios):.2f} to {max(ratios):.2f}  ({spread:.1f}%)")

    gain, offset, r2 = linear_fit(d_balance, d_output)
    print(f"\nLEAST-SQUARES FIT")
    print(f"  G       = {gain:.3f}")
    print(f"  offset  = {offset:+.3f} mV   (baseline error, harmless once fitted)")
    print(f"  R^2     = {r2:.6f}")

    print(f"\nRESIDUALS")
    worst = 0.0
    for db, do in zip(d_balance, d_output):
        fit = gain * db + offset
        residual = do - fit
        worst = max(worst, abs(residual))
        print(f"  {db:+8.4f}  measured {do:+8.2f}  fit {fit:+8.2f}  "
              f"residual {residual:+7.3f} mV")
    print(f"  largest residual {worst:.3f} mV")

    # Sanity checks that have caught real mistakes.
    if r2 < 0.999:
        print("  !! R^2 below 0.999 — suspect a transcription error or a "
              "genuinely nonlinear stage")
    if abs(offset) > 0.05 * max(abs(v) for v in d_output):
        print("  !! large intercept — the baseline reading may have drifted "
              "between the first row and the rest")
    if spread > 5:
        print("  !! per-point ratios spread more than 5% — if the fit is still "
              "clean this is baseline error, not nonlinearity")

    slope = gain * SENSITIVITY_MV_PER_PSI
    print(f"\nCALIBRATION")
    print(f"  transducer sensitivity   {SENSITIVITY_MV_PER_PSI:.3f} mV/PSI")
    print(f"  system gain              {gain:.2f}")
    print(f"  slope at the readout     {slope:.2f} mV/PSI")
    print(f"  P = (V_out / {slope:.3f} mV/PSI) + P_at_balance")

    implied_fso = SENSITIVITY_MV_PER_PSI * FULL_SCALE_PSI
    print(f"\n  implied full-scale output {implied_fso:.1f} mV "
          f"({implied_fso / 100.0 - 1:+.1%} vs the 100 mV nominal)")
    print(f"  excitation {EXCITATION_V:.1f} V — the sensitivity above is only "
          f"valid at this value")


if __name__ == "__main__":
    main()
