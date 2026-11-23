# RPL OF0 vs MRHOF — Contiki-NG

Compare **OF0** and **MRHOF** using RPL Lite on **Cooja** and the **FIT IoT-LAB** testbed.

## Experiments

- **Cooja:** 15 nodes (1 root, 14 UDP clients); Line, Grid, and Random topologies; 5 labeled runs per topology/OF; 300-second analysis window.
- **FIT IoT-LAB:** 15 M3 nodes at Grenoble (root `m3-207`, clients `m3-208`–`m3-221`); tests with both OF0 and MRHOF. Hardware experiment logs are kept separately.
- **Metrics:** packet delivery ratio (PDR), packet delay, hop count, and preferred-parent changes.

## Cooja results

Means across 5 labeled runs per case:

| Topology | OF | PDR (%) | Delay (ms) | Hops* | Parent changes |
|---|---|---:|---:|---:|---:|
| Line | OF0 | 99.817 | 100.383 | 3.738 | 5.4 |
| Line | MRHOF | 100.000 | 99.511 | 3.733 | 0.0 |
| Grid | OF0 | 99.942 | 81.845 | 3.086 | 3.8 |
| Grid | MRHOF | 99.943 | 81.028 | 3.084 | 0.0 |
| Random | OF0 | 99.941 | 94.954 | 3.497 | 5.4 |
| Random | MRHOF | 100.000 | 94.467 | 3.477 | 0.0 |

**Observation:** Both achieved high PDR; MRHOF had fewer parent changes in these Cooja runs. Delay and hop-count differences were small.

## Repository layout

- `cooja/{OF0,MRHOF}/` — simulation source and OF configuration
- `cooja/topology/` — `.csc` topology/seed files
- `fit-iotlab/{OF0,MRHOF}/` — firmware source for M3 nodes
- `logs/cooja/` and `logs/fit-iotlab/` — raw logs from each environment
- `node-positions/` — FIT IoT-LAB node coordinates
- `scripts/analyze_logs.py` — **Cooja** log analyzer
- `results/cooja_runs.csv` — metrics for individual Cooja runs
- `results/cooja_summary.csv` — aggregated **Cooja-only** metrics

## Reproduce Cooja analysis

```bash
python3 scripts/analyze_logs.py --logs logs/cooja --out results --window-seconds 300
```

**Notes:** Hop count is estimated from RPL logs. Parent changes exclude initial parent selection. CSV results cover Cooja only; FIT IoT-LAB results are stored separately.
