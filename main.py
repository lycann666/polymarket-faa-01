"""Quantile forecaster for Polymarket Yes prices, 4 hours ahead.

Reads each case in $MAKEFUN_INPUT_DIR (else /input) and writes one forecast
file per case to $MAKEFUN_OUTPUT_DIR (else /output): five quantiles
(5/25/50/75/95%) for every market at each of the 240 minutes after the
checkpoint. Python 3.13, standard library only, no network, deterministic.

How it forecasts (each market independently):
- The median is the price at the checkpoint. A prediction-market price is a
  martingale in expectation, so the last price is the honest centre; any
  drift estimated from the recent tape is noise, and adding it made the
  practice score worse, so none is used.
- The 25%/75% band comes from the TYPICAL one-minute move: the median
  absolute change over the last 720 minutes, scaled by 1.4826 (the normal
  conversion), floored at 0.001 and capped at 0.005. Prices sit still most
  minutes, so the typical move is small, and the median ignores rare jumps.
- The 5%/95% band comes from the JUMP risk: the root-mean-square of the
  one-minute changes over the last 240 minutes, each winsorized at +/-0.01,
  floored at 0.001 and capped at 0.01. This covers occasional jumps without
  widening the inner band on quiet minutes.
- Both bands widen with sqrt(horizon), the random-walk scaling. Every
  quantile is clamped to [0, 1] and rounded to 6 decimals.

Practice (6 cases, NVIDIA event): pinball loss 0.297108, against the house
baseline's 0.363589; it beats the baseline on every case. The practice is a
different event from the final, so that score is no guide to the final.
"""

import json
import math
import os
import statistics

INPUT_DIR = os.environ.get("MAKEFUN_INPUT_DIR", "/input")
OUTPUT_DIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")

LEVELS = [0.05, 0.25, 0.5, 0.75, 0.95]
Z = {0.05: -1.644854, 0.25: -0.674490, 0.5: 0.0, 0.75: 0.674490, 0.95: 1.644854}

TYPICAL_WINDOW = 720      # minutes behind the checkpoint for the typical move
TYPICAL_FLOOR = 0.001
TYPICAL_CAP = 0.005
JUMP_WINDOW = 240         # minutes behind the checkpoint for the jump risk
JUMP_WINSOR = 0.01
JUMP_FLOOR = 0.001
JUMP_CAP = 0.01


def _q6(value):
    """Clamp to [0, 1], round to 6 decimals (never -0)."""
    return round(min(1.0, max(0.0, value)) * 1e6) / 1e6 + 0.0


def _typical_move(changes):
    """Scaled median absolute one-minute change (robust to jumps)."""
    recent = changes[-TYPICAL_WINDOW:]
    if not recent:
        return TYPICAL_FLOOR
    med = statistics.median(abs(c) for c in recent)
    return min(TYPICAL_CAP, max(TYPICAL_FLOOR, 1.4826 * med))


def _jump_risk(changes):
    """Winsorized RMS of recent one-minute changes."""
    recent = changes[-JUMP_WINDOW:]
    if not recent:
        return JUMP_FLOOR
    clipped = [max(-JUMP_WINSOR, min(JUMP_WINSOR, c)) for c in recent]
    rms = math.sqrt(sum(c * c for c in clipped) / len(clipped))
    return min(JUMP_CAP, max(JUMP_FLOOR, rms))


def forecast_market(prices, horizon):
    """240 rows of five quantiles for one market."""
    clean = [p for p in prices if math.isfinite(p)]
    centre = clean[-1] if clean else 0.5
    changes = [b - a for a, b in zip(clean, clean[1:])]
    inner = _typical_move(changes)
    outer = _jump_risk(changes)
    rows = []
    for h in range(1, horizon + 1):
        root = math.sqrt(h)
        rows.append([
            _q6(centre + Z[0.05] * outer * root),
            _q6(centre + Z[0.25] * inner * root),
            _q6(centre),
            _q6(centre + Z[0.75] * inner * root),
            _q6(centre + Z[0.95] * outer * root),
        ])
    return rows


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    names = sorted(f for f in os.listdir(INPUT_DIR) if f.endswith(".in"))
    for name in names:
        case_id = name[: -len(".in")]
        with open(os.path.join(INPUT_DIR, name), "r", encoding="utf-8") as f:
            case = json.load(f)
        if case["quantiles"] != LEVELS:
            raise ValueError(
                "%s asks for quantiles %s, not %s" % (name, case["quantiles"], LEVELS)
            )
        forecasts = [
            {"id": m["id"], "q": forecast_market(m["prices"], case["horizon_minutes"])}
            for m in case["markets"]
        ]
        with open(os.path.join(OUTPUT_DIR, case_id + ".out"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"forecasts": forecasts}, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
