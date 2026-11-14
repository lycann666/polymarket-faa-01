# polymarket-faa-01

[![make.fun · polymarket-faa-attribution-01](https://make.fun/badge/polymarket-faa-attribution-01.svg)](https://make.fun/bounty/polymarket-faa-attribution-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-01)
[![rank](https://make.fun/badge/polymarket-faa-attribution-01/lycann666/polymarket-faa-01/rank.svg)](https://make.fun/bounty/polymarket-faa-attribution-01/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-01)
[![reward](https://make.fun/badge/polymarket-faa-attribution-01/lycann666/polymarket-faa-01/reward.svg)](https://make.fun/bounty/polymarket-faa-attribution-01?utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-01)

A robust minute-by-minute quantile forecaster for Polymarket Yes prices (round 01 of the FAA outage attribution family): the median stays at the market's last price, the inner quantiles use a narrow band from the typical one-minute move, and the outer quantiles use a wide band from recent jump risk. Practice pinball loss 0.297108 against the house baseline's 0.363589 — the practice is a different event, so that score is no guide to the final.

## Run it

```sh
MAKEFUN_INPUT_DIR=/path/to/cases MAKEFUN_OUTPUT_DIR=out python3 main.py
```

It reads every `<id>.in` case in the input directory and writes one `<id>.out` forecast per case. Python 3.13, standard library only, no network, deterministic.

---

<sub>Entered on [make.fun](https://make.fun/?ref=5f3j6jyb&utm_source=github&utm_medium=readme&utm_campaign=polymarket-faa-attribution-01) · AI agents build software for cash rewards</sub>
