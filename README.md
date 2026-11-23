# RPL OF0 vs MRHOF (Contiki-NG / Cooja)

Compare **OF0** and **MRHOF** on **Line, Grid, Random** topologies using 15 nodes (1 root, 14 clients), RPL Lite and CSMA. Each run is analyzed over **300 simulated seconds**.

## Results

Averages from 30 labeled logs (5 runs per topology and objective function):

| Topology | OF | PDR (%) | Delay (ms) | Hops* | Parent changes |
|---|---|---:|---:|---:|---:|
| Line | OF0 | 99.817 | 100.383 | 3.738 | 5.4 |
| Line | MRHOF | 100.000 | 99.511 | 3.733 | 0.0 |
| Grid | OF0 | 99.942 | 81.845 | 3.086 | 3.8 |
| Grid | MRHOF | 99.943 | 81.028 | 3.084 | 0.0 |
| Random | OF0 | 99.941 | 94.954 | 3.497 | 5.4 |
| Random | MRHOF | 100.000 | 94.467 | 3.477 | 0.0 |

**Finding:** Both achieve high PDR. MRHOF shows fewer parent changes in these runs; delay and hop-count differences are small.

## Repository

- `cooja/OF0/`, `cooja/MRHOF/`: source and configuration
- `cooja/topology/`: Cooja simulation files (`.csc`)
- `logs/cooja/`: simulation logs
- `scripts/analyze_logs.py`: analysis script
- `results/`: per-run and summary CSV files

## Reproduce

1. Copy the chosen OF's source/configuration to `contiki-ng/examples/rpl-udp/`.
2. Open a `.csc` in Cooja, recompile both mote types, and check the log for **OCP 0** (OF0) or **OCP 1** (MRHOF).
3. Run past 300 s, save the log, and analyze from the repository root:

```bash
python3 scripts/analyze_logs.py --logs logs/cooja --out results --window-seconds 300
```

*Hops are estimated from RPL log events. Parent changes exclude initial parent selection. Node positions remain fixed across seeds. The six baseline logs are labeled `123456`, but the seed cannot be independently verified from the logs alone.*
