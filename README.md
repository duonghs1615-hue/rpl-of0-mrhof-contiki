# Evaluation of RPL Objective Functions in Contiki-NG

This repository compares **Objective Function Zero (OF0)** and **Minimum Rank with Hysteresis Objective Function (MRHOF)** in IPv6 Routing Protocol for Low-Power and Lossy Networks (RPL). It contains Contiki-NG applications, Cooja simulation configurations, raw logs, a Python analysis script, and supplementary FIT IoT-LAB experiment materials.

## Experimental setup

| Parameter | Cooja configuration |
|---|---|
| Operating system / simulator | Contiki-NG / Cooja |
| RPL implementation | RPL Lite |
| Objective functions | OF0 (OCP 0), MRHOF (OCP 1) |
| Topologies | Line, Grid, Random |
| Network size | 15 motes: 1 RPL root and 14 UDP clients |
| Radio model | Unit Disk Graph Medium (UDGM) |
| Transmission range / interference range | 50 / 100 (Cooja distance units) |
| Radio TX / RX success ratios | 1.0 / 1.0 in the simulation configuration |
| MAC layer / channel | CSMA / IEEE 802.15.4 channel 26 |
| UDP sending interval | Approximately 10 seconds, with jitter, after routing becomes available |
| Seeds recorded in `.csc` files | 123456, 101, 202, 303, 404 |
| Analysis window | 0 ≤ simulated time < 300 seconds (five minutes) |
| Number of Cooja logs included | 3 topologies × 2 objective functions × 5 nominal seeds = 30 |

Mote positions are **fixed within each saved topology**; changing the Cooja random seed changes the simulation's pseudorandom sequence, not the saved coordinates. The OF0/MRHOF comparison uses the same saved topology for corresponding seeds.

**Seed provenance limitation:** `.csc` files explicitly contain the seeds listed above, and logs are named accordingly; the text logs do not independently record the simulation seed. Hence, filename-to-seed correspondence depends on the experimental recording process, especially for the original `123456` runs.

## Repository structure

```text
rpl-of0-mrhof-contiki/
├── README.md
├── cooja/
│   ├── OF0/                   # OF0 application and project configuration
│   ├── MRHOF/                 # MRHOF application and project configuration
│   └── topology/              # 15 saved .csc files (3 topologies × 5 seeds)
├── fit-iotlab/
│   ├── OF0/                   # M3 firmware source and configuration
│   └── MRHOF/
├── logs/
│   ├── cooja/
│   │   ├── OF0/               # 15 Cooja log files
│   │   └── MRHOF/             # 15 Cooja log files
│   └── fit-iotlab/            # Physical testbed captures and firmware artifacts
├── node-positions/           # FIT IoT-LAB node-position metadata
├── scripts/
│   └── analyze_logs.py
├── results/
│   ├── cooja_runs.csv
│   └── cooja_summary.csv
└── REFERENCES/               # Supporting project materials
```

## Cooja reproduction steps

1. Install Contiki-NG and its prerequisites; initialize Git submodules. The provided `.csc` files refer to the default Contiki-NG example directory via `[CONTIKI_DIR]/examples/rpl-udp/`.
2. Copy the chosen objective function's **four files** (`Makefile`, `project-conf.h`, `udp-client.c`, `udp-server.c`) from `cooja/OF0/` or `cooja/MRHOF/` into `<contiki-ng>/examples/rpl-udp/`. **Back up any existing files in that example directory first.**
3. Launch Cooja, for example:

   ```bash
   cd ~/contiki-ng/tools/cooja
   ./gradlew run
   ```

4. Open a file under `cooja/topology/` (for example `grid-seed101.csc`), and **compile both Cooja mote types** (UDP server and UDP client) with the selected `project-conf.h`. Do not reuse stale firmware built for the other objective function.
5. Check the node logs for `OCP 0` when evaluating OF0 or `OCP 1` for MRHOF. Run slightly beyond 300 simulated seconds to capture any deliveries just beyond the analysis boundary, and save the complete Cooja log with the corresponding topology, objective-function, and seed in its filename.
6. Repeat for each saved topology/seed; switch `project-conf.h` and rebuild both mote types when changing objective function.

**Important:** Merely opening the same `.csc` file does **not** select OF0 or MRHOF. The compiled firmware determines the objective function. The `.csc` source references point to the Contiki-NG example directory, rather than the copies stored in this repository.

## Log analysis

Run the analyzer from the repository root:

```bash
python3 scripts/analyze_logs.py \
  --logs logs/cooja \
  --out results \
  --window-seconds 300
```

Outputs:

- `results/cooja_runs.csv`: measurements for each input log, with diagnostics and checks.
- `results/cooja_summary.csv`: mean and sample standard deviation across five named runs per topology and objective function.

### Metric definitions

- **Uplink PDR (%):** 100 × (uniquely matched UDP requests received by the root within 0–300 s) / (UDP requests sent by clients within the window). Duplicate or unmatched root-reception log entries do not improve the numerator. This is **not** round-trip response delivery probability.
- **Uplink delay (ms):** timestamp at the root's `Received request` log minus the matched client's `Sending request` timestamp. **It is not RTT.** Only successful, matched requests are included in its mean.
- **Hop count\*:** number of RPL `going up` forwarding/reception events associated with a delivered UDP request; the analyzer checks for a matching root reception. This is a **log-derived estimate**, not an independent packet-header hop count. Some runs contain repeated forwarding events and are flagged in `cooja_runs.csv`.
- **Preferred parent changes:** number of parent-switch log events excluding the first selection (`NULL → parent`) when a node joins the DAG.

Some messages sent immediately before the 300-second boundary are received after it; these are excluded from in-window PDR and flagged as late deliveries. Raw reception counts can also include duplicates; always compare `matched_requests` and the CSV notes rather than treating every log line as a new delivered packet.

## Results: Cooja (five named runs per topology / objective function)

| Topology | Objective function | Runs | PDR (%) | Mean uplink delay (ms) | Mean hop count* | Mean parent changes |
|---|---|---:|---:|---:|---:|---:|
| Line | OF0 | 5 | 99.817 | 100.383 | 3.738 | 5.400 |
| Line | MRHOF | 5 | 100.000 | 99.511 | 3.733 | 0.000 |
| Grid | OF0 | 5 | 99.942 | 81.845 | 3.086 | 3.800 |
| Grid | MRHOF | 5 | 99.943 | 81.028 | 3.084 | 0.000 |
| Random | OF0 | 5 | 99.941 | 94.954 | 3.497 | 5.400 |
| Random | MRHOF | 5 | 100.000 | 94.467 | 3.477 | 0.000 |

\*Hop count is estimated from the application-associated RPL log events as described above. Averages come from the supplied `analyze_logs.py` with exactly 30 selected Cooja logs; the redundant `logs/cooja/OF0/log grid.log` copy is **excluded**. Each group mean gives equal weight to each run.

### Observations and limitations

- Both objective functions reached very high uplink PDR under these simulation settings.
- MRHOF showed **zero preferred-parent changes after initial parent selection** across these recorded runs, while OF0 showed some changes. This finding is specific to these static topologies and radio settings.
- Differences in mean uplink delay and estimated hop count were relatively small. These results alone do not establish that either objective function is universally superior, or statistically significantly faster.
- The UDGM TX/RX success ratios are both 1.0; this comparatively idealized radio configuration limits how confidently the results can be generalized to lossy or mobile networks.
- Saved mote positions are fixed across seeds within a topology, and seeded pseudorandomness may affect radio/application timing. The logs do not independently embed their seed values.
- A few log runs include duplicate or repeated forwarding events. These are explicitly reported in the per-run CSV notes and should be considered before interpreting tiny hop-count differences.

## Supplementary FIT IoT-LAB materials

The repository also contains source code, experiment logs, and node-position metadata for a Grenoble FIT IoT-LAB experiment using 15 M3 nodes (`m3-207` as root and `m3-208` through `m3-221` as clients), as documented in the original project materials. These files are **separate** from the Cooja 30-run summary above; FIT IoT-LAB measurements are not included in `cooja_runs.csv` or `cooja_summary.csv`.

The original M3 build commands are:

```bash
ARCH_PATH=../../../arch make TARGET=iotlab BOARD=m3 savetarget
ARCH_PATH=../../../arch make udp-server
ARCH_PATH=../../../arch make udp-client
```

A previously used log-collection command is:

```bash
timeout 300 serial_aggregator -i <experiment_id> | tee <log_file>
```

The FIT IoT-LAB section is supplementary; comparisons from the simulated Cooja dataset should not be presented as measured physical-radio results.
